# VEIL alternate live-demo case packs

These records are entirely fictional and use non-dialable `+910000000xxx`
identifiers. They are designed for VEIL's controlled TXT/CSV intake, not for
real investigations.

Each directory contains one investigation report, one CDR CSV, one transaction
CSV and one vehicle CSV. Upload each file with the matching source type shown
below, then select **Process sources**.

| File suffix | VEIL source type |
|---|---|
| `report.txt` | Report |
| `cdr.csv` | CDR |
| `transactions.csv` | Transaction |
| `vehicles.csv` | Vehicle |

## Scenario 1 — Operation Riverglass

A high-interest coordination scenario. CDR, transaction and vehicle records
overlap near Rivergate depot. This is useful for demonstrating extraction,
cross-source evidence and why a pattern deserves earlier human review.

Expected intake result: all rows valid; positive `USES`, `CALLED`,
`TRANSFERRED_TO`, `REGISTERED_KEEPER` and `OBSERVED_WITH` candidates. The
negative Rahul/Vikram meeting sentence must be retained without creating a
positive `MET` relationship.

## Scenario 2 — Operation Cedar Loop

An ambiguous commercial scenario. Records show communication and payments,
but the report explicitly provides an ordinary invoice explanation and only a
possible meeting. Use this to explain why VEIL preserves uncertainty and does
not treat association as guilt.

Expected intake result: all rows valid. The `may meet` sentence is withheld as
uncertain. The unsupported invoice-purpose sentence remains source evidence but
does not create an invented relationship.

## Scenario 3 — Operation Northstar Fair

A benign busy-day scenario involving event logistics. It contains many calls
and routine supplier payments, plus one intentionally invalid CDR duration.
Use this to show validation and the difference between unusual activity and a
criminal allegation.

Expected intake result: one rejected CDR row. The negative meeting sentence is
preserved and no positive `MET` edge is created.

## Recommended judge use

Keep **Operation Trinetra** as the main end-to-end demonstration because its
computed Lead 17 and graph path are fully planted and tested. If a judge asks
whether VEIL can accept other records, upload one alternate pack and show the
records, mentions, claims, rejected rows and evidence locators. Do not promise
that these alternate intake packs generate the same Lead 17; the current lead
engine is calibrated to the deterministic Trinetra replay dataset.

