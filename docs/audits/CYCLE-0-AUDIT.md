# VEIL — Cycle 0 repository audit and Cycle 1 build plan

Audit date: 4 September 2026. This document treats the implementation already present on disk as the baseline, including its previously named `CYCLE-1.md`. That earlier report is historical; this audit is a new planning checkpoint. No product implementation is authorized or performed in this cycle.

## Verdict

**A. Extend the existing implementation.** The installed stack is already the requested stack, the frontend is usable, the backend computes paths and temporal leads, provenance links resolve, and the existing tests/build pass. The work needed is incremental contract, fixture, correctness, and UI-state refinement. Neither a fresh prototype nor a partial replacement of the frontend/backend is justified.

## 1. Repository inventory

```text
Network Intel/
  frontend/
    package.json, package-lock.json
    index.html, vite.config.ts, tsconfig.json
    src/
      main.tsx                 React entrypoint
      App.tsx                  All views, fetching, filters, inspectors, reviews
      Graph.tsx                Cytoscape rendering and selection
      types.ts                 TypeScript shapes and generic fetch helper
      style.css                Global dark workspace styling
    node_modules/, dist/, tsconfig.tsbuildinfo  [generated]
  backend/
    __init__.py
    main.py                    FastAPI endpoints and SQLite review storage
    intelligence.py            Graph filtering, shortest paths, temporal rule
    generate_data.py            Deterministic fixture generator
    data/trinetra.json          One combined synthetic dataset
    data/reviews.sqlite3        Local review history
  tests/test_backend.py         Six backend tests
  requirements.txt, requirements-lock.txt
  README.md, CYCLE-1.md, .gitignore
  artifacts/                    Existing demo screenshots
  .venv/, .pytest_cache/         [generated]
```

All project-owned source, configuration, fixtures, tests, and existing documentation were inspected. Dependency vendor source was not audited. No AGENTS.md, environment file, lint configuration, CI workflow, container configuration, or hosting manifest was found in the project.

**Git:** `git status --short` and `git rev-parse --show-toplevel` both fail with “not a git repository.” A `.gitignore` exists, but there is no repository metadata in this workspace or a parent recognized by Git. No clean-tree assertion, diff, branch, remote, or history is available. Do not confuse this with an empty Git diff. Establish a Git baseline separately before implementation; do not delete or recreate the workspace.

**Frontend:** React + TypeScript, Vite, Cytoscape, Lucide icons. Installed versions: React/React DOM 19.2.8, Vite 6.4.3, TypeScript 5.8.3, Cytoscape 3.34.2. There is one browser URL, `/`. Network, Source records, Alias review, Leads, and Audit trail are local `view` state inside App, not router routes. Reload restores Network. The brand's `#` link is not a route architecture.

**Styling:** plain global CSS, no Tailwind/component framework. Flex layout, a 205px sidebar, a 330px scrollable inspector, graph canvas, dark palette, type colors, and responsive breakpoints at 1550/1180/900px. The useful visual work should stay. Many metadata/control labels are 9–12px, so readable projected text needs a targeted check. App is compressed into 27 long source lines and CSS into one line; formatting and bounded component extraction will improve maintainability.

**Graph:** actual Cytoscape canvas, typed node shapes/colors, directed source arrows, dashed inferred links, node/edge selection, fit, highlighting. Display positions are fixture coordinates with `y * 0.50`; this is layout, not an analytical computation. NetworkX uses a MultiGraph and shortest_path over backend-filtered edges. Traversal is undirected and equal-cost, with a lexicographically chosen edge among parallel edges. Equal-length node routes still depend on graph insertion order. The graph is recreated whenever its entity/edge inputs change and fitted on resize.

**Data:** `trinetra.json` has 10 entities, 13 edges (12 recorded, one inferred), 13 evidence entries, one alias candidate, and case metadata. There are 5 Report, 3 Transaction, 3 CDR, and 2 Vehicle evidence entries referring to 9 unique source names. Actual named CSV/TXT source files are absent; the excerpts are the canonical synthetic records. The in-memory generator output exactly matches the JSON. There are no separate events, source registry, or lead fixture files. The one lead is computed at runtime, not a fixture lead.

