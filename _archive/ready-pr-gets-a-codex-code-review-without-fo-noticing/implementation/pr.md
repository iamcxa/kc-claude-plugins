fix(kc-dev-flow-2): request Codex review when marking ready

When the First Officer marks a pull request ready, the Codex extension now says to comment `@codex review` once at that moment. The existing instruction to request review after a repair remains in place.

Validation: the candidate sentence search and package lint pass; removing the sentence makes the search fail. ADR lint, number guards, document impact and comment ratio pass. RoboRev and hosted CI have not been run.
