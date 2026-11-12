#!/usr/bin/env python3
"""Exercise evidence restoration and the deletion boundary with real git worktrees."""

import contextlib
import gzip
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import uuid

import scratch


class ScratchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='scratch-test-')
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name).resolve()
        self.env = {**os.environ, 'GIT_AUTHOR_NAME': 'Fixture', 'GIT_COMMITTER_NAME': 'Fixture',
                    'GIT_AUTHOR_EMAIL': 'fixture@example.invalid', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
                    'GIT_CONFIG_COUNT': '2', 'GIT_CONFIG_KEY_0': 'core.hooksPath', 'GIT_CONFIG_VALUE_0': '/dev/null',
                    'GIT_CONFIG_KEY_1': 'commit.gpgsign', 'GIT_CONFIG_VALUE_1': 'false'}
        self.git('init', '-q', '-b', 'main')
        self.git('remote', 'add', 'origin', 'https://example.invalid/fixtures/scratch-' + uuid.uuid4().hex + '.git')
        (self.repo / 'tracked').write_text('original\n')
        self.git('add', 'tracked')
        self.git('commit', '-qm', 'test: original')
        self.folder = self.repo / 'task'
        (self.folder / 'dispatch').mkdir(parents=True)
        self.record = self.folder / 'dispatch/validation-1.md'
        self.record.write_text('# validation-1\n')
        self.root = scratch.claim_root(self.repo, self.folder, 'validation-1')
        self.addCleanup(shutil.rmtree, self.root.parent.parent, True)
        self.evidence = self.folder / 'evidence/validation-1'
        self.evidence.mkdir(parents=True)

    def git(self, *args):
        done = subprocess.run(['git', '-C', str(self.repo), *map(str, args)], capture_output=True,
                              text=True, env=self.env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def close(self, record='validation-1'):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), mock.patch.dict(os.environ, self.env):
            scratch.close(self.folder, record)
        return out.getvalue()

    def test_threshold_restore_and_idempotence(self):
        small, large = b's' * (256 * 1024), b'evidence\n' * 40000
        (self.evidence / 'small.txt').write_bytes(small)
        (self.evidence / 'large.txt').write_bytes(large)
        (self.root / 'scratch.txt').write_text('remove this')
        out = self.close()
        self.assertFalse(self.root.parent.exists())
        self.assertEqual((self.evidence / 'small.txt').read_bytes(), small)
        self.assertFalse((self.evidence / 'large.txt').exists())
        self.assertIn('Scratch removed:', out)
        self.assertIn('Evidence: evidence/validation-1/ (2 files,', out)
        self.git('add', 'task')
        self.git('commit', '-qm', 'test: archived evidence')
        restored = subprocess.run(['git', '-C', str(self.repo), 'show', 'HEAD:task/evidence/validation-1/large.txt.gz'],
                                  capture_output=True, check=True).stdout
        self.assertEqual(gzip.decompress(restored), large)
        sums = (self.evidence / 'SHA256SUMS').read_text()
        self.assertIn(hashlib.sha256(large).hexdigest() + '  large.txt\n', sums)
        log = (self.folder / 'scratch-removed.txt').read_bytes()
        self.assertIn('(absent)', self.close())
        self.assertEqual((self.folder / 'scratch-removed.txt').read_bytes(), log)
        self.assertEqual((self.evidence / 'SHA256SUMS').read_text(), sums)
        with self.assertRaises((EOFError, OSError)):
            gzip.decompress(restored[:-8])

    def test_dirty_registered_worktree_removed_and_external_worktree_survives(self):
        worktree, external = self.root / 'checkout with spaces', self.repo / 'external'
        self.git('worktree', 'add', '--detach', worktree)
        self.git('worktree', 'add', '--detach', external)
        (worktree / 'tracked').write_text('changed')
        subprocess.run(['git', '-C', str(worktree), 'add', 'tracked'], check=True, env=self.env)
        (worktree / 'untracked').write_text('discarded')
        self.close()
        listed = self.git('worktree', 'list', '--porcelain')
        self.assertNotIn(str(worktree), listed)
        self.assertIn(str(external), listed)
        self.assertTrue((external / 'tracked').exists())
        self.assertIn('uncommitted-files=2', (self.folder / 'scratch-removed.txt').read_text())
        self.git('worktree', 'remove', external)

    def test_missing_record_refuses_without_deletion(self):
        sentinel = self.root / 'sentinel'
        sentinel.write_text('keep')
        self.record.unlink()
        with self.assertRaisesRegex(ValueError, 'record missing'):
            self.close()
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_symlink_root_and_parent_leave_sentinel(self):
        sentinel = self.repo / 'sentinel'
        sentinel.mkdir()
        (sentinel / 'keep').write_text('keep')
        shutil.rmtree(self.root)
        self.root.symlink_to(sentinel, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            self.close()
        self.root.unlink()
        self.root.parent.rmdir()
        self.root.parent.symlink_to(sentinel, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            self.close()
        self.root.parent.unlink()
        self.assertEqual((sentinel / 'keep').read_text(), 'keep')

    def test_mismatched_root_and_traversal_refuse(self):
        sentinel = self.root / 'keep'
        sentinel.write_text('keep')
        self.record.write_text('Scratch: /tmp/outside-derived-root\n')
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.close()
        with self.assertRaisesRegex(ValueError, 'invalid dispatch'):
            self.close('../validation-1')
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_evidence_size_limit_preserves_scratch_and_restorable_evidence(self):
        data = os.urandom(1024 * 1024 + 100)
        (self.evidence / 'large.bin').write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'exceeds 1 MiB'):
            self.close()
        self.assertTrue(self.root.is_dir())
        self.assertEqual(gzip.decompress((self.evidence / 'large.bin.gz').read_bytes()), data)
        self.assertFalse((self.folder / 'scratch-removed.txt').exists())

    def test_symlinked_evidence_and_log_refuse_without_deletion(self):
        sentinel = self.repo / 'private'
        sentinel.write_text('never archive this')
        link = self.evidence / 'link'
        link.symlink_to(sentinel)
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            self.close()
        link.unlink()
        (self.folder / 'scratch-removed.txt').symlink_to(sentinel)
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            self.close()
        self.assertTrue(self.root.exists())
        self.assertEqual(sentinel.read_text(), 'never archive this')

    def test_follow_up_uses_parent_dispatch_root(self):
        follow = self.folder / 'dispatch/validation-1-message-2.md'
        follow.write_text('# continuation\n')
        self.assertEqual(scratch.root_for(self.repo, self.folder, follow.stem), self.root)
        self.close(follow.stem)
        self.assertFalse(self.root.exists())
        self.assertFalse((self.folder / 'evidence' / follow.stem).exists())

    def test_cli_returns_nonzero_for_refused_close(self):
        done = subprocess.run([sys.executable, '-B', str(Path(scratch.__file__)), 'close',
                               str(self.folder), 'validation-2'], capture_output=True, text=True)
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertIn('dispatch record missing', done.stderr)
        self.assertTrue(self.root.exists())

    def test_same_basename_repositories_and_clones_keep_foreign_dirty_worktrees(self):
        origin = self.git('remote', 'get-url', 'origin').strip()
        for number, url in enumerate((origin.replace('/fixtures/', '/another-owner/'), origin)):
            with self.subTest(origin=url):
                self.root = scratch.claim_root(self.repo, self.folder, 'validation-1')
                other = self.repo / f'clone-{number}'
                other.mkdir()
                def git(*args):
                    result = subprocess.run(['git', '-C', str(other), *map(str, args)],
                                            capture_output=True, text=True, env=self.env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    return result.stdout
                git('init', '-q', '-b', 'main')
                git('remote', 'add', 'origin', url)
                (other / 'tracked').write_text('original')
                git('add', 'tracked'); git('commit', '-qm', 'test: peer clone')
                folder = other / 'task'
                folder.mkdir()
                peer = scratch.claim_root(other, folder, 'validation-1')
                self.addCleanup(shutil.rmtree, peer.parent.parent, True)
                self.assertNotEqual(self.root, peer)
                checkout = peer / 'checkout'
                git('worktree', 'add', '--detach', checkout)
                (checkout / 'uncommitted').write_text('peer work')
                self.close()
                self.assertEqual((checkout / 'uncommitted').read_text(), 'peer work')
                self.assertIn(str(checkout), git('worktree', 'list', '--porcelain'))
                git('worktree', 'remove', '--force', checkout)

    def test_foreign_or_unowned_root_refuses_notes_reuse_and_close(self):
        notes = self.root / 'scope-notes.md'
        notes.write_text('peer notes')
        marker = self.root / '.owner.json'
        for content in (None, '{"repository":"other","task":"task","record":"validation-1"}'):
            with self.subTest(marker=content):
                marker.unlink(missing_ok=True)
                if content is not None:
                    marker.write_text(content)
                with self.assertRaisesRegex(ValueError, 'ownership'):
                    scratch.claim_root(self.repo, self.folder, 'validation-1')
                with self.assertRaisesRegex(ValueError, 'ownership'):
                    scratch.notes_for(self.repo, self.folder, 'validation-1', 'notes', self.repo)
                with self.assertRaisesRegex(ValueError, 'ownership'):
                    self.close()
                self.assertEqual(notes.read_text(), 'peer notes')
                self.assertFalse((self.evidence / 'SHA256SUMS').exists())

    def test_archive_move_and_linked_worktree_keep_identity(self):
        other_workflow = self.repo / 'another-workflow/task'
        self.assertNotEqual(scratch.root_for(self.repo, other_workflow, 'validation-1'), self.root)
        linked = self.repo / 'linked'
        self.git('worktree', 'add', '--detach', linked)
        self.assertEqual(scratch.root_for(linked, self.folder, 'validation-1'), self.root)
        self.git('worktree', 'remove', linked)
        (self.repo / '_archive').mkdir()
        archived = self.repo / '_archive/task'
        self.folder.rename(archived)
        self.assertEqual(scratch.root_for(self.repo, archived, 'validation-1'), self.root)
        scratch.close(archived, 'validation-1')
        self.assertFalse(self.root.exists())


if __name__ == '__main__':
    unittest.main()