**Backend:** FastAPI, NetworkX, Python standard-library SQLite; JSON loads at import. Only Review has a Pydantic request schema. Case/graph/evidence/lead outputs are unvalidated dictionaries without explicit response models. SQLite has one reviews table; two existing QA reviews were counted through a read-only connection. The table has no case/data/rule version snapshot. Actor is the literal `Demo reviewer`, not authentication.

**Environment:** no mandatory environment variable or external API key. Optional `VEIL_DB` overrides the SQLite path; otherwise it is `backend/data/reviews.sqlite3`. The frontend fetches relative `/api` URLs; Vite's development proxy forwards them to `http://127.0.0.1:8000`. Fixture loading needs readable JSON; reviews need a writable SQLite location. Existing setup uses Node/npm and a Python venv. No external AI, remote database, or downloaded font is required at runtime.

**Deployment:** local development only. Build produces `frontend/dist`; there is no production API reverse proxy, static mount, deployment script, hosting manifest, or CI. A successful Vite build alone is not a working deployed application. Use the documented local two-process demo in Cycle 1; do not add cloud infrastructure during contract work.

## 2. Checks executed in this audit

| Check | Result |
|---|---|
| `npm ls --depth=0` in frontend | Passed; all declared top-level packages installed |
| package-lock root dependencies versus package manifest | Match; lockfile version 3 |
| `.venv/Scripts/python.exe -m pip check` | Passed: no broken requirements |
| `npm run build` in frontend | Passed; includes `tsc -b` and Vite build |
| `frontend/node_modules/.bin/tsc.cmd --noEmit` | Passed separately |
| `.venv/Scripts/python.exe -m pytest -q` | 6 passed, 2 dependency deprecation warnings |
| FastAPI TestClient application startup and current read endpoints | Passed; case, graph, path, evidence all return 200 |
| Requested new URLs | Five return 404; `/api/evidence/{evidence_id}` already works |
| Fixture generation comparison | Existing JSON exactly equals in-memory generator output |
| Review database | Schema inspected and 2 rows counted read-only |
| Browser | Existing Network screen and four-hop inspector observed; screenshot captured; no new review submitted |
| Lint | Not configured; no lint command run or dependency added |
| Frontend automated tests | Not configured; no frontend test script or runner exists |

Build warning: a 670.19 kB JavaScript chunk (212.73 kB gzip) exceeds Vite's 500 kB advisory threshold. Pytest warnings concern Starlette's HTTPX integration and an AnyIO alias. These are warnings, not failed gates. Setup was validated against installed dependencies; this was not a clean-machine reinstall or a security audit.

The existing six tests cover provenance references, path behavior after removing an edge, filters/inferred opt-in, no-path and invalid entities, temporal negatives, review validation/persistence, and non-merging alias decisions. They do not cover the proposed endpoint contracts, malformed fixture startup, source-registry integrity, temporal boundaries, inferred event exclusion, frontend request races, or deterministic ties after fixture reordering.

## 3. Findings and disposition

