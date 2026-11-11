#!/usr/bin/env python3
"""Build the fictional `tidepool` repository for one POC arm. Everything here is invented."""
import subprocess
from pathlib import Path

PKG_REPO = "/Users/kent/conductor/workspaces/kc-claude-plugins/colombo"
PKG_SHA = "e8664a72b0f904e5dda3c391d52ab3abaca876b4"
ARMS = {"A": ("flat", "shipped"), "B": ("layered", "shipped"), "C": ("layered", "convention"),
        "D": ("layered2", "convention2"), "E": ("single", "convention2")}

BOOKING = '''"""Bookings: states, deposit and cancellation."""
from dataclasses import dataclass

CANCEL_FREE_HOURS = 36
DEPOSIT_PERCENT = 15
EXEMPT_GROUP = "Harbor Club"
STATES = ("held", "confirmed", "cancelled", "completed")


@dataclass
class Booking:
    customer: str
    price_cents: int
    state: str = "held"
    group: str = ""
    deposit_cents: int = 0


def confirm(booking):
    if booking.state != "held":
        raise ValueError("only a held booking can be confirmed")
    booking.deposit_cents = booking.price_cents * DEPOSIT_PERCENT // 100
    booking.state = "confirmed"
    return booking


def cancel(booking, hours_before_start):
    """Cancel a confirmed booking and return the deposit refunded, in cents."""
    if booking.state != "confirmed":
        raise ValueError("only a confirmed booking can be cancelled")
    booking.state = "cancelled"
    if hours_before_start >= CANCEL_FREE_HOURS or booking.group == EXEMPT_GROUP:
        refund, booking.deposit_cents = booking.deposit_cents, 0
        return refund
    return 0


def complete(booking):
    if booking.state != "confirmed":
        raise ValueError("only a confirmed booking can be completed")
    booking.state = "completed"
    return booking
'''

SLOTS = '''"""Slots: a slot is held for a short time while the customer finishes booking."""
from datetime import timedelta

HOLD_MINUTES = 7


class Slot:
    def __init__(self, start):
        self.start = start
        self.held_until = None
        self.taken = False

    def hold(self, now):
        if self.taken or (self.held_until and now < self.held_until):
            raise ValueError("slot is not free")
        self.held_until = now + timedelta(minutes=HOLD_MINUTES)
        return self.held_until

    def extend(self, now):
        if not self.held_until or now >= self.held_until:
            raise ValueError("no live hold to extend")
        self.held_until = now + timedelta(minutes=HOLD_MINUTES)
        return self.held_until

    def take(self, now):
        if not self.held_until or now >= self.held_until:
            raise ValueError("hold expired")
        self.taken = True
'''

NOTIFY = '''"""Notifications: one reminder email before the appointment."""
from datetime import timedelta

REMINDER_HOURS_BEFORE = 20
CHANNEL = "email"


def reminder_time(start):
    return start - timedelta(hours=REMINDER_HOURS_BEFORE)
'''

TESTS = '''import unittest
from datetime import datetime, timedelta

from tidepool import booking, notify, slots


class BookingRules(unittest.TestCase):
    def confirmed(self, group=""):
        return booking.confirm(booking.Booking("ana", 20000, group=group))

    def test_deposit_is_taken_at_confirmation(self):
        self.assertEqual(self.confirmed().deposit_cents, 3000)

    def test_cancel_outside_window_refunds_deposit(self):
        self.assertEqual(booking.cancel(self.confirmed(), 36), 3000)

    def test_cancel_inside_window_keeps_deposit(self):
        self.assertEqual(booking.cancel(self.confirmed(), 35), 0)

    def test_exempt_group_is_refunded_inside_window(self):
        self.assertEqual(booking.cancel(self.confirmed("Harbor Club"), 1), 3000)


class SlotHold(unittest.TestCase):
    def test_hold_lasts_seven_minutes(self):
        now = datetime(2026, 3, 2, 9, 0)
        self.assertEqual(slots.Slot(now).hold(now), now + timedelta(minutes=7))


class Reminder(unittest.TestCase):
    def test_reminder_goes_twenty_hours_before(self):
        start = datetime(2026, 3, 2, 9, 0)
        self.assertEqual(notify.reminder_time(start), start - timedelta(hours=20))


if __name__ == "__main__":
    unittest.main()
'''

