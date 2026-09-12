# Cycle 3 — controlled multi-source ingestion

## 1. Implemented

The existing workspace now has Data intake: load/reset official samples, select a local file and validate upload, process sources, inspect manifests, raw/normalized records, mentions, claims, errors and exact evidence, then continue to the extracted graph or resolution queue.

Four real UTF-8 sample files under demo-data/intake produce 15 records: 14 valid, one invalid CDR duration; 46 extracted mentions (including scalar dates/money/identifiers), 16 graph entities, nine positive relationship candidates and five withheld claims. With the preserved base fixtures and no confirmed merges, the combined graph has 58 entities and 52 relationships.

The exact sentence “Rahul Sharma did not meet Vikram Singh on 12 August.” is retained as NEGATIVE / NEGATED and produces no MET edge. A possible meeting is UNCERTAIN and also withheld. Unsupported wording and non-relational report lines produce no graph relationship. All extracted mentions, claims, graph items and evidence are UNVERIFIED.

## 2. Technical decisions

- Extended the existing React/Cytoscape/FastAPI architecture without adding dependencies. Text reports were selected instead of PDF; no OCR, universal document parser, external LLM, or NER model.
- Exact CSV schemas and value validation; rules for structured identifiers; fixed people/organization/location dictionaries; full-sentence typed relationship templates. Dates lacking a year retain that uncertainty. Report sentences do not fabricate event timestamps.
- Upload uses application/json with filename, source_type and UTF-8 content. The file picker reads the actual selected bytes with fatal UTF-8 decoding. JSON avoids adding multipart dependencies. Maximum file size is 64 KiB, 16 files, bounded request envelope. Only plain ASCII .csv/.txt basenames are accepted; path traversal, Windows reserved names, unsupported types and binary controls are rejected. Filenames are never used as destination paths.
- SHA-256 fingerprints UTF-8 content. IDs derive from type/checksum/record position; identical content and type is deduplicated even under a renamed file. Reprocessing replaces the generated snapshot atomically without duplicate records or edges. Header errors invalidate a whole file; row errors reject that row while retaining raw evidence.
- SQLite intake.sqlite3 stores original content, manifests and a small processed snapshot. Automatic idempotent initialization; no ORM or database migration of the base graph. VEIL_INTAKE_DB optionally overrides the path.
- Every mention/claim resolves through a source record and evidence ID. Records contain exact original excerpts, raw fields, normalized fields, physical CSV row and character offsets, version and verification status. Character offsets are zero-based Unicode character indexes with an exclusive end, not byte offsets. Quoted multiline CSV locators are tested.
- The backend adds processed positive source assertions to the graph projection. Names never silently merge with Cycle 2 identities: people remain source-local, while exact structured asset identifiers connect across these controlled files. Person choices include their source filename. The existing resolution queue remains the Cycle 2 candidates; automatically creating new resolution proposals from intake is outside this cycle.
- Graph status 'recorded' means a positive assertion occurs in the source; verification_status remains UNVERIFIED. It does not mean the assertion is a verified fact. Negated, possible and unsupported claims remain available for inspection but are excluded from traversal.
- The frontend consumes graph/path results; its grid coordinates are presentation only. The extracted graph has its own view within the existing canvas. Finding the original Rahul–Vikram path restores the familiar focused layout.

## 3. Files changed

Created:

- demo-data/intake/report.txt, cdr.csv, transactions.csv, vehicles.csv
- backend/intake_models.py, intake_parser.py, intake_store.py
- frontend/src/intakeTypes.ts, components/DataIntake.tsx
- tests/test_intake.py, CYCLE-3.md, artifacts/cycle3/*.png

Modified:

- backend/main.py: required six endpoints, controlled reset, augmented graph/evidence/source/path responses
- backend/demo_schemas.py: source-record provenance, optional event timestamp, explicit machine verification/version fields
- frontend/src/api.ts, demoTypes.ts, components/NetworkWorkspace.tsx, components/InvestigationInspector.tsx, Graph.tsx, golden.css
- tests/test_golden_flow.py and test_resolution.py: isolated intake state alongside existing database isolation; API count updated
- README.md: Cycle 3 usage, limits and API instructions

Dependency manifests/locks, original fixtures, legacy modules and resolution decisions were preserved. Local runtime intake.sqlite3 is automatically initialized and already covered by the existing ignore pattern. There is no Git metadata in this workspace.

## 4. Run commands

No additional dependencies. Existing setup instructions in README still apply.

```powershell
cd 'Z:\XLab\New\Network Intel'
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Second terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm run dev -- --port 5173 --strictPort
```

Open http://127.0.0.1:5173/. Servers are running. Data intake → Load official samples / reset intake replaces only intake content/output and reloads the four official files; then Process sources. Base fixtures and human resolution decisions are unchanged. POST /api/cases/demo/intake/reset with {"reload_samples":false} clears only intake without reloading samples.

## 5. Tests and builds

- `python -m pytest -q --tb=short`: 43 passed, including all prior 25 tests and 18 intake cases.
- Covers valid/invalid CDR, transactions, vehicles, dictionaries and structured entity extraction, date/phone/money/case/transaction identifiers, negation, uncertainty, unsupported and wrongly typed templates, checksum, exact report/CSV evidence locators, multiline CSV, duplicate record IDs, reprocessing/restart persistence, reset, filename attacks, file size/type/header validation and unknown records.
- Integration checks cover graph additions and source evidence, computed paths through extracted edges, original six-hop path, Lead 17, and confirm/undo while intake is processed.
- `npm run typecheck`: passed. `npm run build`: passed; existing large-chunk warning remains (approximately 684 kB, 216 kB gzip). Two existing Python dependency deprecation warnings remain.
- Browser at 1366x768: official sample load and validation, process metrics, negated claim evidence with exact character span, generated graph, original six-hop path, path evidence, Lead 17 and transaction evidence. The initial extracted grid clipped nodes; corrected to a compact four-column layout and visually rechecked.
- Browser file chooser upload was implemented but not exercised through native selection automation; the real upload endpoint was tested with all four formats and malformed inputs. No new frontend test framework or fresh dependency installation was added; dependencies are unchanged.

## 6. Limitations

Controlled English sentence templates, small fixed dictionaries, strict schemas, TXT reports only, INR channels and synthetic asset identifiers. No universal extraction accuracy claims. Source-local people are not automatically resolved against existing people. The base golden graph and Lead 17 remain fixtures; only the separately labelled extracted graph is derived from these uploaded files. A file edit creates a new source fingerprint, not an automatic replacement; use reset for a clean official run. Duplicate content is deduplicated, but semantic duplicate transactions across distinct edited source files are retained separately with provenance. Source integrity checks are not verification of source truth. No authentication, tamper-proof storage, or deployment was added.

## 7. Exact manual demo

1. Open Data intake and select Load official samples / reset intake. Show four files and cdr.csv row 4's invalid duration.
2. Click Process sources: 15 records, 46 mentions, 9 candidates, 1 invalid, 5 withheld.
3. Open Sources → Source manifest / SHA-256 to show checksum, parser version and upload time.
4. Open Records, choose a CSV row, inspect its raw excerpt and normalized fields, then Open record evidence. The inspector shows filename, row/character offsets, parser and UNVERIFIED status.
5. Open Mentions to inspect extracted names, identifiers, dates and money with evidence.
6. Open Claims and scroll to MET / NEGATED. Open its Evidence: the exact report sentence says Rahul did not meet Vikram. No relationship is attached. The possible meeting is separately UNCERTAIN.
7. Click View extracted graph. It shows 16 source-derived entities and 9 positive candidate edges. Select an entity or edge and trace its evidence. No MET edge exists.
8. Click Find path using the unchanged default Rahul Kumar Sharma / Vikram Singh controls. Show the original six-hop path; open E-CDR-01, Lead 17 and E-TX-01.
9. Return to Data intake and Process sources again; counts and identifiers stay unchanged. Continue to resolution review opens the preserved Cycle 2 queue.

## 8. Screenshots

- artifacts/cycle3/intake.png — processing counts and invalid row
- artifacts/cycle3/negation.png — negated source span and evidence
- artifacts/cycle3/graph.png — source-derived graph

## 9. Definition of done

Satisfied for this controlled cycle: all four formats process, a validation error is visible, extracted results have exact provenance, negated/uncertain relationships are withheld, processed results update graph queries, reprocessing is idempotent, and previous cycles pass their regressions and golden-flow browser checks.