| Major part | Decision | Reason and smallest change |
|---|---|---|
| React/Vite/TypeScript toolchain and lock files | KEEP | Working build; compatible with the prototype. No framework migration. |
| Current Network workspace at `/` | KEEP | Already exposes graph, path controls, evidence inspector, and synthetic label. Make this the principal judge screen. |
| App orchestration and local view state | MODIFY | Extract network controls/inspectors; bind case metadata and initial filters to backend response; add explicit loading/error/empty states. No router dependency needed. |
| Cytoscape renderer | MODIFY | Preserve styles and layout. Update elements without unnecessary remounts; preserve pan/zoom; order presentation deterministically and show filter/path semantics clearly. |
| Existing dark CSS and icons | MODIFY | Preserve visual language; format CSS and adjust small critical labels only. |
| Dead `.path-result` CSS rules | REMOVE | Current JSX has no `.path-result` element. Remove in a later implementation change, not this audit. |
| Frontend `types.ts` and fetch helper | MODIFY | Separate API access from types, introduce six requested calls, match backend response schemas, encode query values, use AbortSignal/request guards. |
| FastAPI runtime | KEEP | Works with installed dependencies and serves required existing functions. |
| API route and response layer | MODIFY | Add requested case-scoped routes and lead endpoints using shared services; explicit Pydantic response/error models. Retain legacy wrappers during migration. |
| Combined `trinetra.json` as sole runtime store | REPLACE | Replace its storage shape with the six normalized fixture files. Preserve all existing identities, evidence IDs, edge IDs, and content through migration. |
| Deterministic generator and narrative | MODIFY | Reuse existing synthetic case, generate structured events/sources, validate references and deterministic output. |
| NetworkX path algorithm | MODIFY | Keep shortest_path/MultiGraph; stabilize insertion order and explain source direction versus traversal direction in each hop. |
| T01 temporal lead rule | MODIFY | Keep computed behavior; consume structured events, enforce recorded status across contributing inputs, make association-time assumptions explicit, and return event/relationship IDs. |
| Alias candidate/review behavior | KEEP | Explicitly uncertain; reviewer acceptance never silently merges nodes or verifies edges. Preserve candidate and review IDs during fixture migration. |
| Evidence UI and provenance content | MODIFY | Preserve modal/excerpts; introduce source IDs, structured locators, and validated source-to-excerpt relationships. |
| SQLite review/audit subsystem | KEEP | Already small and persistent. Preserve existing rows/schema and endpoints; future version snapshots can be additive. No new database. |
| Existing Pytest tests | MODIFY | Keep regressions and extend contract, fixture, temporal, and deterministic-path coverage. |
| Local dev proxy and deployment approach | KEEP | Two local processes are sufficient. Document that static build output needs an API-serving arrangement before any deployment. |
| README / prior cycle report / screenshots | MODIFY | Update README and add this audit; preserve the previous report and screenshots as historical evidence. |

### Specific correctness risks

1. **Inferred events enter the temporal rule.** An in-memory copy with the transfer's status changed to `inferred` still produces one lead. Calls and holder edges are also not uniformly status-filtered. This is a demonstrated rule boundary gap; do not advertise the rule as recorded-input-only until corrected.
2. **Association time is not evaluated.** Moving the sender's holder record timestamp after the transfer still produces the lead. This shows that T01 uses record associations, not verified ownership at event time. Do not treat `recorded_at` as `valid_from`. Add explicit synthetic validity intervals where the fixture establishes them; otherwise surface temporal applicability as unknown.
3. **Current APIs differ from the requested contract.** `/api/case`, `/api/graph`, and `/api/path` are global; no lead collection/detail endpoint exists. Five requested new endpoints return 404. Evidence routing already matches.
4. **Case and view state can diverge.** Case name/date defaults and endpoints are embedded in JSX; `/case` and `/graph` fetch separately. A successful graph fetch can clear a case-loading error; graph nodes come from the case payload while graph response entities are ignored. This is a code-inspection risk, not a reproduced UI failure in this audit.
5. **Partial stale-request protection.** Paths guard successful responses with a request counter, but stale errors can still overwrite current errors. Evidence requests have no cancellation or selection guard. A slow response can open an older selection. Add a focused browser test before claiming this fixed.
6. **Filters and meanings need clarity.** Graph filters do not recompute the case-wide lead. Unchanged date text can be mistaken for the active filter. All entities remain visible even with no edges. Undirected traversal is disclosed at the bottom of the path inspector; move that disclosure near the path summary.
7. **Source and event schemas are conflated.** Calls/transfers are graph edges; amounts/durations are mainly excerpt text. Nine named source documents are not separately stored. Treat current excerpts honestly and add structured synthetic source records, not a claim that full files were ingested.
8. **Fixture errors fail late.** Data loads without schema/referential validation; missing fields may raise exceptions within analytical requests. Validate once at startup and fail clearly without a demo fallback that hides corruption.

