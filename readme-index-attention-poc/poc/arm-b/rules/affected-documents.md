## Affected documents

Implementation runs `python3 <package>/scripts/doc_impact.py <base> <candidate>`
and records, for each listed document, `updated` or `unaffected: <reason>` in its
stage report; validation reruns it at the candidate and checks every listed
document carries one. Make the update itself by the retained-document practices in
the package's `references/retained-documents.md`.