# One sentence per fact; both layouts are built from these so the content is the same.
F = {
    "what": "Tidepool takes appointment bookings for small salons: a customer picks a slot, pays a deposit and gets one reminder.",
    "hold": "A slot is held for 7 minutes while the customer finishes booking; an expired hold frees the slot.",
    "states": "A booking is `held`, then `confirmed`, and ends as `cancelled` or `completed`.",
    "deposit": "Confirming a booking takes a deposit of 15 percent of the price.",
    "cancel": "A customer who cancels 36 hours or more before the appointment gets the deposit back; later than that the shop keeps it.",
    "exempt": "Harbor Club members are exempt: they get the deposit back whenever they cancel.",
    "reminder": "One reminder is sent 20 hours before the appointment.",
    "channel": "Reminders go by email only.",
    "limit": "There is no payment provider yet; the deposit is a number on the booking.",
}

FLAT = f"""# Tidepool architecture

{F['what']} The code is three modules under `tidepool/`.

Booking starts with a slot. {F['hold']} The hold length was settled early (ADR 0001) because
shops complained about slots vanishing mid-form. Once the customer finishes, the booking moves on:
{F['states'].lower()} {F['deposit']} That figure is ADR 0002.

Cancelling is where most of the rules sit. {F['cancel']} {F['exempt']} The owner decided that
in ADR 0003 after a run of complaints from long-standing customers.

After confirmation the customer hears from us once. {F['reminder']} {F['channel']} ADR 0004 has
the reason. {F['limit']}

Tests live in `tests/test_tidepool.py` and run with `python3 -m unittest discover -s tests`.
"""

MAP = """# Tidepool architecture

""" + F["what"] + """ This file is the entry point: it says which document owns each question.
Each document under `docs/architecture/` states what is the case today.

| Question | Document |
| --- | --- |
| How a slot is held, how a booking moves between states, deposit and cancellation | [booking](architecture/booking.md) |
| What the customer is told and when | [notifications](architecture/notifications.md) |

Rulings and their reasons are in `docs/adr/`. Tests run with `python3 -m unittest discover -s tests`.
"""

BOOKING_DOC = f"""# Booking

## Covers

Slot holds, booking states, the deposit and cancellation. Reminders are in [notifications](notifications.md).

## Parties

The customer, and the shop that owns the slot.

## States

{F['states']}

## Rules

- {F['hold']}
- {F['deposit']}
- {F['cancel']}
- {F['exempt']}

## Known limits

- {F['limit']}

## Governing ADRs

- [0001](../adr/0001-a-slot-hold-lasts-seven-minutes.md) slot hold length
- [0002](../adr/0002-the-deposit-is-fifteen-percent.md) deposit size
- [0003](../adr/0003-harbor-club-members-keep-their-refund.md) Harbor Club exemption

## Proof

| Property | Evidence |
| --- | --- |
| Hold length | `test_hold_lasts_seven_minutes` |
| Deposit at confirmation | `test_deposit_is_taken_at_confirmation` |
| Refund outside the window | `test_cancel_outside_window_refunds_deposit` |
| No refund inside the window | `test_cancel_inside_window_keeps_deposit` |
| Harbor Club exemption | `test_exempt_group_is_refunded_inside_window` |
"""

