# VEIL — golden judge flow

Current cycle: selection-quality UI, reliability and demo hardening. See [CYCLE-6.md](docs/cycles/CYCLE-6.md) for the verified results and [DEMO-RUNBOOK.md](docs/demo/DEMO-RUNBOOK.md) for the exact 13-step judge flow, screenshots and recording guidance.

The SIH first-round freeze and evidence pack are documented in [SIH-SCOPE-FREEZE.md](docs/sih/SIH-SCOPE-FREEZE.md), [SIH-FIRST-ROUND-EVIDENCE.md](docs/sih/SIH-FIRST-ROUND-EVIDENCE.md), [SIH-JUDGE-QA.md](docs/sih/SIH-JUDGE-QA.md), and [artifacts/first-round](artifacts/first-round/index.html).

A synthetic SIH prototype with controlled source ingestion, explainable entity resolution, reversible human decisions and deterministic temporal lead generation. VEIL surfaces investigative leads, not accusations.

The bounded AI architecture and judge-safe failure modes are summarized in [docs/AI-SYSTEM-NOTE.md](docs/AI-SYSTEM-NOTE.md). Groq is optional; the core investigation flow and grounded fallback require no paid service.

**Case hub:** create a fresh synthetic investigation, upload source files, and generate the active workspace from those records. The bundled reference case is no longer the product identity.

## Fresh setup (Windows PowerShell)

