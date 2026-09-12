# VEIL current-product alignment audit

Date: 2026-09-09

## Scope

Running local production build at 1366x768, reviewed against the proposed five-day SIH 26189 MVP and a three-minute judge flow. This was a read-only audit; no product code or state was deliberately changed.

## Overall verdict

- Functional alignment with the recommended MVP: 88%.
- Judge-demo readiness: 82%.
- Evidence, explainability and human-control design: 95%.
- Visible graph-intelligence breadth: 68%.

The product is already stronger than a typical upload-to-graph prototype. Its primary remaining problem is not missing backend depth. The default network view reveals the Rahul-to-Vikram corridor before `Find Path`, weakening the intended discovery moment. The interface also gives several secondary surfaces equal visual importance in a three-minute demonstration.

## Observed flow

1. Landing page — Healthy, but optional for the judge demo.
   - Clear evidence-led positioning and synthetic-data disclosure.
   - It adds time without proving the investigation workflow.

2. Case overview — Healthy.
   - Shows source, entity, relationship, pending-review and lead counts.
   - Strong next-action cards make the human workflow understandable.

3. Data Sources — Strong.
   - Four controlled types, validation state, rejected row, extracted mentions and withheld claims are visible.
   - Exact manifests and report extraction are available.

4. Entity Resolution — Excellent.
   - Original mentions, feature weights, evidence, limitations and human decision are presented together.
   - Score is explicitly separated from probability; original evidence is preserved.

5. Network before path — Functionally strong, demo-story risk.
   - Search, typed graph, path selectors, zoom, filters and evidence inspector exist.
   - The focused default graph already shows the complete Rahul–Vikram corridor, so the reveal is visually spoiled.

6. Path result — Excellent implementation, weakened contrast.
   - Six hops, eight evidence references, 100% evidence coverage, dimmed unrelated records and an inspectable signal corridor.
   - The path is association-based and caveated appropriately.

7. Source evidence — Excellent.
   - Exact file, row, timestamp, fields, excerpt, entities and relationship are traceable.
   - This is the product's clearest trust advantage.

8. Lead Inbox and explanation — Strong.
   - Review priority is separated from criminal probability.
   - Communication, financial and graph-context calculations plus uncertainties are available.
   - The list uses many filters despite only one demo lead, creating unnecessary first-round visual weight.

9. Timeline — Strong but dense.
   - Observed events, claims, analytical signals and actions are explicitly separated.
   - Long event cards make the important call-to-transfer sequence harder to understand at a glance.

10. Audit trail — Present and valuable, not essential to the first three-minute flow.

## Alignment matrix

| Recommended capability | Current state | Alignment |
|---|---|---:|
| Structured and unstructured ingestion | CSV/TXT controlled ingestion, validation and provenance | 95% |
| Entity/relation extraction | spaCy NER plus deterministic extraction and withheld-claim handling | 90% |
| Human-reviewed entity resolution | Weighted proposals, evidence, confirm/reject/defer/undo and history | 100% |
| Evidence-backed graph | Typed nodes/edges and resolvable evidence | 100% |
| Graph exploration | Search, filters, node/edge inspector, path controls | 90% |
| Hidden connection discovery | Bounded NetworkX shortest path with evidence | 95% functional / 65% demo impact |
| Explainable intelligence | Decomposed signal calculations and limitations | 95% |
| Temporal pattern | Deterministic call-burst, new-contact and transfer sequence | 100% |
| Investigator action | Lead review, resolution decisions and audit history | 100% |
| Centrality/community intelligence | Not exposed in the active product | 25% |
| Relationship-strength explanation | Evidence coverage exists; no decomposed relationship-strength score | 45% |
| Investigation summary/export | Case overview exists; no concise reviewed summary export | 55% |

## Highest-impact refinements

### P0 — Fix before the internal hackathon

1. Preserve the reveal.
   - Default Network view should show two visually separate clusters or a broad case view where the Rahul–Vikram route is not obvious.
   - After `Find Path`, animate/focus only the six-hop corridor and display: `No direct relationship. One evidence-backed indirect path found.`

2. Add one judge-mode CTA on Case Overview.
   - Label: `Investigate hidden connection`.
   - It should open Network with Rahul/Vikram preselected but without computing or exposing the path.

3. Make the lead title human-readable.
   - Replace date-led copy with `Communication burst followed by connected transfers`.
   - Keep date as metadata.

4. Turn Timeline into a compact sequence for the selected lead.
   - For the demo, show four milestones: baseline, call burst, transfers, report/event.
   - Keep the full event register behind `View all events`.

5. Rehearse a workspace-first demo.
   - Start on Case Overview, not the marketing landing page.
   - Recommended sequence: Overview → Data Sources → Resolution → hidden path → exact evidence → lead explanation.

### P1 — Build only after P0 is stable

6. Add one bridge insight, not an analytics laboratory.
   - Compute betweenness centrality on person nodes or the relevant projected graph.
   - Show a single card: `Amit Verma connects otherwise separated record clusters` with methodology and caveat.
   - Do not equate the score with leadership or guilt.

7. Add a minimal community cue.
   - Colour two detected/manual demo communities before path discovery.
   - Explain that communities are dense record clusters, not identified gangs.

8. Add relationship evidence strength only if fully decomposed.
   - Inputs: independent source count, interaction frequency, identifier certainty and recency.
   - Label it `Evidence strength`, never `criminal risk` or probability.

9. Add a one-screen investigation summary.
   - Confirmed observations, reviewable leads, unresolved identity decisions and explicit limitations.
   - Export is optional; the screen itself matters more.

### P2 — Do not prioritize now

- Neo4j migration.
- GNN/link prediction.
- RAG or chat interface.
- More anomaly models.
- PDF/OCR unless requested by the internal-hackathon rubric.
- Authentication beyond a clearly explained production architecture.
- Additional landing-page polish.

## UX and accessibility risks visible in the run

- Several secondary labels and metadata lines are very small and low contrast at 1366x768.
- Purple, rose and muted-grey text on near-black backgrounds may fail normal-text contrast; measure with an automated contrast tool.
- Graph canvas itself is not a sufficient accessible representation, although path selectors and the signal corridor provide a strong alternative.
- Timeline and resolution screens are information-dense; 200% zoom and keyboard-only reflow still need explicit verification.
- Date fields expose browser-native controls; labels are present, but keyboard and screen-reader behavior was not fully tested in this screenshot-led audit.

## Recommended three-minute flow

1. Case Overview — 15 seconds — explain fragmented sources and investigator control.
2. Data Sources — 20 seconds — show four types, one rejected row and source provenance.
3. Entity Resolution — 25 seconds — show why a candidate is not auto-merged.
4. Network before reveal — 15 seconds — state there is no direct Rahul/Vikram edge.
5. Find Path — 35 seconds — reveal corridor and identify the intermediary.
6. Exact Evidence — 25 seconds — open the transaction row and one CDR record.
7. Lead Explanation — 30 seconds — show call burst, transfers, graph context and alternative explanation.
8. Architecture/close — 15 seconds — evidence to inference to human review.

## Evidence limits

The audit verified the local running UI, API-backed screens, 101 backend tests, TypeScript type checking and a production frontend build. Screenshot inspection alone cannot establish full WCAG compliance, real-world analytical validity, production security, multi-user scale or performance on agency-sized datasets.
