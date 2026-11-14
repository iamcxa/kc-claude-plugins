# Close stdout and checksums

The close command exited 0 and removed scratch. Its stdout was redirected into close.log in the evidence folder; the close command enumerated that file before stdout was populated, so the original checksum list records close.log as empty.

SHA256SUMS.before-stdout retains the original list unchanged. SHA256SUMS was then regenerated after stdout capture completed and checked against every retained evidence file (excluding SHA256SUMS itself). Source evidence and frozen hypotheses were not changed. The exact close stdout remains in close.log; its file/size totals refer to the close command's enumeration, before this explanatory note and the preserved original list were added.
