# Cycle 1 — runnable evidence-to-review slice

Status: definition of done satisfied for the bounded synthetic cycle. Verified 4 September 2026. The full SIH product is not complete; see limitations below.

## 1. Implemented

Operation Trinetra opens directly in a restrained investigator workspace. The source register contains reports, CDRs, transactions, and vehicle records. A supplied alias candidate exposes uncertainty and exact evidence. Cytoscape renders 10 typed entities and 12 recorded relationships, with a thirteenth inferred alias relationship available by explicit opt-in. NetworkX computes filtered shortest paths. T01 computes a temporal lead from three calls followed by a transfer. Human decisions persist in SQLite and appear in the audit trail.

## 2. Technical decisions

The workspace was empty; no existing code was replaced. React/TypeScript, Cytoscape, FastAPI, NetworkX, JSON fixtures, and SQLite follow the requested stack. Backend intelligence is separate from API and frontend code. Fixed graph positions are presentation only. All relationships and lead signals resolve to evidence IDs. The lead is computed rather than a fixture lead. Alias review does not merge entities. Undirected association paths preserve source direction in each cited relationship. All dates are displayed in IST. No API keys, external AI, trained models, production authentication, or public hosting are required.

## 3. Files created

- `.gitignore`, `README.md`, `CYCLE-1.md`, `requirements.txt`, `requirements-lock.txt`
- `backend/__init__.py`, `backend/main.py`, `backend/intelligence.py`, `backend/generate_data.py`, `backend/data/trinetra.json`
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/index.html`
- `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/Graph.tsx`, `frontend/src/types.ts`, `frontend/src/style.css`
- `tests/test_backend.py`
- Four screenshots in `artifacts/`

Generated and ignored: `.venv`, frontend dependencies/build output, Python caches, SQLite review database, TypeScript build cache. Two QA-labeled review entries were intentionally retained in the local demo database as examples.

## 4. Run commands

Dependencies are already installed on this machine. From the workspace root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm run dev -- --port 5173 --strictPort
```

Open `http://127.0.0.1:5173`. Both servers were left running at delivery. Fresh setup commands are in README.md.

## 5. Tests/builds executed

- `python -m pytest -q`: **6 passed**, including evidence integrity, graph path changes on edge removal, inferred-link filtering, invalid/empty paths, temporal negative cases, review validation, non-merging alias decisions, and database persistence. Tests use temporary databases.
- `npm run build`: **passed**, TypeScript check and Vite production build. Final main bundle approximately 670 kB / 213 kB gzip. Vite warns about a chunk over 500 kB; not a build failure.
- Two dependency deprecation warnings from Starlette/HTTPX and AnyIO remain; no test failures.
- Package downloads initially failed with intermittent DNS/connection resets. Retrying completed successfully; both dependency lock files are present.
- Live `/api/path` returned four hops and source references. Live API and frontend returned successful responses. Reviews remained after backend restart.
- Browser QA at **1366×768** and **1280×720**. Verified source filters: 5 report, 3 CDR, 3 transaction, and 2 vehicle records. Inspected exact source excerpts and locators.
- Verified direct graph node click, entity selector, relationship inspector, computed four-hop path, restrictive-filter no-path error, and inferred opt-in changing relationship count from 12 to 13.
- Opened a source for each lead signal category, submitted an alias review and a lead review, and verified audit content after reload.
- Keyboard check: Shift+Tab at the first evidence-modal button wraps to the last button; Escape closes the modal.
- Development hot reload exposed duplicate React root warnings. Separating the App component from the entrypoint fixed the source; no new error/warning logs appeared during the final reloaded interaction check. This does not claim exhaustive browser compatibility or accessibility certification.

## 6. Known limitations

One synthetic case only. Canonical JSON source excerpts rather than uploaded file parsing. Supplied alias candidate rather than automated entity resolution. One deterministic heuristic rather than a validated AI model. No OCR, ingestion pipeline, precision/recall evaluation, live sources, login, production authorization, or tamper-evident audit chain. Graph filters do not scope the case-wide lead rule. Relationships use record timestamps, not reconstructed validity periods. Review decisions are listed in history; cards do not yet show a consolidated latest-review status. The review drawer scrolls at laptop sizes. Browser QA was manual and targeted, not an automated regression suite.

## 7. Exact manual demonstration

1. Open the local URL; click the Operation Trinetra case card.
2. Open Source records and select Report, CDR, Transaction, then Vehicle in the type filter. Open E010 and inspect its row and excerpt; close it.
3. Open Alias review; inspect A. Mehta / Arjun Mehta, E001 and E013, and the uncertainty explanation.
4. Return to Network; select Arjun Mehta using the entity selector or graph node. Select listed phone to inspect its cited relationship.
5. Use default endpoints Arjun Mehta and DEMO-VH-07; click Find path. Inspect the four-hop result and evidence for each relationship.
6. Optional negative check: Filters → relationship call → Find path. Read the no-path result; restore All relationships.
7. Open Leads → Calls followed by a transfer. Read the three-call signal, 16-minute gap, and recorded holder connections.
8. Open E005, E008, and E003 from their respective signals. Review the benign alternatives and limitations.
9. Scroll the drawer to Human review. Select Follow up on lead and enter `Check whether this payment relates to an ordinary delivery.` Click Save review decision.
10. Click View audit trail. Verify decision, rationale, target, reviewer label and timestamp. Reload and reopen Audit trail to confirm persistence.

## 8. Screenshots

- `artifacts/legacy-ui/network-path-1366.png`: final computed path and relationship evidence inspector.
- `artifacts/legacy-ui/evidence-1366.png`: exact vehicle source excerpt.
- `artifacts/legacy-ui/audit-1366.png`: two saved QA decisions.
- `artifacts/legacy-ui/network-1280.png`: smaller laptop layout.

## 9. Definition of done

**Satisfied for cycle 1.** The complete ten-step controlled demonstration was exercised; computations are backend-owned, provenance is resolvable, reviews persist, and tests/build pass. No claim is made that this implements all capabilities of an AI criminal-network analysis system or guarantees SIH selection.
