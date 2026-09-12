# Design QA — Investigator case hub

## Final comparison

- Viewport checked: desktop in-app browser at the existing product's standard wide layout.
- Visual target: the established Network Intel graphite/violet investigation console, serif display headings, compact evidence typography, restrained square cards, and persistent synthetic-data boundary.
- Dashboard: passed. Case hierarchy, active-case priority, counts, and primary creation action are readable without leaving the existing design system.
- Create flow: passed. The empty-case promise is explicit before creation and the primary action moves directly to source intake.
- Intake empty state: passed. It shows zero graph/lead state and asks for judge-supplied CSV/TXT evidence.
- Processed case: passed. Four uploaded Riverglass sources appear with exact record counts and processed status.
- Core investigation: passed. Rahul Sharma to Vikram Singh resolves as an eight-hop, eight-evidence path with every step inspectable and unrelated records dimmed.
- Safety posture: passed. Synthetic data, evidence/inference separation, no-confidence claim, and “lead, not proof” language remain visible.
- Responsive CSS: passed by inspection; case cards, summary metrics, modal, and compact case rows collapse at the existing mobile breakpoint.

## Functional verification

- Create fresh investigation
- Preserve the active case when resetting/reloading its evidence pack
- Upload Report, CDR, Transaction, and Vehicle files
- Parse 28 records into 24 entities and 24 relationships
- Compute one explainable lead
- Find the intended eight-hop evidence path
- Open case overview, source intake, network, path inspector, and lead inbox

## Known limit

The archived/reference case cards are intentionally read-only demo summaries; only the active case opens a full workspace in this local prototype.

final result: passed
