# VEIL: 2 minute 40 second demonstration

Use after slide 6, or pause on slide 5. Prepare the local demo using Demo-runbook.md before presenting. Existing screenshot artifacts are a fallback only and must be identified as captures if used.

| Time | Action | Exact narration |
|---|---|---|
| 0:00–0:20 | Open Case Overview and Data Sources | “This is a synthetic case. Four source types have been processed: report text, call records, transactions and vehicle records. Each keeps its source identity and evidence locator.” |
| 0:20–0:45 | Open Entity Resolution and the Rahul / R.K. Sharma proposal | “A similar name alone is insufficient. We inspect the shared identifiers and their source records. A reviewer can confirm the identity or leave it unresolved. Original mentions remain preserved.” |
| 0:45–1:10 | Open Network; select Rahul Kumar Sharma and Vikram Singh; find path | “The backend computes this six-hop association path. Each relationship links to source evidence. This path does not establish chronology or wrongdoing.” |
| 1:10–1:45 | Open Lead 17 and expand its calculations | “Eleven calls differ from the two-per-day baseline. Three connected transfers occur within seventy-five minutes. Graph context overlaps these records. The rule engine uses these categories to prioritize review, not estimate guilt.” |
| 1:45–2:10 | Open a source evidence link | “Here is the exact source row or excerpt supporting the signal. The investigator can check the calculation against its evidence rather than accept an unexplained score.” |
| 2:10–2:40 | Submit Needs More Evidence with a reason; open Audit Trail | “The human records the decision and reason. The application retains that action in its audit history. VEIL surfaces the connection; the investigator decides what it means.” |

NER and Behavioral Profiles are optional Q&A demonstrations. Describe spaCy as probabilistic extraction and Isolation Forest as statistical triage. Neither establishes guilt. Do not add these steps to the timed route unless replacing another section.