NOTIFY_DOC = f"""# Notifications

## Covers

What the customer is told after booking. Booking rules are in [booking](booking.md).

## Parties

The customer. The shop is not notified.

## States

None of its own; a reminder belongs to a `confirmed` booking.

## Rules

- {F['reminder']}
- {F['channel']}

## Known limits

- A reminder is computed, not sent: there is no mail provider yet.

## Governing ADRs

- [0004](../adr/0004-reminders-go-by-email-only.md) reminder channel

## Proof

| Property | Evidence |
| --- | --- |
| Reminder timing | `test_reminder_goes_twenty_hours_before` |
"""

ADRS = [
    ("0001-a-slot-hold-lasts-seven-minutes", "A slot hold lasts seven minutes", "2026-02-03",
     "Shops reported slots disappearing while customers were still typing their details.",
     "Seven minutes. Long enough to type a phone number, short enough that nobody camps a slot.",
     ["seven minutes", "three minutes", "fifteen minutes"], "seven minutes",
     "A slot is held for seven minutes from the moment the customer picks it.",
     "A longer form would reopen this."),
    ("0002-the-deposit-is-fifteen-percent", "The deposit is fifteen percent of the price", "2026-02-10",
     "No-shows cost shops a chair for the hour. A deposit was the cheapest deterrent.",
     "Fifteen percent. Enough to sting, not enough to scare people off.",
     ["fifteen percent", "a flat fee", "no deposit"], "fifteen percent",
     "Confirming a booking takes fifteen percent of the price as a deposit.",
     "A real payment provider may force a minimum charge and reopen this."),
    ("0003-harbor-club-members-keep-their-refund", "Harbor Club members keep their deposit refund", "2026-03-01",
     "Long-standing customers complained after losing deposits on late cancellations.",
     "Harbor Club people get their deposit back whenever they cancel. They have earned it.",
     ["exempt Harbor Club members", "exempt nobody", "exempt on the shop's say-so"], "exempt Harbor Club members",
     "A Harbor Club member is refunded the deposit however late the cancellation.",
     "Abuse of the exemption would reopen this."),
    ("0004-reminders-go-by-email-only", "Reminders go by email only", "2026-03-15",
     "A second channel doubles the delivery failures to chase, and every customer already gives an address.",
     "Email only for now. One channel we can actually watch.",
     ["email only", "email and a phone call"], "email only",
     "The reminder is one email. No other channel sends it.",
     "A shop whose customers do not read email would reopen this."),
]

ADR_TEMPLATE = """# {n}. {title}

Date: {date}

## Status

Accepted

## Context

{context}

## Decision

**Words:** 「{words}」 — Mira (owner), {date}

**Options considered:**
{options}

**Recommended:** {rec}

**Protects:** none

{rule}

## Consequences

{cons}
"""

README_FLAT = """# Tidepool

Appointment booking for small salons. `ARCHITECTURE.md` describes how the system works;
`docs/adr/` holds the owner's rulings. Tests: `python3 -m unittest discover -s tests`.
"""

README_LAYERED = """# Tidepool

Appointment booking for small salons. `docs/architecture.md` says which document describes each
part of the system; `docs/adr/` holds the owner's rulings. Tests: `python3 -m unittest discover -s tests`.
"""

FLOW_README = """# How you work here

You are the implementation worker for one task in this repository. A coordinator hands you the task
and reads your report; you do not talk to the owner. Read these files, in this order, before you
change anything, and follow them:

{files}

They are copied from the development-flow package this project uses. `<package>` in them is
`.flow/pkg`. This is a trial harness, so `comment_ratio.py` and `number_guards.py` do not apply and
there is no pull request to open; `doc_impact.py` does apply (base is the commit you started from).
The ADR template is `.flow/pkg/references/adr-template.md`. Do not commit: the harness commits what
you leave in the working tree. Run the tests before you finish. End with a short stage report.
"""

AFFECTED = """# Affected documents

Implementation runs `python3 <package>/scripts/doc_impact.py <base> <candidate>`
and records, for each listed document, `updated` or `unaffected: <reason>` in its
stage report; validation reruns it at the candidate and checks every listed
document carries one. Make the update itself by the retained-document practices in
the package's `references/retained-documents.md`.
"""

