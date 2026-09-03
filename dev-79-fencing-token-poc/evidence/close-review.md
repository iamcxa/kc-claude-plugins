# DEV-79 close review

Direction: change. The writer fence held (AC-1, AC-2) and its absence produced two persisted claims (AC-3), but the create call already in flight when the holder slept left an orphan workspace, so exactly-once needs a reconcile pass by the new holder. Evidence: run-laptop.log, run-alwayson.log, orphans.txt, reconcile.txt, claims.txt, holder-final.json. Candidate 72f5c215 retained on branch for Captain decision.