Tested with Python 3.14.6 and Node 24.16.0. Run from the project root. Dependency installation needs internet or a populated package cache; the installed demo runs without internet, API keys, external AI. SQLite review storage initializes automatically.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe -m backend.serve_demo --reset --port 8000
```

Open [VEIL](http://127.0.0.1:8000/). One process serves the production UI and API. Stop it with Ctrl+C before resetting or restarting; do not start duplicate servers. Omit `--reset` on later starts to preserve decisions.

The launcher uses dedicated SQLite state under `backend/data/rehearsal` and archives those databases before an explicit reset. Four official source files are processed automatically. Earlier-cycle databases are preserved. No mandatory environment variables or external services are required. The normal application audit is append-only; the explicit archived rehearsal reset is an administrative exception.

For frontend development, keep this backend running and run `npm run dev -- --port 5173 --strictPort` in `frontend`. Vite proxies `/api` to port 8000. There is no hosted deployment configured.

## Current judge demonstration

Follow the [exact 13-step runbook](docs/demo/DEMO-RUNBOOK.md#exact-judge-flow-and-recording-script). The visible-browser rehearsal completed in **107.054 seconds excluding narration**. A spoken three-minute recording has not been timed. [Screenshots](artifacts/cycle6/index.html) and [sample API exports](artifacts/sample-api/) provide explicitly labelled fallback references.

## Cycle 5 decision-loop demonstration

Open Lead 17, inspect its evidence, enter a reviewer and choose **Needs more evidence**. Add an optional reason, click **Review submission**, then **Confirm submission**. The updated status persists across reloads and backend restarts. **Review history** retains earlier decisions. The current demo includes a review submitted during browser verification.

Open **Audit history**, filter Action to **LEAD REVIEW SUBMITTED** and apply. Inspect actor, reason and previous/new state. Open **Timeline**, select **transfer**, **Transaction** and **Account A17**, then open **E-TX-01** from an event card. Timeline labels distinguish observed source events, extracted claims, analytical signals and human/system actions. Time filters are interpreted in IST; undated claims sort last and are excluded by date filters.

All six requested review actions are available. Relationship verification and incorrect-merge assessments require an explicit supporting object ID. They record the investigator's assessment; source flags are unchanged, and merge reversal uses the existing Resolution review flow. Reviews are tied to the computed lead revision, so changed results do not inherit an old status. Identical submission retries are idempotent.

The journal records source upload/processing, resolution/undo, lead generation/access, evidence access and review submission. Audit generation timestamps are wall-clock times; analytical signals retain the documented replay timestamp. Access entries identify a local demo session, not an authenticated person. There is no cryptographic tamper-resistance claim. Normal application behavior cannot edit or delete audit entries.

## Earlier cycles

Historical implementation reports remain in `docs/cycles/CYCLE-1.md` through `docs/cycles/CYCLE-5.md`. Use the current runbook for judge timings, graph counts and reset instructions: processed source mentions and confirmed aliases change the active graph projection.

## Data and analytical boundaries

- 42 original entities: 12 person mentions, 12 non-dialable synthetic phone identifiers, 8 accounts, 3 vehicles, 4 locations, 3 organizations.
- 43 relationships; each has resolvable evidence. 62 exact evidence records in 9 synthetic source collections. Confirming Rahul projects 41 canonical entities without deleting source mentions.
- Six deterministic fixture files in `backend/data/demo`: entities, relationships, events, leads, evidence, sources.
- A schema-validated repository loads graph, event and evidence fixtures at startup and validates identifiers/provenance. Corrupt fixtures fail visibly at startup. The compatibility leads file is empty and is not loaded by the runtime.
- NetworkX performs bounded breadth-first shortest-path traversal, with a maximum of 8 hops and deterministic edge ordering. Traversal is undirected association search; each step states its traversal direction. Display positions never determine a path.
- Lead 17 is computed by `temporal-leads-v1` from event records, current graph projection and exact evidence. There is no fixture fallback; nonqualifying inputs return an empty inbox.
- Baseline: two calls on each of seven days, then 11 calls; seven event-day contacts absent from the baseline. Three account transfers total INR 195,000 over 75 minutes. This is transfer volume, not necessarily distinct funds.
- The shortest Rahul–Vikram path contains A17 and A31. A44 belongs to the seven-hop alternate route through A17 → A44 → A31; the lead explicitly states that it is not on the shortest path.
- The last listed transfer precedes the fictional Event X report by 10 minutes. Temporal proximity is not causation.
- Base source filenames identify canonical synthetic record collections. Controlled Cycle 3 files can also be processed into graph records and analytical events. No real investigation data is used. Phone numbers are explicitly non-dialable DEMO identifiers.

## API

The active endpoints return Pydantic-validated JSON. Graph responses retain synthetic-data metadata; computed lead responses expose the engine version and replay clock.

| Endpoint | Result |
|---|---|
| `GET /api/cases/demo` | Active case metadata and counts |
| `GET /api/cases/demo/sources` | Source registry |
| `GET /api/cases/demo/graph` | Nodes and typed relationships |
| `GET /api/cases/demo/leads` | Computed lead inbox, signals and engine diagnostics |
| `GET /api/cases/demo/signals` | Computed signals with calculations and evidence |
| `GET /api/leads/17` | Lead 17 explanation, signals, disclaimer and provenance |
| `GET /api/evidence/{evidence_id}` | Exact record, locator, fields, status and related IDs |
| `GET /api/cases/demo/path?source=rahul&target=vikram&max_depth=8` | Computed nodes, relationships, steps, evidence references and path_length |

Unknown IDs: 404 with a helpful code/message. Disconnected or depth-limited paths: 404 `NO_PATH_WITHIN_DEPTH`. Invalid/missing parameters, or depth outside 1–8: 422 `INVALID_REQUEST`. Same known source/target: zero-hop result. Inspect schemas at [API docs](http://127.0.0.1:8000/docs).

## Tests and build

From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
cd frontend
npm run lint
npm run typecheck
npm run build
npm test
```

101 backend tests and 2 Playwright browser tests pass. Root-level `pytest` discovery is restricted to the product suite, so vendored artifact dependencies are not collected. Active-code lint, type checking and production build pass. Browser tests use installed Microsoft Edge and an isolated server on port 8001; build first. See `docs/cycles/CYCLE-6.md` for error recovery, console/network, clean setup and restart verification, plus the remaining warnings.

## File organization