## 4. Smallest viable architecture

```text
React Network workspace at /
  → typed fetch client (relative /api)
  → one FastAPI application
      → validated in-memory DemoRepository (six JSON fixture files)
      → existing NetworkX path service
      → deterministic T01 lead service
      → existing SQLite review/audit store
```

Request flow: Open Case → fetch graph → compute path → list/open related lead → resolve evidence and its source. The backend returns all analytical results, counts, paths, rule signals and provenance. The frontend only renders, sorts/presents records, handles selections, and highlights returned IDs. No LLM, Neo4j, vector database, queue, auth service, graph ML, or new frontend framework.

The current `/` Network view remains the primary judge-demo screen. Keep source/alias/audit views reachable through the existing sidebar. Add a compact case-lead entry point inside Network so opening a lead does not require losing the graph. No new landing page is justified. Persistent URL navigation can be deferred.

## 5. Initial API contracts — proposed, not implemented

All responses are JSON. IDs are strings, dates use ISO 8601, event timestamps include timezone offsets, list ordering is deterministic, and the demonstration uses `case_id: "trinetra"`, `data_version: "trinetra-v1"`, `synthetic: true`. `demo` is a stable URL alias for this case, not a second case ID. Every success response carries those three metadata fields. The UI never infers that `recorded` means verified.

Shared shapes (required unless marked optional):

```ts
type Entity = {
  id: string;
  label: string;
  type: 'Person'|'Alias'|'Phone'|'Account'|'Vehicle'|'Location'|'Organization';
  description: string;
  evidence_ids: string[];
  position: { x: number; y: number }; // display only
};
type Relationship = {
  id: string;
  source: string; target: string;
  type: string; // validated fixed fixture vocabulary
  status: 'recorded'|'inferred';
  recorded_at: string;
  valid_from: string|null; valid_to: string|null;
  event_ids: string[];
  evidence_ids: string[]; // nonempty
  inference_reason?: string;
  candidate_id?: string; // preserve alias-01
};
type Evidence = {
  id: string; source_id: string;
  kind: 'Report'|'CDR'|'Transaction'|'Vehicle';
  recorded_at: string;
  locator: { kind:'row'|'paragraph'; number:number; fields:string[] };
  excerpt: string;
};
type Signal = {
  id: string; title: string; detail: string;
  event_ids: string[]; relationship_ids: string[];
  evidence_ids: string[]; // nonempty
};
type Lead = {
  id: string; title: string; subtitle: string;
  entity_ids: string[];
  generated_by: 'computed_rule';
  rule: { id:'T01'; version:string; parameters:{call_count_min:3;
    call_window_minutes:30; transfer_gap_minutes:30} };
  review_priority: 'review_suggested'; // never guilt probability
  time_window: {start:string; end:string};
  scope: 'case';
  signals: Signal[];
  evidence_ids: string[];
  limitations: string[];
};
```

### GET /api/cases/demo

200: metadata plus `case: {id,name,reference,description,timezone,date_range:{start,end}}`, `counts:{entities,relationships,evidence,sources,leads,alias_candidates}`, `defaults:{source_id,target_id,include_inferred:false}`, and `capabilities:{computed_paths:true,computed_leads:true,review_persistence:true}`. Counts reflect the entire validated case, not current graph filters. Do not embed the whole evidence collection in this response.

### GET /api/cases/demo/graph

Optional query: `relationship` (one validated relation type), `start`, `end` (inclusive YYYY-MM-DD in Asia/Kolkata), `include_inferred=false`. Empty/omitted dates are unbounded; an unknown type or reversed range is 422.

200: metadata plus `entities: Entity[]`, `relationships: Relationship[]`, `filters:{relationship,start,end,include_inferred}`, `counts:{entities,relationships}`, `time_basis:"recorded_at"`, `available_relationship_types:string[]`. Keep all 10 entities to maintain selectable disconnected endpoints; visibly state zero relationships when filters remove all edges. Types for the controls come from the full case vocabulary, not the narrowed result. Validity intervals and event timing are separate from graph record-date filtering.

