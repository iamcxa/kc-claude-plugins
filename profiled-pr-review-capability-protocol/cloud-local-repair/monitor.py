"""One monitor core; live adapter dormant and explicitly denied by default."""
import hashlib
import json
import math
import subprocess
import time


class ObservationError(ValueError):
    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


class Clock:
    @property
    def now(self):
        return time.monotonic()

    def advance(self, seconds):
        time.sleep(seconds)


class CommandTransport:
    """Tests inject runner/clock into this same command and timeout path."""
    def __init__(self, runner=None, clock=None, *, allow_live=False):
        if runner is None and not allow_live:
            raise PermissionError('live transport requires separate explicit authority')
        self.runner = runner if runner is not None else subprocess.run
        self.clock = clock if clock is not None else Clock()

    def request(self, args, timeout):
        allowed = {('workspace', 'get'), ('workspace', 'session'), ('workspace', 'archive'),
                   ('session', 'message'), ('session', 'status'), ('session', 'cancel')}
        if tuple(args[:2]) not in allowed or not 0 < timeout <= 10:
            raise ObservationError('command_or_timeout_not_allowed')
        try:
            result = self.runner(['conductor', '--json', *args], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            raise TimeoutError('command response unknown after timeout') from error
        return {'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


class Monitor:
    def __init__(self, transport, root, workspace, session, project, *,
                 submitted_monotonic, deadline_monotonic, expected_prior_sha256):
        if type(transport) is not CommandTransport:
            raise TypeError('explicit CommandTransport required')
        self.transport, self.clock, self.root = transport, transport.clock, root
        self.workspace, self.session, self.project = workspace, session, project
        self.calls, self.steps, self.events = [], {}, {}
        self.deadline = None
        if not all(type(value) in (int, float) and math.isfinite(value) for value in (submitted_monotonic, deadline_monotonic)):
            raise ValueError('finite frozen times required')
        if not 0 < deadline_monotonic - submitted_monotonic <= 300:
            raise ValueError('frozen window must not exceed 300 seconds')
        if not isinstance(expected_prior_sha256, str) or len(expected_prior_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_prior_sha256):
            raise ValueError('frozen prior SHA-256 required')
        self.submitted_monotonic, self.frozen_deadline = submitted_monotonic, deadline_monotonic
        self.baseline = expected_prior_sha256

    def call(self, *args):
        timeout = 10 if self.deadline is None else min(10, self.deadline - self.clock.now - 30)
        record = {'args': args, 'start': self.clock.now, 'timeout': timeout}
        try:
            if timeout <= 0:
                raise ObservationError('deadline')
            try:
                result = self.transport.request(args, timeout)
            except TimeoutError as error:
                raise ObservationError('command_timeout_unknown') from error
            record['raw'] = result
            if result.get('exit') != 0:
                raise ObservationError('command_failed')
            try:
                parsed = json.loads(result['stdout'])
            except (ValueError, KeyError, TypeError) as error:
                raise ObservationError('malformed_json') from error
            if not isinstance(parsed, dict):
                raise ObservationError('invalid_response_shape')
            record['state'] = 'ok'
            return parsed
        except ObservationError as error:
            record.update(state='unknown' if error.kind == 'command_timeout_unknown' else 'error', kind=error.kind)
            raise
        finally:
            record['end'] = self.clock.now
            self.calls.append(record)

    def capture(self, name, operation):
        try:
            value = operation()
            step = {'state': 'ok', 'value': value}
        except (ObservationError, OSError, KeyError, TypeError) as error:
            kind = getattr(error, 'kind', type(error).__name__)
            step = {'state': 'unknown' if kind == 'command_timeout_unknown' else 'error', 'kind': kind}
        self.steps[name] = step
        return step

    def identity(self):
        ws = self.call('workspace', 'get', self.workspace)
        if ws.get('id') != self.workspace or ws.get('projectId') != self.project:
            raise ObservationError('workspace_identity_mismatch')
        page = self.call('workspace', 'session', self.workspace, '--include-archived', '--limit', '100')
        rows = page.get('data')
        if not isinstance(rows, list) or not any(isinstance(row, dict) and row.get('id') == self.session for row in rows):
            raise ObservationError('session_identity_mismatch_or_incomplete')
        return ws

    def pages(self):
        cursor = next(reversed(self.events), None)
        for unused in range(3):
            args = ['session', 'message', self.session, '--limit', '10']
            if cursor:
                args.extend(['--after', cursor])
            page = self.call(*args)
            rows = page.get('data')
            if not isinstance(rows, list) or type(page.get('hasMore')) is not bool:
                raise ObservationError('invalid_page_shape')
            for row in rows:
                if not isinstance(row, dict) or row.get('sessionId') != self.session or not isinstance(row.get('id'), str):
                    raise ObservationError('message_identity_mismatch')
                content = row.get('content')
                if not isinstance(content, dict) or ('rawPayload' in content and not isinstance(content['rawPayload'], dict)):
                    raise ObservationError('invalid_message_shape')
                if row['id'] in self.events:
                    raise ObservationError('cursor_repeated_or_duplicate')
                self.events[row['id']] = row
            if not page['hasMore']:
                return {'complete': True, 'count': len(self.events)}
            if not rows:
                raise ObservationError('empty_incomplete_page')
            cursor = rows[-1]['id']
        raise ObservationError('page_bound_incomplete')

    def terminal(self):
        for row in self.events.values():
            value = row.get('content', {}).get('rawPayload', {})
            if value.get('type') == 'result' and value.get('session_id') == self.session:
                return value
        return None

    def status(self):
        status = self.call('session', 'status', self.session)
        if status.get('sessionId') != self.session or status.get('workspaceId') != self.workspace:
            raise ObservationError('status_identity_mismatch')
        return status

    def canary(self):
        unchanged = hashlib.sha256((self.root / 'prior.json').read_bytes()).hexdigest() == self.baseline
        if not unchanged or (self.root / 'current.json').exists():
            raise ObservationError('canary_changed')
        return {'prior_unchanged': True, 'current_absent': True}

    def cleanup(self):
        self.deadline = None
        # Every operation is independently captured; diagnostics cannot gate archive.
        allowed = self.capture('cancel_identity', self.identity)['state'] == 'ok'
        if allowed:
            self.capture('cancel', lambda: self.call('session', 'cancel', self.session))
        else:
            self.steps['cancel'] = {'state': 'refused', 'kind': 'identity_unverified'}
        self.capture('post_cancel_status', self.status)
        allowed = self.capture('archive_identity', self.identity)['state'] == 'ok'
        if allowed:
            self.capture('archive', lambda: self.call('workspace', 'archive', self.workspace))
        else:
            self.steps['archive'] = {'state': 'refused', 'kind': 'identity_unverified'}
        for index in range(3):
            ws = self.capture('archive_readback_' + str(index), lambda: self.call('workspace', 'get', self.workspace))
            value = ws.get('value', {})
            if value.get('id') == self.workspace and value.get('projectId') == self.project and value.get('state') == 'archived':
                self.steps['archive_observed'] = {'state': 'ok', 'value': value}
                break
            self.clock.advance(1)
        else:
            self.steps['archive_observed'] = {'state': 'unknown', 'kind': 'archive_not_observed'}
        self.capture('final_status', self.status)
        self.capture('final_transcript', self.pages)
        self.capture('final_canary', self.canary)

    def run(self):
        """Observe a synthetic already-submitted turn; no create/message capability."""
        reason = 'incomplete'
        self.deadline = self.frozen_deadline
        try:
            self.canary()
            if self.clock.now >= self.deadline - 35:
                raise ObservationError('deadline_incomplete')
            self.identity()
            previous = None
            while self.clock.now < self.deadline - 35:
                self.pages()
                status = self.status()
                self.canary()
                terminal = self.terminal()
                if terminal and status.get('status') == 'idle':
                    signature = json.dumps(terminal, sort_keys=True)
                    if signature == previous:
                        reason = 'terminal_complete' if terminal.get('subtype') == 'success' and terminal.get('is_error') is False else 'terminal_failed'
                        break
                    previous = signature
                self.clock.advance(5)
            else:
                reason = 'deadline_incomplete'
        except (ObservationError, OSError, KeyError, TypeError) as error:
            reason = getattr(error, 'kind', type(error).__name__)
        finally:
            self.cleanup()
        idle = self.steps['final_status'].get('value', {}).get('status') == 'idle'
        complete = reason == 'terminal_complete' and idle and all(step['state'] == 'ok' for step in self.steps.values())
        result = {'reason': reason, 'exit_code': 0 if complete else 1, 'steps': self.steps, 'calls': self.calls,
                  'events': list(self.events.values()), 'finished_monotonic': self.clock.now,
                  'submitted_monotonic': self.submitted_monotonic, 'frozen_deadline': self.frozen_deadline,
                  'expected_prior_sha256': self.baseline,
                  'remote_deadline_and_descendant_death': 'unverified'}
        (self.root / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        return result['exit_code'], result


if __name__ == '__main__':
    raise SystemExit('Execution refused: import with an explicitly bound transport; no live entrypoint.')
