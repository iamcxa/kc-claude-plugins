#!/usr/bin/env python3
"""Send one Standard-Webhooks-signed synthetic relay capacity event.

usage: send_event.py URL [--tamper] [--event bound-ceiling-near|bound-ceiling-full]
The secret is read from OPS_WEBHOOK_SECRET and never printed. --tamper changes one
byte of the body after signing.
"""
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid


def sign(secret, msg_id, timestamp, body):
    key = base64.b64decode(secret[len("whsec_"):]) if secret.startswith("whsec_") else secret.encode()
    digest = hmac.new(key, msg_id.encode() + b"." + timestamp.encode() + b"." + body, hashlib.sha256).digest()
    return "v1," + base64.b64encode(digest).decode()


def main(argv):
    url = argv[1]
    event = argv[argv.index("--event") + 1] if "--event" in argv else "bound-ceiling-near"
    full = event == "bound-ceiling-full"
    payload = {"v": 1, "event": event, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "day": time.strftime("%Y-%m-%d", time.gmtime()), "count": 50 if full else 40,
               "limit": 50, "limitSource": "default"}
    body = json.dumps(payload, separators=(",", ":")).encode()
    msg_id, ts = "msg_" + uuid.uuid4().hex, str(int(time.time()))
    signature = sign(os.environ["OPS_WEBHOOK_SECRET"], msg_id, ts, body)
    if "--tamper" in argv:
        body = body.replace(b'"count":40', b'"count":41').replace(b'"count":50', b'"count":51')
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "content-type": "application/json", "webhook-id": msg_id,
        "webhook-timestamp": ts, "webhook-signature": signature})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(resp.status, resp.read().decode())
    except urllib.error.HTTPError as err:
        print(err.code, err.read().decode())
    print("webhook-id", msg_id)


if __name__ == "__main__":
    main(sys.argv)