- `backend/main.py`: active API including resolution decisions.
- `backend/demo_schemas.py`, `demo_repository.py`, `demo_paths.py`, `generate_demo.py`: contracts, fixtures, traversal and deterministic authoring.
- `frontend/src/components/NetworkWorkspace.tsx`: case, graph, search, path controls, sources and lead inbox.
- `frontend/src/components/InvestigationInspector.tsx`: entity, relationship, path, lead and evidence drawers.
- `frontend/src/components/EvidenceRefs.tsx`: expandable evidence references.
- `frontend/src/Graph.tsx`: retained Cytoscape renderer, adapted for the new case and path fading.
- `frontend/src/demoTypes.ts`, `api.ts`, `golden.css`: contracts, request helpers, scoped styling over the retained theme.
- Earlier UI and backend are preserved as `LegacyApp.tsx`, `LegacyGraph.tsx`, `legacyTypes.ts`, and `backend/legacy.py`; old fixtures, detector, tests, database and reports remain available for reference. They are not mounted by the active app.

## Limitations

One synthetic case; bounded rule-based temporal lead generation; controlled CSV/TXT ingestion only; no universal NER/extraction or authentication. Resolution scores use uncalibrated fixed rules; reviewer identity is self-declared for this local demo. Lead review decisions persist in a separate SQLite journal; resolution decisions remain reversible. Full-network exploration uses pan/zoom rather than forcing every label into a tiny canvas. No accuracy or real-world investigative validity claims. Dependency deprecation and bundle-size warnings are recorded, not hidden. Use the local single-process build for judging; hosted SQLite state is ephemeral and must not be presented as durable storage.


## Cycle 2 resolution review

Open Resolution review in the existing sidebar. Select R.K. Sharma or A. Verma. Inspect the normalized name comparison, phone and vehicle features, weights, evidence and recommendation. Original entity summaries expand to source records. Scores are ranking scores, not probabilities.

For R.K. Sharma, enter a reviewer and reason, then Confirm. The graph has 41 canonical entities; searching R.K. Sharma opens Rahul with the alias and both original IDs. Evidence retains original mentions. An active path is recalculated by the backend. Return to Resolution review, enter an undo reason, then Undo to restore 42 separate entities. Decision history shows both actions and the reversal reference.

A. Verma scores 16.5/100: no shared phone or vehicle. It remains REVIEW until a human decides. Reject and Defer record decisions without changing identity. A later decision can reconsider either; confirmed matches must be undone first. No recommendation, including YES, automatically merges.

New typed endpoints:

- GET /api/cases/demo/resolution-proposals
- GET /api/resolution-proposals/{proposal_id} (proposal plus ordered decision history)
- POST /api/resolution-proposals/{proposal_id}/decisions
- POST /api/resolution-decisions/{decision_id}/undo

POST body: {"action":"CONFIRM_MATCH","reviewer":"Demo investigator","reason":"Reviewed source evidence"}. Other actions: REJECT_MATCH, DEFER, UNDO_CONFIRMED_MATCH. Undo requires the undo action and active confirmation ID. Conflicts return 409; blank reviewer/reason returns 422.

Normalization: Unicode NFKC, case folding, punctuation removal, whitespace collapse. Blocking: same surname and first initial, or exact shared phone entity. Score: normalized string similarity x0.2 + exact shared phone x0.6 + shared vehicle x0.2. YES needs score at least 0.99 plus phone; REVIEW needs phone or name similarity at least 0.35; otherwise NO. Missing identifiers contribute zero, not a contradiction. Common names and shared assets remain a risk. Canonical display preference: longer normalized name, then stable ID. These rules are demo heuristics, not validated identity inference.

SQLite stores only append-only decisions. Idempotent initialization uses CREATE TABLE IF NOT EXISTS; proposals are computed deterministically from fixtures. Historical resolution-only reset for the original database (use `backend.serve_demo --reset` for the current dedicated rehearsal):

```powershell
.\.venv\Scripts\python.exe -m backend.reset_resolution
```

This clears only this cycle's decision history; reload the browser afterward. Regenerating fixtures does not erase decisions. Restart the backend after fixture regeneration. See docs/cycles/CYCLE-2.md for files, verification, limitations and screenshots.


## Cycle 3 controlled intake

