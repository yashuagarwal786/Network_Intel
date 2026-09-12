# Network Intel — SIH Judge-Readiness Audit

Audit date: 6 September 2026  
Verdict: **READY FOR LOCAL JUDGE DEMO**

## Scope and evidence

- Inspected the React/TypeScript frontend, FastAPI backend, SQLite stores, fixture loader, ingestion/parser, NER, entity-resolution, graph/path, lead, behavioral anomaly, timeline, audit, and Vercel entry-point code.
- Ran the production frontend and backend locally and exercised Case Overview, Data Sources, Entity Resolution, Network, Inspector, Evidence, Lead Inbox, Timeline, and Audit Trail.
- Application tests: **101 passed**. Root `pytest.ini` now restricts discovery to `tests/`, so default `pytest` no longer collects vendored artifact dependencies.
- Frontend: TypeScript check passed, ESLint passed, production build passed. Bundle warning remains: JavaScript 754.04 kB minified / 234.52 kB gzip.
- Fresh runtime evidence: [current-audit.jpg](../../artifacts/network-intel-audit/current-audit.jpg).

## Implemented architecture

```text
Synthetic fixtures + uploaded TXT/CSV
                  ↓
         validation and parsing
                  ↓
 spaCy NER + regex/gazetteer extraction
                  ↓
 deterministic relationship templates ──→ unsupported/negated/uncertain claims retained only
                  ↓
 heuristic identity proposals ──→ mandatory human confirm/reject/defer
                  ↓
 canonical in-memory NetworkX MultiGraph
                  ↓
 bounded shortest path + temporal rules + Isolation Forest triage
                  ↓
 evidence-linked leads/signals (not accusations)
                  ↓
 investigator review + timeline + local SQLite journal
```

Frontend is a React 19 SPA using Cytoscape. The browser calls same-origin `/api` endpoints. FastAPI serves APIs and the built SPA. Base data is immutable JSON; uploaded state, identity decisions, and reviews are held in three SQLite databases. The graph is reconstructed in memory; there is no graph database.

## Capability truth table

| Capability | Classification | How it actually works / safe claim |
|---|---|---|
| Data Sources | Real for prototype | Four controlled synthetic source types plus bounded user upload. Every source has manifest/provenance metadata. |
| Document ingestion | Partially real | UTF-8 TXT reports and CSV for CDR/Transaction/Vehicle; 64 KiB/file and 16-file cap. No PDF/OCR/streaming connectors. |
| Parsing | Real, bounded | Schema validation and deterministic parsers; malformed rows are rejected and excluded. |
| Entity extraction | Real, hybrid | spaCy `en_core_web_sm` NER for person/org/location; regex for identifiers; gazetteer fallback/supplement. |
| Entity resolution | Real, simplified | Candidate blocking plus weighted name/phone/vehicle heuristics; no auto-merge; human decision, projection, provenance, and undo are implemented. |
| Relationship extraction | Partially real | Controlled deterministic templates. Negated, uncertain, and unsupported claims are retained but do not become graph edges. Not general open-domain relation extraction. |
| Graph generation | Real | Evidence-backed recorded relationships become a NetworkX `MultiGraph`, rebuilt from current projected data. |
| Find Path | Real | Dynamically computed bounded unweighted shortest path using NetworkX BFS, max 8 hops, deterministic tie ordering. |
| Graph filtering | Real UI behavior | Entity/relationship visibility controls operate on the loaded client graph; not a server-side query engine. |
| Evidence density | Real descriptive count | Inspector displays the number of source references. It is explicitly not a risk or guilt score. |
| Confidence score | Mixed | Entity-resolution score is a real weighted heuristic but not a calibrated probability. Network Inspector correctly shows N/A. No general relationship confidence model exists. |
| Evidence count | Real | Counts referenced evidence IDs; count measures quantity, not truth or independent verification. |
| Source verification | Partially real | Exact source, row/span, fields, timestamp, excerpt, and checksum are traceable. Synthetic records are explicitly not independently verified. |
| Inference relationships | Conservative | Analytical signals are separate; uncertain or inferred claims do not create graph edges. The current graph path uses recorded associations only. |
| Computed path summary | Real deterministic presentation | Human-readable text is derived from returned path values. It is not LLM-generated or generative AI. |
| Related Leads | Real for current rules | Derived by matching selected entities to deterministic computed leads. |
| Lead Inbox | Real, rule-based | `temporal-leads-v1` computes communication, new-contact, transfer, and graph-context signals. HIGH/MEDIUM/LOW is review order, not guilt/risk probability. |
| Behavioral Profiles | Real experimental ML | Isolation Forest over five engineered behavioral features. Unsupervised triage only; no real-world accuracy estimate or ground truth. |
| Timeline | Real projection | Chronological union of observed events, extracted claims, analytical signals, and human/system actions with filters. |
| Audit Trail | Partially real | Persistent local application journal with state transitions and provenance. No authentication and no cryptographic tamper resistance. |
| Signal Corridor | Real visualization | Mirrors the returned path node sequence and evidence count; it does not perform a separate analysis. |
| Inspector | Real UI | Resolves selected entity/path/evidence/lead details from loaded API data and uses evidence counts and path coverage instead of a risk label. |
| Search | Real client-side | Finds loaded entities and opens/focuses them; not full-text search across raw documents. |
| Case Overview | Real projection | Counts and next-step panels derive from current API state; case narrative is synthetic fixture content. |
| Synthetic dataset | Mock data, real pipeline | Fictional deterministic fixtures intentionally designed to exercise the workflow. The data is mocked; parsing, analysis, provenance, and review flows are implemented. |

