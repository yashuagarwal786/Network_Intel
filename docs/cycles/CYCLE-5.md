# Cycle 5 — human review, timeline and audit trail

## 1. Implemented

The investigator can review Lead 17, choose any of the six requested actions, supply a reviewer and optional reason, inspect a confirmation step and submit. The inbox and detail show the persisted status. Review history retains previous decisions. The tested live decision is NEEDS_MORE_EVIDENCE, submitted by Demo investigator; it survived a page reload and backend restart.

The audit journal records source upload/processing/reset, entity-resolution decisions and undo, lead generation/opening, evidence opening and lead review submission. Each entry includes actor/type, affected object, previous/new states, reason and wall-clock timestamp. Audit filters support date range, action, actor and object ID (object ID is API-only).

The timeline combines calls, transactions, reports, vehicle observations, extracted claims, analytical signals and human/system actions. Date/time, event type, entity, source type and record-category filters run on the backend. Cards open exact evidence in the existing drawer. Clicking an entity on a card filters the timeline. Original mentions and confirmed canonical identities are matched when filtering.

## 2. Technical decisions

- No new algorithms, dependencies, ORM or redesign. New storage is backend/data/investigator_journal.sqlite3; VEIL_REVIEW_DB can override it. Existing legacy reviews.sqlite3 is not used. Initialization rejects an incompatible legacy review schema without changing its records.
- A lead review and its audit event commit in the same SQLite transaction. Idempotency keys return the original review on an identical retry; reused keys with different content return 409. Concurrent duplicate requests are serialized by BEGIN IMMEDIATE. The UI disables submission while saving and has an immediate in-memory submission lock.
- Reviews carry a content revision of the computed lead. A changed lead cannot silently inherit the previous revision's decision. Stale submissions return 409; earlier reviews remain accessible. This content hash is an identity/version mechanism, not cryptographic audit protection.
- Lead generation is journalled once per case/content revision. Re-running identical analysis does not flood generation history. The engine's replay timestamp remains distinct from the actual audit generation timestamp.
- Source operations atomically append a pending audit record in their existing intake database. Idempotent reconciliation copies those records into the central journal, including after an interrupted request. Resolution audit reconciliation uses the existing durable decision history. Reading audit/timeline also reconciles pending records. No historical source operations predating Cycle 5 are fabricated.
- Normal APIs offer no audit update/delete. Intake reset preserves both its pending audit journal and central audit history. There is no cryptographic tamper resistance or authenticated actor identity. Evidence/lead detail GET requests record access by “Local demo session”; these indicate service access, not proof of human reading.
- VERIFIED_RELATIONSHIP requires an identified supporting relationship; INCORRECT_ENTITY_MERGE requires an involved, currently confirmed proposal. These record investigator assessments. They do not silently rewrite source verification flags or undo a merge; the existing reversible Resolution review flow performs undo.
- Observed source events remain unverified source assertions. Extracted claims retain polarity and uncertainty. Undated report claims remain undated and sort last; date-range filters exclude them. Analytical signals carry replay analysis time; human/system actions carry wall-clock time. All display timestamps use IST.

## 3. Files changed

Created:

- backend/review_store.py — typed inputs/reviews/audit events, revision identity and SQLite journal
- backend/activity.py — typed timeline projection and chronological ordering
- frontend/src/reviewTypes.ts
- frontend/src/components/LeadReview.tsx
- frontend/src/components/ActivityView.tsx
- tests/conftest.py — isolate review storage for every test
- tests/test_review_activity.py — 14 additional test cases
- CYCLE-5.md and artifacts/cycle5/audit.png, artifacts/cycle5/timeline.png

Modified:

- backend/main.py — required APIs, audited access, reconciliation and status projection
- backend/intake_store.py — transactional pending audit records
- backend/lead_models.py — review status/revision fields
- backend/lead_engine.py — wording now acknowledges separately recorded human assessment; calculations unchanged
- frontend/src/api.ts, leadTypes.ts
- frontend/src/components/LeadDetail.tsx, InvestigationInspector.tsx, NetworkWorkspace.tsx
- frontend/src/golden.css — review/activity styling and laptop-height sidebar adjustment
- tests/test_golden_flow.py — active endpoint inventory
- README.md — setup and Cycle 5 walkthrough

Runtime journal files initialize automatically. Existing fixture data and legacy review records are preserved. No Git metadata exists, so no commit was created.

