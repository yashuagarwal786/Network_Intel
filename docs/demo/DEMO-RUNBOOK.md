# VEIL: local judge demonstration

Synthetic Demonstration Data only. VEIL generates leads, not accusations. The complete visible-browser rehearsal took **107.054 seconds**, excluding spoken narration. The narration schedule below is a target, not a measured recording.

## Fresh setup

Tested on Windows with Python 3.14.6, Node 24.16.0 and Microsoft Edge. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe -m backend.serve_demo --reset --port 8000
```

Open [VEIL](http://127.0.0.1:8000/). One local process serves the production UI and API. No API key or manual database setup is required. Dependency installation needs internet or a populated cache; the installed application requires no external network service, fonts or AI API.

For a subsequent start that preserves decisions:

```powershell
.\.venv\Scripts\python.exe -m backend.serve_demo --port 8000
```

For a fresh rehearsal, stop that server with Ctrl+C in its own terminal, then run the launcher with `--reset`. Do not reset a running server or start another server on the same port. Reset archives the three dedicated rehearsal databases under `backend/data/rehearsal/archives`, restores the four processed files, and clears rehearsal decisions. Original databases from previous cycles remain separate. An explicit rehearsal reset is an administrative operation; normal application audit history is append-only.

Standalone seed/reset, with the server stopped:

```powershell
.\.venv\Scripts\python.exe -m backend.prepare_demo --reset
```

Initialization is idempotent. Analytical inputs and results are repeatable; operational audit timestamps and decision IDs are not fixed. For frontend development, keep this backend running and use `npm run dev -- --port 5173 --strictPort` from `frontend`; Vite proxies API requests to port 8000.

## Exact judge flow and recording script

Use a 1366×768 browser viewport at 100% zoom. Reset before recording. The four files are already processed so ingestion is not a live setup dependency.

| Step | Action | What to demonstrate |
|---|---|---|
| 1 | Open `http://127.0.0.1:8000/` | Operation Trinetra, Active Review, synthetic-data notice. |
| 2 | Click **Data Sources** | Four processed sources: report, CDR, transactions, vehicle records. One intentionally invalid CDR row is clearly rejected. |
| 3 | Click **Continue to resolution review** | R.K. Sharma proposal is REVIEW; original mentions are separate. |
| 4 | Inspect name, exact phone and vehicle evidence; enter reviewer and reason; click **Confirm** | The score is not a probability. Confirmation creates a reversible canonical projection. A. Verma remains ambiguous. |
| 5 | Click **Network** | Distinct entity types, relationship direction and evidence legend. |
| 6 | Search `Rahul`, press Enter | Canonical Rahul and confirmed alias appear in the inspector. |
| 7 | Select Rahul Kumar Sharma as Path start and Vikram Singh as Path end; click **Find path** | Backend computes six hops, with maximum depth eight. |
| 8 | Inspect the highlighted route | Unrelated elements dim; every path relationship has an evidence link. |
| 9 | Click **Open Lead 17** | Generated review lead, HIGH examination priority, explicit disclaimer. |
| 10 | Expand communication and connected-transfer signals | Median 2 calls/day, 11 event-day calls; three transfers totalling ₹1,95,000 over 75 minutes within the configured 90-minute window. |
| 11 | Click **Open evidence E-TX-01** within the transfer signal | Exact source filename, Row 2, timestamp, raw excerpt and verification status. |
| 12 | **Back to investigation** → **Record investigator review**; enter reviewer, select **Needs more evidence**, add reason; **Review submission** → **Confirm submission** | Persisted human decision; no accusation or automatic enforcement. |
| 13 | Click **Audit Trail**, filter action to **LEAD REVIEW SUBMITTED**, then **Apply filters** | Actor, reason and UNREVIEWED → NEEDS_MORE_EVIDENCE transition. |

Suggested recording allocation: 0:00–0:20 case/sources; 0:20–0:55 resolution; 0:55–1:20 search/path; 1:20–2:00 signals; 2:00–2:20 evidence; 2:20–2:45 review/audit. Leave fifteen seconds of slack. Use an existing OS screen recorder, keep notification popups out of the frame, and capture the whole workspace. A narrated recording has not been produced or timed.

Optional follow-up: Timeline → event type `transfer` → entity `Account A17` → open E-TX-01. Resolution → enter an undo reason → Undo restores the original mentions as separate graph entities. These are outside the three-minute core script.

## Checks

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run lint
npm run typecheck
npm run build
npm test
```

The smoke runner uses installed Microsoft Edge and an isolated local server on port 8001, with separate `backend/data/smoke` databases. Port 8001 must be available. Build before testing: the smoke server serves `frontend/dist`. This Windows browser configuration was tested; other OS/browser configurations were not.

## Fallback package

- [First-round evidence package](../../artifacts/first-round/index.html): final Midnight Evidence Lab screenshots and captured API results.
- [Technical evidence brief](../sih/SIH-FIRST-ROUND-EVIDENCE.md), [scope freeze](../sih/SIH-SCOPE-FREEZE.md) and [judge Q&A](../sih/SIH-JUDGE-QA.md).
- [Screenshot gallery](../../artifacts/cycle6/index.html): static, local reference images; not an interactive replacement for computation.
- [Cycle report](../cycles/CYCLE-6.md) and [screen audit](../audits/CYCLE-6-AUDIT.md).
- [Sample API exports](../../artifacts/sample-api/): ten captured responses, including computed path, generated lead, evidence and audit. The UI does not load these as hidden fallbacks.

Refresh exports while the local server is running:

```powershell
.\.venv\Scripts\python.exe -m backend.export_demo --base-url http://127.0.0.1:8000
```

Evidence and lead access are audited, so exporting those endpoints creates access entries. If a live demo cannot run, label screenshots and JSON explicitly as previously captured results.

## Boundaries to explain candidly

One synthetic case and controlled parsers, not universal document understanding. Imported records coexist with the original canonical fixtures; matching names do not silently merge them. Source-file count and evidence-register collection count therefore differ. The graph layout is deterministic presentation; NetworkX calculates paths, and the backend lead engine calculates signals. A graph path does not establish a new factual relationship. Reviewers are self-declared; the audit is not cryptographically tamper-resistant. Full-network exploration needs pan/zoom. No claim of real-world detection accuracy or calibrated probability is made.