# The treatment text under test. Frozen before the first scored run.
CONVENTION = """# Documents in this repository

Each kind of document answers one question and lives in one place.

| Document | Question it answers | How it changes |
| --- | --- | --- |
| `docs/architecture.md` | Which document owns this question? | A row is added |
| `docs/architecture/<topic>.md` | How does the system work today? | Edited in place, present tense |
| `docs/adr/NNNN-title.md` | Why was this decided? | Never edited; a new one supersedes it |
| the task you were handed | What is being done now? | Ends with the task |

Read in this order: `docs/architecture.md`, then the topic documents your task touches, then the
ADRs they list, then the code.

Before you finish:

- A task that changes behaviour a topic document states leaves that document true: its States,
  Rules, Known limits and Proof sections describe the system as it now is.
- A new flow gets its own topic document with the same sections, and a row in `docs/architecture.md`.
- A person's ruling becomes a new ADR in their own words. The topic document lists the ADR under
  Governing ADRs and states the rule; the reason stays in the ADR.
- Plans, ideas for later and work in progress stay out of the topic documents and out of the ADRs.
- A change that alters no behaviour leaves the topic documents alone.

In your report, write one line `Architecture touched:` naming each topic document and section you
changed, or `none: <reason>`.
"""


# Round 2. D: map + topic documents on the revised skeleton. E: one file on the same skeleton.
PROOF_BOOKING = """| Property | Evidence |
| --- | --- |
| Hold length | `test_hold_lasts_seven_minutes` |
| Deposit at confirmation | `test_deposit_is_taken_at_confirmation` |
| Refund outside the window | `test_cancel_outside_window_refunds_deposit` |
| No refund inside the window | `test_cancel_inside_window_keeps_deposit` |
| Harbor Club exemption | `test_exempt_group_is_refunded_inside_window` |"""
PROOF_NOTIFY = "| Reminder timing | `test_reminder_goes_twenty_hours_before` |"

MAP2 = """# Tidepool architecture

""" + F["what"] + """ This file is the map: it says which document owns each question.
Each document under `docs/architecture/` states what is the case today.

| You want to know | Read |
| --- | --- |
| How a slot is held, how a booking moves between states, what happens to the deposit | [booking](architecture/booking.md) |
| What the customer is told and when | [notifications](architecture/notifications.md) |

Rulings and their reasons are in `docs/adr/`. Ideas for later are in `docs/journey/later.md`.
Tests run with `python3 -m unittest discover -s tests`.
"""

BOOKING_DOC2 = f"""# Booking

## What this covers, and what it leaves to others

| Owns | Does not own |
| --- | --- |
| Slot holds, booking states, the deposit, cancellation | What the customer is told: [notifications](notifications.md) |

## Rules

- {F['hold']}
- {F['deposit']}
- {F['cancel']}
- {F['exempt']}

## Following a booking from held to finished

{F['states']}

## Proven and not proven

{PROOF_BOOKING}

Not proven: nothing takes real money, so no test covers a failed charge.

## Known limits

- {F['limit']}

## Governing ADRs

- [0001](../adr/0001-a-slot-hold-lasts-seven-minutes.md) slot hold length
- [0002](../adr/0002-the-deposit-is-fifteen-percent.md) deposit size
- [0003](../adr/0003-harbor-club-members-keep-their-refund.md) Harbor Club exemption
"""

NOTIFY_DOC2 = f"""# Notifications

## What this covers, and what it leaves to others

| Owns | Does not own |
| --- | --- |
| What the customer is told after booking, and when | Booking rules: [booking](booking.md) |

## Rules

- {F['reminder']}
- {F['channel']}

## Proven and not proven

| Property | Evidence |
| --- | --- |
{PROOF_NOTIFY}

Not proven: delivery. A reminder is computed, not sent.

## Known limits

- A reminder is computed, not sent: there is no mail provider yet.

## Governing ADRs

- [0004](../adr/0004-reminders-go-by-email-only.md) reminder channel
"""