## Hero workflow verification

Rahul Kumar Sharma → Vikram Singh succeeds at max depth 8 and returns a **6-hop** path:

`Rahul → P101 → P204 → Amit Verma → A17 → A31 → Vikram`

The six relationships are `USES`, `CALLED`, `USED_BY`, `CONTROLS`, `TRANSFERRED_TO`, and `CONTROLLED_BY`. The UI dims unrelated records, Signal Corridor matches the seven returned nodes, selecting Vikram updates the Inspector, and `E-ACC-02` opens the exact source `account-control-register.csv`, row 3, with excerpt and linked relationship `R06`. Max depth 5 returns `NO_PATH_WITHIN_DEPTH`; 8 succeeds. Source=target returns a valid zero-hop path. Missing entity returns `ENTITY_NOT_FOUND`; max depth 99 returns validation error. Tests also verify no-path, reverse path, isolated graph behavior, deterministic ties, and alternate paths when evidence-backed edges are removed.

Important truth: path discovery is dynamic, but it is an undirected association path—not a chronological flow and not proof of wrongdoing. Evidence references prove that a source record asserted each edge; they do not independently verify the assertion.

## Runtime, state, and adversarial findings

- Navigation and primary panels loaded without failed API calls or broken assets in the tested local run.
- Refresh preserves durable source/resolution/review data because it is in local SQLite. Selected view/entity/path state is primarily client state and should not be promised as durable across reload.
- Rapid requests are bounded by a 12-second client timeout and identical concurrent GETs are deduplicated. Mutations are not automatically retried.
- Review writes use revision/idempotency conflict protection; entity-resolution confirm and undo are covered by tests.
- Empty/no-result and validation states exist for path, lead filters, timeline filters, malformed ingestion, and missing endpoints.
- Duplicate IDs, unsafe filenames, invalid CSV headers, incomplete evidence, negated/uncertain claims, weak signals, false-merge negatives, zero-variance ML input, and insufficient ML sample size have dedicated passing tests.
- No authentication, authorization, encryption policy, multi-user tenancy, or secure secrets workflow is implemented. Reviewer names are user-entered labels.
- Hosted Vercel state uses SQLite files under `/tmp`; it is ephemeral and unsuitable for durable multi-instance persistence.
- Public URL returned HTTP 200 but its HTML title was still **“VEIL · Operation Trinetra”**, while the local build is **“Network Intel — Operation Trinetra”**. The public build is stale relative to the audited local build.

## Measured performance (local loopback, 20 requests each)

| Route | Median | p95 |
|---|---:|---:|
| Case | 15.15 ms | 28.64 ms |
| Graph | 23.55 ms | 31.40 ms |
| Rahul→Vikram path | 15.77 ms | 17.18 ms |
| Leads | 22.62 ms | 24.30 ms |
| Timeline | 41.01 ms | 47.39 ms |
| Behavioral anomalies | 179.21 ms | 264.14 ms |

The tested case currently contains 57 entity records and 52 sourced relationships. These numbers demonstrate prototype performance only. NetworkX BFS is O(V+E) for one traversal, but the app rebuilds/project the graph and serializes much of the case per request; Cytoscape also renders the graph client-side. No million-node claim is defensible. For production scale, use indexed durable storage, precomputed/cached projections, server-side subgraph queries, pagination, background jobs, and likely a graph-capable persistence/query layer.

The requested 1920×1080 and 1366×768 layouts have responsive artifacts in the repository from the current redesign cycle, and the live audit at the available 1280×720 viewport remained usable. However, because this audit run could not programmatically resize the in-app browser, those two exact viewport captures were not independently re-created in this pass; re-run the existing Playwright responsive checks immediately before the event.

## Verdict and ruthless priorities

### P0 — resolved before judges

1. **Resolved:** Inspector “Risk Index” labels were replaced with factual evidence-density and association-path labels.
2. **Deploy the audited Network Intel build and verify it on the actual demo URL.** The current public page still identifies itself as VEIL.
3. **Choose one demo persistence strategy.** Prefer the local/offline FastAPI build for judging. If using Vercel, do not demonstrate durable writes or claim persistence; `/tmp` state can reset.

### P1 — should fix

1. **Resolved:** root `pytest.ini` restricts discovery to the product suite and excludes artifact/vendor directories.
2. Rehearse and document the clean reset/seed procedure, then freeze the exact judge dataset and reviewer state.
3. Add authentication/role boundaries and durable production storage before any claim of deployable investigative use.
4. Code-split the 754 kB JavaScript bundle and virtualize/paginate the very long Timeline/Audit views.

### P2 — only if time remains

1. Add reproducible larger synthetic benchmarks (1k/10k/100k nodes) and report measured limits.
2. Replace remaining internal `VEIL-DEMO-001` identifiers after the demo freeze; do not risk a late migration before judging.

## Safe one-line product claim

“Network Intel is an evidence-linked investigation prototype that ingests controlled records, resolves identities with human review, builds an association graph, surfaces rule-based and statistical leads, and lets an investigator trace every surfaced claim back to its source.”