## 4. Commands

Both servers are running. To start them after stopping the existing processes:

```powershell
cd 'Z:\XLab\New\Network Intel'
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a separate terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm run dev -- --port 5173 --strictPort
```

Open http://127.0.0.1:5173/. No new installation or manual database setup is required. Fresh dependency setup remains in README.md; installation was not repeated this cycle because dependencies did not change.

New contracts:

- POST /api/leads/{lead_id}/reviews — reviewer, action, optional reason/object_id, idempotency_key and lead_revision from the current lead; returns persisted Review
- GET /api/leads/{lead_id}/reviews — chronological history, including earlier revisions
- GET /api/cases/demo/audit — start/end (timezone required), action, actor, object_id filters
- GET /api/cases/demo/timeline — start/end, event_type, entity_id, source_type, category filters

## 5. Verification

- `.\.venv\Scripts\python.exe -m pytest -q`: **67 passed**, including all 53 previous regression cases and 14 new cases. Two existing dependency deprecation warnings remain.
- `npm run typecheck`: passed.
- `npm run build`: passed. JavaScript 696.85 kB / 220.36 kB gzip; existing >500 kB bundle warning remains.
- New cases cover persistence, validation, identical/conflicting/concurrent retries, old/new state transitions, revision invalidation, generation deduplication, evidence access, resolution/undo, object assessments, intake audit recovery/reset retention, initialization, incompatible legacy storage, chronological ordering, case isolation and filtering.
- Browser at 1366×768: computed six-hop path, review preparation/confirmation, persisted NEEDS_MORE_EVIDENCE in inbox/detail after reload, audit action filter and previous/new states, timeline transfer/source/entity filters and E-TX-01 evidence opening verified.
- Restarted the live backend and re-read the original browser review: one persisted review, same review ID, NEEDS_MORE_EVIDENCE.
- Live QA caught and fixed a legacy database filename collision. Tests now explicitly cover incompatible legacy schemas. The original legacy review rows were not modified.
- No new frontend test runner or browser-console capture was added; browser verification used native tool-driven interactions and visible state. The narrated presentation was not timed this cycle.

## 6. Limitations

This is a local synthetic prototype with self-declared reviewers and no authentication. The audit journal is append-only through normal app behavior, not protected against direct filesystem/database edits. Timeline and audit results are unpaginated and intended for the controlled dataset. Repeated detail GET requests create repeated access entries. Explicit intake reset can make old intake evidence links unavailable until the same sample files are reloaded; journal entries themselves survive. Source observations and investigator assessments are not proof of criminal activity. No real-world accuracy claim is made.

## 7. Exact manual demo

1. Open Operation Trinetra. Keep Rahul Kumar Sharma and Vikram Singh selected and click Find path; show six computed hops.
2. Open Lead 17. Inspect a signal's calculation and evidence, then return to the lead.
3. In Record investigator review, enter a reviewer, select Needs more evidence and optionally enter a reason. Click Review submission, inspect the confirmation, then Confirm submission.
4. Show the saved message, updated inbox/status and Review history. Reload the page and reopen Lead 17 to demonstrate persistence. The live demo already contains one such review from validation.
5. Open Audit history, select LEAD REVIEW SUBMITTED under Action and Apply filters. Show the actor, reason and UNREVIEWED → NEEDS_MORE_EVIDENCE transition. Expand Previous / new state for exact stored values.
6. Open Timeline. Select transfer under Event type and Transaction under Source type; Apply filters. Extracted intake claims and base source events are labelled distinctly.
7. Select Account A17 under Entity. Open E-TX-01 from the first matching source event. Show filename, row 2, timestamp and exact transaction excerpt in the evidence drawer.
8. Clear filters and select LEAD REVIEW SUBMITTED to show the human decision as a timeline action. Audit history also records the evidence-open access.

## 8. Screenshots

- artifacts/cycle5/audit.png — persisted decision, actor, reason and state transition
- artifacts/cycle5/timeline.png — filtered transaction timeline and exact source evidence

## 9. Definition of done

Satisfied: Lead 17 can be marked Needs More Evidence; status updates and survives restart; audit records the decision; timeline distinguishes source/claim/signal/action categories and opens evidence; all earlier regression tests pass. Existing resolution, intake and computed lead algorithms remain active.
