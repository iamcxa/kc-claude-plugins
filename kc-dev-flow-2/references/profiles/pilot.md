# Pilot: bounded real use

Deliver one integrated user journey for limited real use and likely iteration,
without silently accepting long-term production obligations.
Use repository-native structure where it lowers near-term iteration cost;
avoid hypothetical scale and general-purpose platform work.

Cover real persistence and external seams. Include diagnostics, recovery,
duplicate handling and data safety where the accepted journey exposes them.
Test owned behavior and real seams rather than stable vendor internals.

Return to profile selection if scope adds production data or credentials, broad
exposure, a consumer-required compatibility migration, irreversible migration,
unattended recurring operation, support/SLO duty or release/rollback ownership.
A normal published upgrade that consumers can absorb remains eligible for Pilot
with its applicable version and migration-note obligations; publication alone
does not select Production.