See docs/cycles/CYCLE-3.md for the complete implementation report and manual demo. Data intake in the sidebar loads official sample files, accepts local CSV/TXT file selection, validates sources, processes records and opens exact evidence. Load official samples / reset intake replaces only intake output and files. Then Process sources. Expected: 15 records, 14 valid, one invalid CDR row, 46 mentions, 16 new graph entities, 9 candidate edges, 5 withheld claims. The separate extracted graph is derived from files; the earlier golden graph remains fixtures. Both coexist without silently merging person names.

Actual sample files: demo-data/intake/report.txt, cdr.csv, transactions.csv, vehicles.csv. Match CSV headers exactly. Reports use the controlled templates and dictionaries in backend/intake_parser.py. The negated Rahul/Vikram meeting and uncertain Rahul/Amit meeting are retained but never added as positive graph edges. All extracted items are UNVERIFIED.

No new dependencies. Intake storage initializes automatically at backend/data/intake.sqlite3; optional VEIL_INTAKE_DB overrides it. UTF-8 text only, CSV or TXT, 64 KiB per file, maximum 16 files. Uploads must use plain non-reserved filenames; paths and unsupported extensions are rejected. Report PDF/OCR and external AI are not supported. Regenerating base fixtures does not reset intake.

API:

- POST /api/cases/demo/sources/upload with JSON {"filename":"cdr.csv","source_type":"CDR","content":"...CSV text..."}; source_type is Report, CDR, Transaction or Vehicle. This is a JSON text upload, not multipart.
- POST /api/cases/demo/process
- GET /api/cases/demo/processing-summary
- GET /api/cases/demo/source-records
- GET /api/source-records/{record_id}
- GET /api/cases/demo/extracted-claims
- POST /api/cases/demo/intake/reset with {"reload_samples":true}; false clears only intake.

Each source manifest records case ID, filename/type, SHA-256, parser version, upload time, record count, status and validation errors. Source records expose exact raw fields/excerpt, normalized fields and row/character offsets. Evidence is available through the existing evidence endpoint. Character spans are zero-based and end-exclusive; missing report event timestamps are explicitly absent, not invented. An unchanged upload or reprocess does not duplicate records. A changed source is a new fingerprint; semantic deduplication across differing files is outside this cycle.

## Cycle 4 computed temporal leads

`backend/lead_engine.py` computes communication bursts, new contacts, connected transfers and bounded graph-path correlation. Typed contracts are in `backend/lead_models.py`. `frontend/src/components/LeadDetail.tsx` displays the backend calculations and opens their evidence; the frontend does not calculate analytical results.

The baseline is the previous seven complete IST calendar days, including zero-call days. At least three observed baseline days are required. Event-day outbound calls must reach both five calls and three times the median; new contacts require at least three contacts absent from the baseline. Financial sequences require at least three connected transfers within an inclusive 90-minute window. Graph correlation uses at most eight hops, the involved phone, at least two involved accounts, and communication within 90 minutes of the transfers. Separate ownership evidence is required for the graph-context category.

Communication burst and new contacts count as one category. HIGH requires three traceable categories; MEDIUM requires two. Although the policy labels one category LOW, a single category cannot create a lead. Categories are distinct operational checks, not a claim of statistical independence. Review priority determines examination order. It is not a probability of criminal activity.

The default engine calculates a median of 2 calls/day, 11 event-day calls, 7 new contacts and three transfers totaling INR 195,000 over 75 minutes within the configured 90-minute window. Generated time uses the case event timestamp as a deterministic replay clock, not request wall time. Select a priority filter, open the computed lead, expand each signal and use its evidence links or **Show computed signal path**.

Run the labelled synthetic evaluation from the project root:

```powershell
.\.venv\Scripts\python.exe -m backend.temporal_validation
```

Ground truth and three materialized datasets are in `demo-data/temporal-validation`. Results are written to `artifacts/cycle4/evaluation.json`: primary 4/4 expected signals, alternate 4/4, benign-only 1/1; zero false leads, complete evidence traces and deterministic repetition in these datasets. The alternate dataset changes dates, baseline counts, contacts and transfer amounts. These results make no claim about real-world accuracy. See `docs/cycles/CYCLE-4.md` for the complete cycle report.
