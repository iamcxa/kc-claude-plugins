"""Account for Python-created scratch directories without altering behavior."""
import json
import os
import sys

def record(event, args):
    if event != 'os.mkdir' or not os.environ.get('SCRATCH_DIRECTORY_LOG'):
        return
    path = os.path.realpath(os.fspath(args[0]))
    if path.startswith('/private/tmp/') and not os.path.exists(path):
        with open(os.environ['SCRATCH_DIRECTORY_LOG'], 'a') as output:
            output.write(json.dumps({'path': path, 'pid': os.getpid()}) + '\n')

sys.addaudithook(record)
