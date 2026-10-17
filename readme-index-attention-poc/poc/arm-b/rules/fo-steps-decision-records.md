## FO steps: decision records

A ruling settled at a gate, in a worker report, or mid-stage feedback — a rule about
the product, a constraint, or a direction later work must respect — is landed as an
ADR before the next gate is presented, at latest by the terminal approval. A ruling
that governs only this task's own work stays in the task. A design names an ADR
by its ruling and the file's short title, with no number; FO reserves the number when
it dispatches implementation (Number guards) and the implementation worker writes
`docs/adr/<reserved number>-<short-title>.md`. FO confirms the validation ADR lint
passes before presenting the gate. A deferred user-facing capability belongs on
the product's journey map, not here.

