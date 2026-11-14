#!/usr/bin/env python3
"""Exercise installed hooks against real staged bytes, commits and local remotes."""

import gzip
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest import mock

import state_guard as guard

SCRIPT = Path(guard.__file__).resolve()


class StateGuardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='state-guard-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.repo, self.state, self.remote = [self.base / name for name in ('product', 'state', 'remote.git')]
        self.list = self.base / 'identifiers.tsv'
        self.slug, self.host, self.private = ['invented-' + uuid.uuid4().hex for _ in range(3)]
        self.list.write_text('private-slug\t' + self.slug + '\ntailnet-host\t' + self.host +
                             '\nprivate-repo\tre:' + self.private + r'\d+' + '\n')
        self.env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        self.env.update(GIT_AUTHOR_NAME='Fixture', GIT_COMMITTER_NAME='Fixture',
                        GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_EMAIL='fixture@example.invalid',
                        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_COUNT='2',
                        GIT_CONFIG_KEY_0='user.email', GIT_CONFIG_VALUE_0='fixture@example.invalid',
                        GIT_CONFIG_KEY_1='commit.gpgsign', GIT_CONFIG_VALUE_1='false',
                        KC_DEV2_IDENTIFIERS=str(self.list), PYTHONDONTWRITEBYTECODE='1')
        self.run_command(['git', 'init', '-q', '-b', 'main', self.repo])
        self.run_command(['git', 'init', '-q', '--bare', self.remote])
        self.git(self.repo, 'remote', 'add', 'origin', self.remote)
        (self.repo / 'seed').write_text('public\n')
        self.git(self.repo, 'add', 'seed')
        self.git(self.repo, 'commit', '-qm', 'test: seed')
        self.git(self.repo, 'worktree', 'add', '--detach', self.state)
        self.git(self.state, 'checkout', '--orphan', 'spacedock-state/test')
        self.git(self.state, 'rm', '-rf', '.')
        (self.state / 'seed').write_text('public state\n')
        self.commit('seed')
        self.git(self.state, 'push', 'origin', 'spacedock-state/test')

    def run_command(self, args, expected=0, data=None, env=None):
        result = subprocess.run(list(map(str, args)), capture_output=True, text=True, input=data,
                                env=env or self.env, timeout=30)
        if expected is not None:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def git(self, root, *args, expected=0, data=None):
        return self.run_command(['git', '-C', root, *args], expected, data)

    def install(self, *extra, expected=0):
        self.git(self.repo, 'config', 'extensions.worktreeConfig', 'true')
        return self.run_command([sys.executable, '-B', SCRIPT, 'install', self.state, *extra], expected)

    def check(self, expected=0, env=None):
        return self.run_command([sys.executable, '-B', SCRIPT, 'check', self.state], expected, env=env)

    def commit(self, name, expected=0):
        self.git(self.state, 'add', '--', name)
        return self.git(self.state, 'commit', '-qm', 'test: state', expected=expected)

    def assert_private_output_absent(self, output):
        for value in (self.slug, self.host, self.private, str(Path.home()), 'fixture@example.invalid'):
            self.assertNotIn(value, output)

    def test_real_commit_refusals_keep_staged_bytes_and_clean_push_passes(self):
        self.install('--refuse', 'private-slug,tailnet-host,private-repo')
        self.assertIn('guarded (', self.check().stdout)
        for name, data, kind in (('slug.txt', self.slug, 'private-slug'), ('host.txt', self.host, 'tailnet-host'),
                                 ('regex.txt', self.private + '42', 'private-repo')):
            (self.state / name).write_text(data)
            refused = self.commit(name, expected=1)
            self.assertIn(f'"{name}" adds a {kind} identifier', refused.stderr)
            self.assert_private_output_absent(refused.stderr)
            self.assertEqual(self.git(self.state, 'show', ':' + name).stdout, data)
            (self.state / name).write_text('public\n')
            self.commit(name)
        self.git(self.state, 'push', 'origin', 'spacedock-state/test')

    def test_push_scans_every_commit_even_after_deletion(self):
        (self.state / 'transient.txt').write_text(self.host + '\n' + self.slug)
        self.commit('transient.txt')
        leak = self.git(self.state, 'rev-parse', 'HEAD').stdout.strip()
        (self.state / 'transient.txt').write_text('public')
        self.commit('transient.txt')
        before = self.git(self.state, 'ls-remote', 'origin').stdout
        self.install('--refuse', 'tailnet-host,private-slug')
        result = self.git(self.state, 'push', 'origin', 'spacedock-state/test', expected=1)
        self.assertIn(leak[:12], result.stderr)
        self.assertIn('transient.txt', result.stderr)
        self.assertIn('tailnet-host', result.stderr)
        self.assertIn('private-slug', result.stderr)
        self.assert_private_output_absent(result.stderr)
        self.assertEqual(before, self.git(self.state, 'ls-remote', 'origin').stdout)

    def test_gzip_and_binary_blobs_refuse_and_file_names_are_safe(self):
        self.install('--refuse', 'private-slug,tailnet-host')
        for name, content in (('evidence.gz', gzip.compress(self.host.encode())),
                              ('nested.gz', gzip.compress(gzip.compress(self.host.encode()))),
                              ('binary.bin', b'\0' + self.slug.encode())):
            path = self.state / name
            path.write_bytes(content)
            result = self.commit(name, expected=1)
            self.assertIn(name, result.stderr)
            self.assert_private_output_absent(result.stderr)
            self.git(self.state, 'reset', '--', name)
            path.unlink()
        path = self.state / (self.slug + '.txt')
        path.write_text(self.host)
        result = self.commit(path.name, expected=1)
        self.assert_private_output_absent(result.stderr)
        self.assertIn('[private-slug].txt', result.stderr)

    def test_warn_then_refuse_home_and_email_and_do_not_scan_product_worktree(self):
        shared = Path(self.git(self.repo, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks').stdout.strip())
        shared.mkdir(exist_ok=True)
        prior = shared / 'pre-commit'
        prior.write_text('#!/bin/sh\nprintf shared-hook-ran >&2\n')
        prior.chmod(0o755)
        self.install()
        (self.state / 'home.txt').write_text(str(Path.home()) + '/public\nfixture@example.invalid\n')
        warned = self.commit('home.txt')
        self.assertIn('warning;', warned.stderr)
        self.assertIn('shared-hook-ran', warned.stderr)
        self.assertIn('home identifier', warned.stderr)
        self.assertIn('email identifier', warned.stderr)
        self.assert_private_output_absent(warned.stderr)
        self.install('--refuse', 'home,email')
        (self.state / 'home.txt').write_text(str(Path.home()) + '/another\nfixture@example.invalid added\n')
        self.commit('home.txt', expected=1)
        (self.repo / 'private.txt').write_text(self.slug)
        self.git(self.repo, 'add', 'private.txt')
        result = self.git(self.repo, 'commit', '-qm', 'test: product')
        self.assertNotIn('state guard:', result.stderr)
        self.assertEqual(self.git(self.repo, 'config', '--get', 'core.hooksPath', expected=1).stdout, '')

    def test_missing_list_still_checks_derived_classes_and_check_detects_drift(self):
        self.assertIn('unguarded:', self.check(expected=1).stdout)
        self.install('--refuse', 'home')
        self.list.unlink()
        self.assertIn('partial: identifier list absent', self.check(expected=1).stdout)
        (self.state / 'derived.txt').write_text(str(Path.home()) + '/public')
        self.assertIn('home identifier', self.commit('derived.txt', expected=1).stderr)
        script = Path(self.git(self.state, 'config', '--get', 'core.hooksPath').stdout.strip()) / 'state_guard.py'
        script.write_text(script.read_text() + '\n')
        self.assertIn('stale: installed copy', self.check(expected=1).stdout)

    def test_rename_does_not_recheck_old_lines_and_added_plus_lines_are_scanned(self):
        (self.state / 'old.txt').write_text(self.slug + '\npublic\n')
        self.commit('old.txt')
        self.install('--refuse', 'private-slug,tailnet-host')
        self.git(self.state, 'mv', 'old.txt', 'archive.txt')
        self.commit('archive.txt')
        with (self.state / 'archive.txt').open('a') as output:
            output.write('+++' + self.host + '\n')
        self.assertIn('tailnet-host identifier', self.commit('archive.txt', expected=1).stderr)

    def test_installer_refuses_repository_list_and_unenabled_worktree_config(self):
        unenabled = self.run_command([sys.executable, '-B', SCRIPT, 'install', self.state], expected=2)
        self.assertIn('extensions.worktreeConfig is off', unenabled.stderr)
        inside = self.repo / 'list.tsv'
        inside.write_text(self.list.read_text())
        env = {**self.env, 'KC_DEV2_IDENTIFIERS': str(inside)}
        result = self.run_command([sys.executable, '-B', SCRIPT, 'install', self.state], expected=2, env=env)
        self.assertIn('outside every git repository', result.stderr)
        self.assert_private_output_absent(result.stderr)

    def test_shared_install_preserves_hooks_and_skips_nonstate_branch(self):
        hooks = Path(self.git(self.repo, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks').stdout.strip())
        hooks.mkdir(exist_ok=True)
        previous = hooks / 'pre-push'
        previous.write_text('#!/bin/sh\ncat > "' + str(self.base / 'shared-input') + '"\n')
        previous.chmod(0o755)
        self.run_command([sys.executable, '-B', SCRIPT, 'install', self.state,
                          '--shared', '--refuse', 'private-slug'])
        self.check()
        self.git(self.state, 'push', 'origin', 'spacedock-state/test')
        (self.repo / 'unchecked.txt').write_text(self.slug)
        self.git(self.repo, 'add', 'unchecked.txt')
        self.git(self.repo, 'commit', '-qm', 'test: product')
        (self.state / 'refused.txt').write_text(self.slug)
        self.commit('refused.txt', expected=1)
        self.assertTrue((self.base / 'shared-input').exists())


class HomeRewriteTests(unittest.TestCase):
    def test_path_boundaries_preserve_other_homes_and_line_endings(self):
        with mock.patch.object(guard.Path, 'home', return_value=Path('/invented/home')):
            self.assertEqual(guard.rewrite_home('cwd: /invented/home/path\r\n"/invented/home"\n'),
                             'cwd: ~/path\r\n"~"\n')
            for text in ('/invented/homer/path', '/another/invented/home/path', 'x/invented/home/path'):
                self.assertEqual(guard.rewrite_home(text), text)


if __name__ == '__main__':
    unittest.main()