### GET /api/cases/demo/leads

200: metadata plus `scope:"case"` and `items` containing `{id,title,subtitle,entity_ids,review_priority,time_window,rule_id,rule_version,evidence_count,generated_by}`. Backend computes the collection. No graph filters apply implicitly. No leads returns 200 with `items: []`. The frontend can choose a lead whose returned entity IDs intersect the selected path; this is presentation filtering, not lead computation.

### GET /api/leads/{lead_id}

200: metadata plus `lead: Lead`. Initially preserve `T01-r008` so existing review rows retain meaning. All signal evidence, event and relationship IDs must resolve within the same data version. Unknown ID returns 404 `LEAD_NOT_FOUND`.

### GET /api/evidence/{evidence_id}

200: metadata plus `evidence: Evidence` and `source:{id,title,kind,representation:"synthetic_excerpt_collection",synthetic:true}`. The locator identifies a record in the canonical source collection; the excerpt must equal that source record's text. Do not return an invented file download URL. Unknown ID returns 404 `EVIDENCE_NOT_FOUND`. This changes the current flat response shape, so the frontend adapter and response test must ship in the same increment.

### GET /api/cases/demo/path?source={id}&target={id}

Required query `source`, `target`; optional filters exactly match the graph endpoint, using the same filter function. The result is the minimum-hop association path, not a chronological route or communication-flow assertion.

200 example payload, in addition to common metadata:

```json
{
  "found": true,
  "source": "p1",
  "target": "v1",
  "node_ids": ["p1", "ph1", "ph2", "p2", "v1"],
  "relationship_ids": ["r001", "r005", "r002", "r009"],
  "hops": 4,
  "steps": [
    {"from":"p1","to":"ph1","relationship_id":"r001","traversal":"forward","evidence_ids":["E001"]},
    {"from":"ph1","to":"ph2","relationship_id":"r005","traversal":"forward","evidence_ids":["E005"]},
    {"from":"ph2","to":"p2","relationship_id":"r002","traversal":"reverse","evidence_ids":["E002"]},
    {"from":"p2","to":"v1","relationship_id":"r009","traversal":"forward","evidence_ids":["E009"]}
  ],
  "evidence_ids": ["E001","E002","E005","E009"],
  "contains_inferred": false,
  "method": {"algorithm":"shortest_path","direction":"undirected_association","cost":"one_per_relationship","tie_break":"stable_entity_and_relationship_id_order"},
  "limitations": ["Association does not establish causation or a chronological sequence."]
}
```

Also return applied `filters`. A known but disconnected pair returns 200, `found:false`, empty IDs/steps/evidence, `hops:null`, and `reason:"NO_PATH_UNDER_FILTERS"`. A known identical source/target returns one node, zero steps, zero hops. Unknown entities return 404 `ENTITY_NOT_FOUND`; missing required parameters or bad filters return 422. This separates an expected no-result state from an invalid entity.

Common error body: `{"error":{"code":"ENTITY_NOT_FOUND","message":"Unknown entity","details":{"entity_id":"missing"}}}`. Normalize request-validation errors to the same envelope. No stack traces or silent fixture fallbacks. A corrupt fixture stops startup with a descriptive validation error. Existing legacy routes can retain their old envelopes while the UI migrates; both call the same services.

## 6. Minimum synthetic fixture files

Create these under `backend/data/demo/`. Each file has `{schema_version:1,case_id:"trinetra",data_version:"trinetra-v1",synthetic:true,items:[...]}`. `entities.json` also carries the case metadata/defaults described above, avoiding an unnecessary seventh case manifest.

