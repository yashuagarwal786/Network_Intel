# Cycle 4 — temporal signals and computed lead generation

## 1. Implemented

Lead 17 is generated on demand by temporal-leads-v1 from event records and the current graph projection. The active API never reads a fixture lead. The historical leads.json now contains an empty items array; the generator no longer authors explanations or leads. If conditions fail, the inbox is empty and GET /api/leads/17 returns 404, rather than substituting a fixture.

The default case computes four signals: historical median 2 calls/day versus 11 current calls; 7 recipients absent from the baseline; 3 connected transfers totalling INR 195,000 across 75 minutes within a 90-minute window; and an actual 6-hop path containing P101 and accounts A17/A31. A44 remains explicitly outside the returned shortest path.

The inbox filters by priority, shows generation time, categories and UNREVIEWED status, and offers Re-run engine. Lead detail explains what, when, who, why and uncertainty. Each signal expands its calculation, threshold, observed/expected values and exact evidence. Show computed signal path highlights the actual returned path without adding a relationship.

## 2. Technical decisions and priority policy

- New typed signal and lead models are separate from graph storage. No anomaly model, external API, new dependency or UI redesign.
- Baseline: seven complete IST calendar days before the event day; outgoing call records; missing dataset days count as zero. At least three days must contain observed calls before a communication signal is eligible. This is a conservative record-coverage gate, not proof that the dataset is complete.
- Current window: event-day midnight through the case analysis timestamp, inclusive. For the demo this is 15 August 2026, 00:00–20:00 IST. The replay clock is also generated_at, explicitly labelled in the UI; repeated requests do not invent a new wall-clock generation time. IST is fixed UTC+05:30 for these controlled 2026 datasets.
- Communication burst: current count >= max(5, 3 * historical median). Demo threshold is 6, observed 11. New-contact burst: at least 3 distinct current recipients outside the baseline recipient set; demo observes 7. These share one COMMUNICATION category.
- Financial sequence: at least 3 distinct transfer records in a weakly connected account component inside an inclusive 90-minute sliding window. Amounts use Decimal. Strict-subset duplicate windows are suppressed. Total is transfer volume, not distinct funds or a crime classification. Imported transaction IDs are preserved; the original golden dataset uses canonical event record IDs where no external transaction ID exists.
- Correlation: the case's selected investigation endpoints are traversed using NetworkX, maximum 8 hops. The triggering phone and at least 2 accounts from the sequence must occur on that path. At least one triggering phone call must be within 90 minutes of the transfer interval. All path and signal references must resolve to source evidence. No new graph edge is inferred.
- GRAPH_CONTEXT adds a priority category only when the path includes separately cited USES/USED_BY/CONTROLS/CONTROLLED_BY evidence beyond the communication/transfer rows. These are distinct operational evidence checks, not a claim of statistical independence.
- HIGH: at least 3 categories with complete evidence, temporal proximity and bounded connectivity. MEDIUM: 2 qualifying categories. LOW describes an isolated category requiring context; this engine deliberately does not create a lead for that alone, consistent with the multiple-category requirement. Standalone signals remain available at the signals endpoint.
- Review status starts at UNREVIEWED. This cycle does not implement lead-review decisions; Cycle 2 identity decisions remain reversible and persisted. Lead display IDs are assigned deterministically from 17 after sorting qualifying candidates. No ID guarantees that a lead will be generated.
- Processed Cycle 3 CDR and transaction rows now feed the same event model. The default four intake samples are from a different day and do not supply the planted complete baseline. Their absence of a HIGH lead is expected. Golden Lead 17 uses the original synthetic event/evidence records, with its explanation computed afresh.

Required disclaimer: “Review priority determines examination order. It is not a probability of criminal activity.”

## 3. Files changed

Created:

- backend/lead_models.py, lead_engine.py, temporal_validation.py
- frontend/src/leadTypes.ts, components/LeadDetail.tsx
- tests/test_lead_engine.py
- demo-data/temporal-validation/ground-truth.json and materialized primary_with_benign, alternate_seed_22, benign_only datasets (entities, relationships, events, evidence and sources JSON)
- artifacts/cycle4/evaluation.json, cycle4-lead.png, cycle4-calculation.png; CYCLE-4.md

Modified:

- backend/main.py: computed lead endpoints/counts and standalone signals endpoint
- backend/demo_schemas.py: removed fixture lead contracts, Decimal event amounts and optional transaction IDs
- backend/demo_repository.py: no lead fixture loading or fallback
- backend/generate_demo.py and backend/data/demo/leads.json: removed authored lead output
- backend/intake_store.py: event adapter for valid parsed CDR/transaction records
- frontend/src/api.ts, demoTypes.ts, components/NetworkWorkspace.tsx, components/InvestigationInspector.tsx, golden.css
- tests/test_golden_flow.py: assertions use the new computed contract
- README.md: current setup, architecture, policy, validation and walkthrough