SINGLE = f"""# Tidepool architecture

{F['what']} This file states what is the case today.
Rulings and their reasons are in `docs/adr/`. Ideas for later are in `docs/journey/later.md`.
Tests run with `python3 -m unittest discover -s tests`.

## What this covers, and what it leaves to others

| Owns | Does not own |
| --- | --- |
| Slot holds, booking states, the deposit, cancellation, the reminder | Taking real money and sending real mail: neither exists yet |

## Rules

### Booking

- {F['hold']}
- {F['deposit']}
- {F['cancel']}
- {F['exempt']}

### Notifications

- {F['reminder']}
- {F['channel']}

## Following a booking from held to finished

{F['states']}

## Proven and not proven

{PROOF_BOOKING}
{PROOF_NOTIFY}

Not proven: nothing takes real money or sends real mail, so no test covers a failed charge or delivery.

## Known limits

- {F['limit']}
- A reminder is computed, not sent: there is no mail provider yet.

## Governing ADRs

- [0001](adr/0001-a-slot-hold-lasts-seven-minutes.md) slot hold length
- [0002](adr/0002-the-deposit-is-fifteen-percent.md) deposit size
- [0003](adr/0003-harbor-club-members-keep-their-refund.md) Harbor Club exemption
- [0004](adr/0004-reminders-go-by-email-only.md) reminder channel
"""

LATER = """# Ideas for later

Not built and not planned. One line each, with who raised it and when.
"""

README_D = """# Tidepool

Appointment booking for small salons. `docs/architecture.md` says which document describes each
part of the system; `docs/adr/` holds the owner's rulings; `docs/journey/later.md` holds ideas for later.
Tests: `python3 -m unittest discover -s tests`.
"""

README_E = """# Tidepool

Appointment booking for small salons. `docs/architecture.md` describes how the system works;
`docs/adr/` holds the owner's rulings; `docs/journey/later.md` holds ideas for later.
Tests: `python3 -m unittest discover -s tests`.
"""

# The revised treatment text. Frozen before the first scored run of round 2.
CONVENTION2 = """# Documents in this repository

Each kind of document answers one question and lives in one place.

| Document | Question it answers | How it changes |
| --- | --- | --- |
{rows}
| `docs/adr/NNNN-title.md` | Why did a person decide this? | Body never edited; see below |
| `docs/journey/later.md` | What might we do someday? | One line added |
| the task you were handed | What is being done now? | Ends with the task |

Read the architecture first, then the ADRs it lists, then the code.

Before you finish:

- A task that changes behaviour leaves the architecture true. State the rule or the number in the
  architecture itself; a link to an ADR never stands in for the sentence.
- Only a ruling a person made becomes an ADR, in that person's quoted words. An instruction from the
  coordinator is a task, not a ruling: change the code and the architecture and write no ADR.
- When a new ADR replaces an older one, change the older one's Status line to `Superseded by NNNN`
  and nothing else in it. List the new ADR under Governing ADRs.
- An idea for later goes in `docs/journey/later.md` as one line, never in the architecture or an ADR.
- {newflow}
- A change that alters no behaviour leaves the architecture alone.

In your report, write one line `Architecture touched:` naming each document and section you changed,
or `none: <reason>`.
"""
ROWS_D = ("| `docs/architecture.md` | Which document owns this question? | A row is added |\n"
          "| `docs/architecture/<topic>.md` | How does the system work today? | Edited in place, present tense |")
ROWS_E = "| `docs/architecture.md` | How does the system work today? | Edited in place, present tense |"
NEWFLOW_D = "A new flow gets its own topic document with the same headings, and a row in `docs/architecture.md`."
NEWFLOW_E = "A new flow gets its own `###` group under Rules and its rows under Proven and not proven, in the same file."
ONE_PER = "Write one file per decision, `docs/adr/NNNN-short-title.md`"
ONE_PER_RULING = "Write one file per ruling a person made, `docs/adr/NNNN-short-title.md`"