| File | Minimum contents | Role and migration |
|---|---|---|
| `entities.json` | Existing 10 entities, evidence IDs, display positions; case metadata and default endpoints | Preserve IDs p1/p2/alias/ph1/ph2/a1/a2/v1/loc/org. Positions do not determine paths. |
| `relationships.json` | Existing 13 relationships with provenance, status, optional validity and event links | Preserve existing IDs including r13. Preserve alias candidate ID alias-01 and its reason on r13 for legacy review compatibility. |
| `events.json` | 5 events: 3 calls, 1 transfer, 1 vehicle observation | Each has id, type, occurred_at, status, participants with roles, relationship_ids, evidence_ids, and structured attributes. Call duration_seconds and transaction amount/currency are authored in the generator alongside the excerpt. No frontend parsing. |
| `leads.json` | Deterministic expected computed output for T01-r008, with rule/data version | Regression snapshot only. The live API computes leads from events/relationships; it never serves a stale stored lead when inputs change. Do not downgrade the working rule to hardcoded fixture leads. |
| `evidence.json` | Existing 13 excerpts, source_id, structured locator, recorded_at | Preserve evidence IDs and verbatim text; validate exact matching to canonical source records. |
| `sources.json` | 9 source entries, matching the 9 existing names | id, title, kind, synthetic:true, representation:synthetic_excerpt_collection, records:[{locator,text}]. These are authored synthetic record collections, not uploaded full documents. |

Event example: `{id:"ev005",type:"call",occurred_at:"2026-08-15T21:10:00+05:30",status:"recorded",participants:[{entity_id:"ph1",role:"caller"},{entity_id:"ph2",role:"callee"}],relationship_ids:["r005"],evidence_ids:["E005"],attributes:{duration_seconds:80}}`.

Validation gates: unique IDs per namespace; case/data versions agree; all endpoints, participant IDs, source IDs, event IDs, and evidence IDs resolve; every relationship/signal has evidence; source text and evidence locators agree; timestamps have offsets; event/relationship directions agree where applicable; inferred items carry reasons; no duplicate event counting; generated output is deterministic. At least one non-qualifying temporal variant must be constructed in tests. Preserve the live case fixture until migration equivalence is proven.

## 7. Exact Cycle 1 implementation plan — future work

No new runtime or test dependency is needed. Retain current lock files. Existing Pydantic, NetworkX, Pytest, HTTPX, React and Cytoscape cover the work. Use current browser tooling for manual UI verification; do not add an automated browser framework solely for this cycle.

| Increment | Files to create | Files to modify | Exit gate: runnable demo |
|---|---|---|---|
| 1. Contract layer over current data | `backend/schemas.py`, `backend/repository.py`, `tests/test_api_contracts.py` | `backend/main.py`, `backend/intelligence.py` only for return-shape adapters | Add six requested endpoints and response/error models. Existing frontend and review endpoints still work. Test positive/404/422/no-path cases. |
| 2. Normalize deterministic fixtures | Six `backend/data/demo/*.json` files above; `tests/test_fixtures.py` | `backend/repository.py`, `backend/generate_data.py`, `tests/test_backend.py` | Loader validates normalized fixtures and builds the legacy adapter as needed. Compare IDs, excerpts, graph, expected path and review targets with old fixture before switching. |
| 3. Correct analytical boundaries | `tests/test_temporal_rules.py`, `tests/test_paths.py` | `backend/intelligence.py`, `backend/schemas.py`, fixture generator/snapshots | T01 consumes events, checks recorded status, uses explicit association validity or reports uncertainty, and emits source-complete signals. Paths are stable under reordered fixture input. Demo still computes from data. |
| 4. Migrate the Network view incrementally | `frontend/src/api.ts`, `frontend/src/components/NetworkWorkspace.tsx`, `frontend/src/components/InvestigationInspector.tsx`, `frontend/src/components/EvidenceDialog.tsx` | `frontend/src/App.tsx`, `frontend/src/types.ts`, `frontend/src/Graph.tsx`, `frontend/src/style.css` | Typed calls use new contracts; controls/defaults use backend case metadata; path → related lead → evidence works within Network. Existing source/alias/audit views stay functional. |
| 5. Acceptance and handoff | `docs/CYCLE-1-ACCEPTANCE.md`, new QA screenshots under `artifacts/` | `README.md`; package scripts only if exposing existing type checker helps | All existing/new tests and build pass; manual ten-step flow at 1366×768; one source and one graph failure/retry check; no new runtime errors. |