Existing legacy modules, source fixtures, resolution/intake databases, dependency locks and prior cycle reports remain preserved. The directory has no Git metadata; no commit was created.

## 4. Run commands

No new installation required. Existing servers run on 8000 and 5173.

```powershell
cd 'Z:\XLab\New\Network Intel'
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Second terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm run dev -- --port 5173 --strictPort
```

Recreate the labelled validation files and evaluation artifact without changing the live dataset:

```powershell
.\.venv\Scripts\python.exe -m backend.temporal_validation
```

GET /api/cases/demo/leads recomputes and returns leads, signals, diagnostics, engine version and replay generation time. GET /api/leads/{lead_id} returns a currently qualifying lead or 404. GET /api/cases/demo/signals exposes computed standalone signals. All existing case/graph/path/evidence/intake/resolution routes remain available.

## 5. Tests, build and synthetic evaluation

- Pytest: 53 passed, including the previous 43 regressions and 10 engine tests. Covers calendar baseline/zero days, bursts/new contacts, inclusive transaction-window boundary, connectivity, path depth, temporal separation, category priority, missing evidence, no fixture fallback, order invariance, changed inputs, benign controls, alternate data, and intake event integration.
- Type check: passed. Production build: passed, approximately 687 kB JavaScript / 217 kB gzip. Existing bundle-size warning and two Python dependency deprecation warnings remain.
- Browser at 1366x768: computed lead opens; all four signal expanders and evidence links work; the graph signal highlights its six-hop path; MEDIUM filter shows an empty result; HIGH restores Lead 17; re-run succeeds with unchanged values. Existing workspace and evidence drawer remain usable alongside the graph.
- No new frontend test runner was added. Native browser checks are tool-driven interactions. No fresh dependency install repeated because dependencies are unchanged.

| Labelled dataset | Expected signals found | False leads | Missing leads | Evidence trace coverage | Expected priority | Repeatable |
|---|---:|---:|---:|---:|---|---|
| Primary + benign outlier | 4/4 | 0 | 0 | 58/58 references | HIGH | Yes |
| Alternate seed 22 | 4/4 | 0 | 0 | 68/68 references | HIGH | Yes |
| Benign-only control | 1/1 | 0 | 0 | 51/51 references | No lead | Yes |

The alternate seed has a median of 3 calls/day, 14 current calls, 6 new contacts and INR 90,000 across 80 minutes. It is not a renamed copy of the primary metrics. All variants contain a labelled benign P314 communication outlier. The ground-truth manifest is separate from engine output; false/missing lead counts preserve multiplicity. Evaluation verifies repeatable full serialized outputs. These results describe the planted synthetic cases only, not real-world accuracy, sensitivity or calibration.

## 6. Limitations

Small controlled datasets, fixed thresholds, outgoing-call definition, case-scoped path endpoints and incomplete-source uncertainty. Graph associations are not proof of chronology, causation or common operators. Source assertions remain unverified. Multiple overlapping transfer windows that are not strict subsets may yield separate candidates. Different records are not assumed to be semantically deduplicated. Generation uses an explicit replay clock. No scientific risk/probability model, automatic accusations, production scale claim, or new lead-review persistence.

## 7. Exact manual demo

1. Open Operation Trinetra. Keep Rahul Kumar Sharma and Vikram Singh as the path endpoints; click Find path to show the original six-hop route.
2. Click Open Lead 17. Show COMPUTED, HIGH, UNREVIEWED, replay generation time and the required disclaimer.
3. Read What happened: median 2, observed 11, 7 new contacts, 3 transfers, INR 195,000, 75 minutes. Show When and the three-category priority explanation.
4. Expand “2 calls/day → 11 calls”. Show the seven daily counts, median calculation and threshold, then open E-BASE-08-0. Back to investigation; expand again and use +22 more to reach event-day CDR evidence if desired.
5. Expand “7 contacts new to the baseline”. Inspect observed recipient sets and open its evidence.
6. Expand “3 connected transfers · ₹1,95,000”. Show the addition, 75 elapsed minutes and configured 90-minute window; open E-TX-01.
7. Expand the 6-hop graph signal. Show that only A17 and A31 are on this path, open E-ACC-01, then Show computed signal path. A44 is not falsely placed on it.
8. Set the inbox filter to MEDIUM: no matching leads. Restore HIGH and click Re-run engine; the same inputs return the same calculations.
9. Open artifacts/cycle4/evaluation.json to show the alternate metrics and benign non-lead results. Existing Data intake and Resolution review remain available.

## 8. Screenshots

- artifacts/cycle4/lead.png — computed lead beside highlighted path
- artifacts/cycle4/calculation.png — expanded baseline calculation and evidence references

## 9. Definition of done

Satisfied: Lead 17 is computed, its displayed analytical values come from backend calculations, each signal opens exact evidence, benign unusual activity does not automatically produce HIGH, repeated results are deterministic, and Cycles 1–3 regressions pass. Synthetic evaluation is explicitly limited to the labelled datasets.
