---
id: 98jq8h0ek4eekvs39jgdwd6e
title: Make gated profile routes skip inactive stages
status: backlog
source: Carlove Netlify DB local gate incident, 2026-08-22
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
archived: 2026-08-22T07:43:55Z
---

## Problem

kc-dev-flow correctly declares POC and Pilot validation-to-done routes, but the current Spacedock gate lifecycle follows the README's immediate successor and sends an approved POC gate into the Production-only release stage. The existing adopter smoke bypasses the gated path, so it did not detect this contract mismatch.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