def pkg_file(path):
    return subprocess.run(["git", "-C", PKG_REPO, "show", f"{PKG_SHA}:kc-dev-flow-2/{path}"],
                          check=True, capture_output=True, text=True).stdout


def build(dest, arm):
    layout, rules = ARMS[arm]
    dest = Path(dest)
    files = {
        "tidepool/__init__.py": "",
        "tidepool/booking.py": BOOKING,
        "tidepool/slots.py": SLOTS,
        "tidepool/notify.py": NOTIFY,
        "tests/test_tidepool.py": TESTS,
        ".gitignore": "__pycache__/\n",
    }
    for slug, title, date, context, words, options, rec, rule, cons in ADRS:
        files[f"docs/adr/{slug}.md"] = ADR_TEMPLATE.format(
            n=int(slug[:4]), title=title, date=date, context=context, words=words,
            options="\n".join(f"- {o}" for o in options), rec=rec, rule=rule, cons=cons)
    if layout == "flat":
        files["README.md"] = README_FLAT
        files["ARCHITECTURE.md"] = FLAT
    elif layout == "layered2":
        files["README.md"] = README_D
        files["docs/architecture.md"] = MAP2
        files["docs/architecture/booking.md"] = BOOKING_DOC2
        files["docs/architecture/notifications.md"] = NOTIFY_DOC2
        files["docs/journey/later.md"] = LATER
    elif layout == "single":
        files["README.md"] = README_E
        files["docs/architecture.md"] = SINGLE
        files["docs/journey/later.md"] = LATER
    else:
        files["README.md"] = README_LAYERED
        files["docs/architecture.md"] = MAP
        files["docs/architecture/booking.md"] = BOOKING_DOC
        files["docs/architecture/notifications.md"] = NOTIFY_DOC
    flow = ["principles.md", "retained-documents.md", "affected-documents.md"]
    files[".flow/principles.md"] = pkg_file("skills/implementation/principles.md")
    files[".flow/retained-documents.md"] = pkg_file("references/retained-documents.md")
    files[".flow/affected-documents.md"] = AFFECTED
    files[".flow/pkg/scripts/doc_impact.py"] = pkg_file("scripts/doc_impact.py")
    files[".flow/pkg/references/adr-template.md"] = pkg_file("references/adr-template.md")
    files[".flow/pkg/references/retained-documents.md"] = files[".flow/retained-documents.md"]
    if rules == "convention":
        flow.append("documents.md")
        files[".flow/documents.md"] = CONVENTION
    if rules == "convention2":
        flow.append("documents.md")
        single = layout == "single"
        files[".flow/documents.md"] = CONVENTION2.format(rows=ROWS_E if single else ROWS_D,
                                                         newflow=NEWFLOW_E if single else NEWFLOW_D)
        assert files[".flow/principles.md"].count(ONE_PER) == 1
        files[".flow/principles.md"] = files[".flow/principles.md"].replace(ONE_PER, ONE_PER_RULING)
    files[".flow/README.md"] = FLOW_README.format(files="\n".join(f"{i}. `.flow/{f}`" for i, f in enumerate(flow, 1)))
    for rel, text in files.items():
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    env = {"GIT_AUTHOR_DATE": "2026-04-01T09:00:00Z", "GIT_COMMITTER_DATE": "2026-04-01T09:00:00Z",
           "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(dest)}
    for args in (["init", "-q", "-b", "main"], ["add", "-A"],
                 ["-c", "user.name=harness", "-c", "user.email=harness@example.invalid", "commit", "-q", "-m", "world"],
                 ["tag", "step-0"]):
        subprocess.run(["git", "-C", str(dest), *args], check=True, env=env)
    return dest


if __name__ == "__main__":
    import sys
    build(sys.argv[2], sys.argv[1])
