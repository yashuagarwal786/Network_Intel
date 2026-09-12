# VEIL — cycle 1

A local, synthetic investigation prototype for the team's SIH26189 demo brief. VEIL produces evidence-backed leads, not accusations. This implementation does not claim official SIH validation or production readiness.

## Run (Windows PowerShell)

From `Z:\XLab\New\Network Intel`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m backend.generate_data
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm ci
npm run dev -- --port 5173 --strictPort
```

Open http://127.0.0.1:5173. Dependency installation requires internet; the installed demo requires no internet or external AI API. Python 3.11+ and Node 20.19+ recommended. The checked-in lock files record the tested dependencies.

## Architecture and boundaries

- React + TypeScript presents backend results; Cytoscape draws entities and evidence-backed relationships. Fixed visual positions keep the demonstration legible and repeatable. Paths are not fixed.
- FastAPI exposes `/api/case`, `/api/graph`, `/api/path`, `/api/evidence/{id}`, `/api/reviews`, `/api/audit`.
- NetworkX computes minimum-hop paths over the filtered graph. Traversal treats relationships as undirected associations; source arrows preserve record direction. Repeated call edges remain distinct. For parallel relationships, the lexicographically first edge is the deterministic path explanation. All chosen edges carry evidence IDs.
- `backend/intelligence.py` owns graph filtering, traversal, and the T01 temporal rule. No frontend analytical scoring. T01 requires three calls between the same directed SIM pair within 30 minutes, followed within 30 minutes by a transfer between their recorded holders. The candidate-call search is bounded to the preceding hour. A changed timestamp or missing qualifying call changes the result.
- Every signal references exact synthetic source excerpts and locations. Excerpts in JSON are the canonical source records, not claims of access to separately uploaded files. All people, identifiers, organizations, and events are fictional.
- Inferred alias edges are excluded by default. Alias review records a decision but never merges identities or promotes an inference to a verified relationship.
- SQLite stores human decisions as separate audit rows. Previous decisions are preserved; there are no edit/delete endpoints. SQLite is introduced in this cycle because the requested review flow needs persistence.

## Exact judge walkthrough

1. Open the app; Operation Trinetra is the active fictional case. Select its sidebar card to return to Network at any time.
2. Select **Source records**. Inspect **Report**, **CDR**, **Transaction**, and **Vehicle** using the category dropdown. Open E005 and confirm its row, time, and unaltered excerpt. Close it.
3. Select **Alias review**. Inspect `A. Mehta ≈ Arjun Mehta`, the stated uncertainty, E001 and E013. Optionally save **Inconclusive** with a reason.
4. Select **Network**. Use **Find an entity** to inspect Arjun Mehta. Click a relationship on the graph or in the drawer to see its evidence.
5. Leave the path controls at **Arjun Mehta → DEMO-VH-07**, then select **Find path**. A four-hop route is computed by the backend. Open an evidence reference in the path explanation.
6. Select **Filters**. Try relationship **call** and recompute to show a truthful no-path result. Restore **All relationships**. Inferred links are opt-in and dashed.
7. Select **Leads**, then **Calls followed by a transfer**. Inspect three calls, a 16-minute gap before the transfer, and record-based holder connections.
8. Open references in each of the three signals. Read the benign alternatives and limitations. Scroll the lead drawer to Human review.
9. Choose **Follow up on lead**, enter `Check whether this payment relates to an ordinary delivery.`, then **Save review decision**.
10. Select **View audit trail** in the success banner. Confirm target, decision, reason, reviewer label, and timestamp. Reload to confirm persistence.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run build
```

The backend tests use temporary databases and do not modify demo reviews. Browser QA outcomes and screenshots are recorded in `CYCLE-1.md` and `artifacts/`.

## Limitations

- One case, 10 entities, 13 evidence records; JSON canonical excerpts only. No PDF/OCR parsing, ingestion pipeline, entity extraction model, or live connectors.
- T01 is a deterministic, explainable heuristic, not a trained or validated AI model. No accuracy/recall claims, guilt probabilities, centrality-based leadership, criminal community labels, or link prediction.
- The alias candidate is a supplied synthetic candidate, not automated entity resolution. Accepting it does not merge entities.
- No authentication. `Demo reviewer` is a session label, not a verified identity. Audit history is persistent but is not cryptographically tamper-evident or a legal chain of custody.
- Local development delivery only; no public hosting or production hardening. Graph and lead filtering are separate: graph filters do not recompute the case-wide lead rule.
- Dates filter relationship records by their recorded timestamp; this is not a reconstruction of relationship validity over time.
- Source reliability and identity are unverified. No real-world inference or action should be based on this fictional dataset.

## Cycle 1 definition of done

The ten-step walkthrough is runnable locally; analytical computations are backend-owned; paths respond to graph changes; every relationship and signal has resolvable evidence; human reviews persist and are auditable; build and backend tests pass; browser screenshots document the target layout. See `CYCLE-1.md` for actual verification and remaining issues.

Implementation references: [Cytoscape.js documentation](https://js.cytoscape.org/) and [FastAPI testing documentation](https://fastapi.tiangolo.com/tutorial/testing/).
