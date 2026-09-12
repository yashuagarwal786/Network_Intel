# Cycle 2 — explainable entity resolution and human review

## Implemented

Extended the existing investigation workspace with a Resolution review queue. Original mentions Rahul Kumar Sharma / R.K. Sharma and Amit Verma / A. Verma are separate. The fixture now contains 42 entities, 43 relationships, 62 evidence records and 9 source collections. The Cycle 1 six-hop path and fixture Lead 17 remain available.

Normalization, candidate blocking, feature comparison and weighted recommendation run in the backend. Rahul's proposal scores 94.3/100 from name similarity, shared P101 and shared V02. Amit's proposal scores 16.5/100 with name evidence only. Both initially recommend REVIEW. Scores are visibly labelled as ranking scores, not probabilities. No recommendation automatically merges.

Confirm, Reject, Defer and Undo accept reviewer/reason, persist a timestamped decision, and expose the ordered history. Confirm projects 41 canonical entities; Undo restores 42. Alias search and entity details preserve original mention IDs and evidence. Active paths are recomputed after decisions.

## Technical decisions

- Retained React, Vite, Cytoscape, FastAPI, NetworkX and existing styling. No dependency added; no redesign.
- JSON remains the source of graph/evidence truth. A small SQLite table stores only decisions, with automatic idempotent initialization and transactional state checks. Explicit local reset leaves fixture and legacy files untouched.
- Source mentions and source relationship IDs are immutable. Projection redirects endpoints while returning original_source/original_target; nodes expose aliases and original_entity_ids. Evidence endpoints continue returning unchanged original records. Parallel relationships remain distinct to retain provenance.
- NFKC/case folding/punctuation normalization; surname plus first initial or shared phone blocks. Score = name similarity * 0.2 + exact shared phone * 0.6 + shared vehicle * 0.2. Missing identifiers contribute zero, not contradiction. YES threshold 0.99 with shared phone; REVIEW for shared phone or name similarity >=0.35; otherwise NO. Human action is always required.
- Canonical display record prefers longer normalized name, then stable ID. Path inputs accept original IDs and resolve them through the same projection as graph queries.
- Blank reviewer/reason is rejected (422); nonexistent proposals/decisions return 404; invalid or repeated undo and conflicting decisions return 409. Confirmed state must be undone before another decision. Rejected/deferred proposals may be reconsidered through a later logged decision.

## Files changed

Created: backend/resolution.py (models, pipeline, store, projection), backend/resolution_fixtures.py, backend/reset_resolution.py, frontend/src/components/ResolutionReview.tsx, tests/test_resolution.py, CYCLE-2.md, artifacts/cycle2/*.png.

Modified: backend/main.py, backend/demo_schemas.py, backend/generate_demo.py; generated entities.json, relationships.json, evidence.json, sources.json under backend/data/demo; frontend/src/api.ts, demoTypes.ts, components/NetworkWorkspace.tsx, components/InvestigationInspector.tsx, golden.css; tests/test_golden_flow.py; README.md. Fixture generation also rewrites events/leads identically. Existing legacy code, dependency locks, original database and earlier reports remain preserved. No Git metadata is present.

## Run commands

Existing setup continues to work; no new package installation is required. Fresh installation remains documented in README.md.

```powershell
cd 'Z:\XLab\New\Network Intel'
.\.venv\Scripts\python.exe -m backend.generate_demo
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Second terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm run dev -- --port 5173 --strictPort
```

Open http://127.0.0.1:5173/. Resolution DB defaults to backend/data/resolution.sqlite3. Optional VEIL_RESOLUTION_DB overrides its path. Explicit rehearsal reset: `.\.venv\Scripts\python.exe -m backend.reset_resolution`, then reload the browser. Regenerating fixtures does not reset human decisions; restart the backend after generation. Servers are already running at handoff.

## Validation

- `python -m pytest -q`: 25 passed (6 resolution, 13 golden-flow, 6 legacy cases). Tests isolate decision databases.
- Resolution tests cover normalization/blocking, phone and vehicle comparisons, name-only ambiguity, false-merge negative case, no automatic merge, confirm/reject/defer/undo, conflicts and validation, graph counts, aliases, original endpoints, unchanged evidence, canonical and restored paths, persisted state, idempotent initialization and reset.
- Original golden-flow tests still verify exact six-hop route, changed paths after edge removal, missing/disconnected entities, depth enforcement, evidence/lead retrieval and fixture determinism.
- `npm run typecheck`: passed. `npm run build`: passed. Existing approximately 676 kB bundle warning remains (214 kB gzip); final build has no CSS syntax warning. Two existing Python deprecation warnings remain.
- Application startup and the explicit reset command tested. Browser verified at 1366x768: proposals/features, source evidence/back navigation, confirm 42->41, alias search/canonical detail, undo 41->42, visible decision history, ambiguous-pair rejection, and retained Cycle 1 path/Lead 17/transaction evidence. Active six-hop path refreshed after undo.
- A Windows encoding error during a copy edit was corrected by restoring the component; the final type check/build and browser confirmation/undo passed afterward.
- No frontend test runner added. Browser checks are manual tool-driven interactions, not a checked-in automated browser suite. This cycle did not repeat fresh dependency installation because dependencies are unchanged; Cycle 1's fresh-setup checks remain documented.

## Limitations

Synthetic fixed-rule demonstration, not calibrated entity resolution. Shared phones/vehicles and common names can produce false matches; even YES requires human action. Two fixture candidates demonstrate the workflow, not population-scale accuracy. Reviewer identity is self-declared; no authentication or tamper-proof audit storage. Browser updates its own decisions immediately; another open browser must reload to observe external decisions. Evidence navigation resets an unsubmitted review reason. No ingestion, NER, automated lead detection or production deployment added. Lead 17 remains explicitly fixture-authored.

## Exact manual demo

1. Open Operation Trinetra. Show separate Rahul and R.K. Sharma nodes.
2. Click Resolution review. R.K. Sharma is selected; show REVIEW and 94.3/100, not a probability.
3. Scroll to Matching evidence. Show normalized names, exact shared P101 and V02 with weights. Open E-RES-01, show resolution-mentions.csv row 2 and the original R.K. Sharma excerpt, then Back to investigation.
4. Enter a reviewer/reason and Confirm. The graph drops to 41 canonical entities. The success message and decision history record the human action.
5. Search R.K. Sharma and press Enter. Rahul details show the alias, both original IDs and retained evidence.
6. Find the default Rahul-to-Vikram path. It still has six computed hops. Open Lead 17 and E-TX-01 to demonstrate the retained golden flow.
7. Return to Resolution review. Enter an undo reason, click Undo, and observe 42 entities and the restored R.K. Sharma node. The active path is recalculated and history includes the reversal.
8. Choose A. Verma in the queue. Show 16.5/100, no shared phone/vehicle, and separate entities. Reject or Defer with a reason; graph identities remain unchanged.

## Screenshots

- artifacts/cycle2/review.png — queue and separate nodes
- artifacts/cycle2/features.png — per-feature matching evidence
- artifacts/cycle2/source.png — original source mention
- artifacts/cycle2/canonical.png — canonical entity and retained alias
- artifacts/cycle2/decision.png — confirmation history and projected graph

## Definition of done

Satisfied: R.K. Sharma proposal visible and explained; confirmation changes graph identity; A. Verma is not automatically merged; Undo restores original entities; source mentions remain traceable; Cycle 1 flow remains functional. Browser rehearsal decisions were undone; both candidates are separate at handoff, with Rahul's confirm/undo history retained.