Components remain deliberately few. NetworkWorkspace contains search, relationship/date controls, path controls, legend, and existing Graph; InvestigationInspector renders entity, relationship, path, and lead detail plus existing review form; EvidenceDialog owns the source excerpt and focus behavior. Leave unrelated source/alias/audit views in App for now rather than turning a small extraction into a rewrite.

Backend modules remain equally small: main for HTTP wiring and existing reviews, schemas for validation, repository for fixture loading/indexes and source lookup, intelligence for path/lead functions. No generic service framework, ORM, or new database migration layer.

### Required tests for Cycle 1

- Contract tests for all six endpoints, consistent metadata, typed success and error envelopes, unknown IDs, empty lists, and source lookup.
- Fixture integrity and deterministic generation; invalid fixtures fail before requests; source excerpt/locator equality; IDs used by existing reviews remain valid.
- Path length/adjacency/provenance, same-node zero-hop, disconnected result, edge deletion, dates/relation filters, inferred excluded by default, explicit inferred inclusion, parallel edges, and stable ties after input shuffling.
- T01 positive, two-call negative, inclusive 30-minute boundaries, transfer-before-call negative, wrong direction/pair, inferred call/transfer/holder exclusion, duplicate source/event handling, multiple candidates with unique lead IDs, and association validity/unknown-time behavior.
- Retain review validation, persistence, and no-merge tests. Do not reset the existing demo database to make a test pass.
- Manual UI: complete judge flow, filter-induced no-path, rapid selection/request changes, backend failure and recovery, evidence keyboard focus/escape, no frontend recomputation, and screenshot legibility at target size.

### Risks and mitigations

- Fixture/API migration can break review references: preserve existing IDs and keep adapters until parity tests pass.
- Full source documents do not exist: keep the representation label explicit; author synthetic record collections without inventing an ingestion claim.
- Time semantics can introduce false precision: separate recorded_at, occurred_at and validity; expose unknown applicability.
- T01 remains a heuristic: do not claim validated AI accuracy or guilt probabilities. No external AI dependency is added to mask this limitation.
- App extraction can destabilize selection/focus: move bounded UI blocks and verify each increment, preserving the CSS layout.
- Local deployment and Git history remain absent: document the two-terminal setup and establish a baseline before implementation; do not add production complexity.

## 8. Run and inspect the existing demo

No setup installation was performed during this audit. If the retained local servers are no longer running, use the existing installed environment:

```powershell
cd 'Z:\XLab\New\Network Intel'
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Second terminal:

```powershell
cd 'Z:\XLab\New\Network Intel\frontend'
npm run dev -- --port 5173 --strictPort
```

Open `http://127.0.0.1:5173` → Operation Trinetra → Network → default Arjun Mehta / DEMO-VH-07 → Find path → inspect E001/E005/E002/E009 → Leads → Calls followed by a transfer → inspect E005/E008/E003. Source records, Alias review and Audit trail remain available. No review submission is needed to reproduce the audit's read-only observations.

## 9. Audit completion

The Cycle 0 definition of done is an inspected inventory, executed safe checks, explicit dispositions, minimal architecture, six API contracts, six fixture definitions, primary-screen choice, and a file-level Cycle 1 plan with tests and risks. Those deliverables are complete. Only this audit document and a screenshot were added; generated build/cache outputs may refresh from the requested checks. No product source, dependency declaration, lock file, fixture, or existing review was intentionally modified.

**Final verdict: A. Extend the existing implementation.** Keep the working frontend/backend and spend Cycle 1 on correctness and contract alignment. The identified gaps are local and testable; a rebuild would discard working graph, provenance, and review behavior without solving a structural incompatibility.
