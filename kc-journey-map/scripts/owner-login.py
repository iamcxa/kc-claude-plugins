#!/usr/bin/env python3
"""Owner-only Unix peer channel; no Internet or document access."""
import ctypes
import json
import os
import socket
import signal
import stat
import struct
import sys


def peer_uid(connection):
    if sys.platform.startswith('linux'):
        return struct.unpack('3i', connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))[1]
    if sys.platform == 'darwin' or 'bsd' in sys.platform:
        uid, gid = ctypes.c_uint(), ctypes.c_uint()
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.getpeereid(connection.fileno(), ctypes.byref(uid), ctypes.byref(gid)):
            raise OSError(ctypes.get_errno(), 'peer identity unavailable')
        return uid.value
    raise RuntimeError('unsupported OS peer credentials; local sign-in disabled')


def check_socket(path):
    parent = os.lstat(os.path.dirname(path))
    target = os.lstat(path)
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.geteuid() or parent.st_mode & 0o077:
        raise RuntimeError('socket directory must be owned, real and 0700')
    if not stat.S_ISSOCK(target.st_mode) or target.st_uid != os.geteuid() or target.st_mode & 0o077:
        raise RuntimeError('socket must be owned, real and 0600')


def server(path, owner):
    if owner != os.geteuid():
        raise RuntimeError('service owner mismatch')
    left, right = socket.socketpair()
    try:
        if peer_uid(left) != owner:
            raise RuntimeError('peer identity probe failed')
    finally:
        left.close()
        right.close()
    if os.path.lexists(path):
        raise RuntimeError('socket path exists; verify and remove an old owned socket explicitly')
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    old_umask = os.umask(0o177)
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        listener.bind(path)
        os.chmod(path, 0o600)
        check_socket(path)
        listener.listen(4)
        print(json.dumps({'ready': True}), flush=True)
        while True:
            connection, _ = listener.accept()
            with connection:
                connection.settimeout(10)
                try:
                    if peer_uid(connection) != owner:
                        raise RuntimeError('owner peer denied')
                    raw = connection.makefile('rb').readline(4097)
                    if len(raw) > 4096:
                        raise RuntimeError('request too large')
                    request = json.loads(raw)
                    if request.get('op') not in ('challenge-inspect', 'challenge-approve') or not isinstance(request.get('requestId'), str):
                        raise RuntimeError('unknown owner operation')
                    print(json.dumps({'op': request['op'], 'requestId': request['requestId'], 'peerUid': owner}), flush=True)
                    reply = sys.stdin.readline()
                    if not reply:
                        return
                    connection.sendall(reply.encode())
                except Exception:
                    connection.sendall(b'{"error":"owner request denied"}\n')
    finally:
        listener.close()
        os.umask(old_umask)
        if os.path.lexists(path) and stat.S_ISSOCK(os.lstat(path).st_mode) and os.lstat(path).st_uid == owner:
            os.unlink(path)


def request(path, operation, request_id):
    check_socket(path)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(10)
        connection.connect(path)
        if peer_uid(connection) != os.geteuid():
            raise RuntimeError('server peer denied')
        connection.sendall((json.dumps({'op': operation, 'requestId': request_id}) + '\n').encode())
        result = json.loads(connection.makefile('rb').readline(4097))
        if 'error' in result:
            raise RuntimeError(result['error'])
        return result


if __name__ == '__main__':
    try:
        if len(sys.argv) == 4 and sys.argv[1] == '--serve':
            server(sys.argv[2], int(sys.argv[3]))
        elif len(sys.argv) == 3:
            path, request_id = sys.argv[1:]
            details = request(path, 'challenge-inspect', request_id)
            print('Approve this browser request?')
            print(json.dumps(details, ensure_ascii=False, indent=2))
            if input('Type approve to sign in as this owner: ').strip() != 'approve':
                raise RuntimeError('cancelled')
            print(json.dumps(request(path, 'challenge-approve', request_id)))
        else:
            raise RuntimeError('usage: python3 scripts/owner-login.py /absolute/owned/socket request-id')
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
