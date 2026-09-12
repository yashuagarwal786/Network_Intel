# VEIL / Network Intel — Fundamental Audit + SIH Judge Defense (Hinglish)

**Audit date:** 9 September 2026  
**Target:** SIH 26189 — AI-Powered Criminal Network Analysis System  
**Basis:** current working tree, backend/API/frontend code, fixtures, tests, production build, and SIH problem description.  
**Verification:** 101/101 backend tests passed; frontend typecheck and lint passed; production build passed with one large-chunk warning; 4/4 Playwright tests passed.

## Executive verdict — sabse important answer

Experienced technical judge 10 minutes mein sabse pehle yahan attack karega:

1. **“Fresh arbitrary data par bhi chalega, ya sirf Trinetra story par?”** Controlled CSV/TXT ingestion real hai, lekin report relationships exact grammar par depend hain, Person nodes source-local hain, aur seeded lead logic ka strongest graph-correlation path default case anchors use karta hai. **FIX/MITIGATE.**
2. **“Key influencer identification kahan hai?”** Official PS ka explicit requirement hai, par active product mein PageRank, degree/betweenness ranking ya community detection exposed nahi hai. **FIX NOW. Do not defend this as implemented.**
3. **“Entity resolution kitni reliable hai?”** Real conservative workflow hai, lekin score fixed, uncalibrated heuristic hai; false-merge/false-split metrics nahi hain. Shared phone ko 60% weight milta hai. **MITIGATE + LEARN.**
4. **“AI exactly kya karta hai?”** spaCy NER aur Isolation Forest actually implemented hain. Temporal lead engine and path are deterministic, AI nahi. NER relation creation itself ML nahi; exact templates hain. Isolation Forest tiny, biased case cohort par unvalidated triage ranking hai. **EXPLAIN honestly.**
5. **“Police data secure kaise hai?”** Authentication, RBAC, case-level authorization, encryption policy, retention/deletion, rate limiting, and tamper-evident audit absent hain. Synthetic local MVP ke liye disclose kar sakte ho; real investigative use claim nahi kar sakte. **MITIGATE before judges; production gap EXPLAIN.**

**Bottom line:** Product sirf pretty graph nahi hai. Isme real provenance, parsers, graph construction, bounded path traversal, deterministic leads, reversible identity review, statistical anomaly triage, exact evidence drill-down and review journal hain. Lekin it is a **controlled synthetic investigation-workflow prototype**, not a general criminal intelligence engine. Current strongest advantage explainability/provenance hai; biggest rejection risks PS-incomplete influencer analysis, narrow generalization, unvalidated identity/anomaly logic, and absent security boundary hain.

---

# PART 1 — Actual system reverse-engineering

## End-to-end pipeline

| Stage | Status | Actual implementation and truth |
|---|---|---|
| User input | 🟡 Partial | User controlled JSON text envelope se CSV/TXT upload karta hai (`DataIntake.tsx`, `api.ts`, `main.py:158`). PDF, OCR, images, arbitrary FIR format absent. Fresh case creation hidden/non-schema API se possible hai. |
| Frontend | ✅ Implemented | React 19 + TypeScript + Vite. `NetworkWorkspace.tsx` orchestration; `DataIntake.tsx`, `ResolutionReview.tsx`, `Graph.tsx`, `LeadDetail.tsx`, `BehavioralAnomalyView.tsx`. |
| API | ✅ Implemented | FastAPI (`backend/main.py`) with Pydantic response models and normalized error envelope for active endpoints. Synchronous single process. |
| Parsing | ✅ Controlled / ⚠️ narrow | Exact CSV headers and strict validation in `intake_parser.parse/validate_row`; TXT split line-by-line. 64 KiB/file, 16 files. Real messy schemas unsupported. |
| Entity extraction | 🟡 Partial | CDR/accounts/vehicles/dates/money via regex; Report Person/Org/Location via `ner_service.extract` using `en_core_web_sm`, plus gazetteer fallback. Small English NER is not domain-trained; offsets from spaCy are not stored in `Mention`. |
| Entity resolution | 🟡 Real but weakly validated | `resolution.normalize/assets/candidates/proposals`; normalized string similarity 20%, exact shared phone 60%, vehicle 20%; human confirm/reject/defer/undo. No auto merge. No calibrated accuracy. |
| Relationship creation | ⚠️ Narrow | Structured rows create `CALLED`, `TRANSFERRED_TO`, keeper/observed-with edges. Reports create edges only for exact full-line templates (`uses phone`, `controls account`, etc.). Negated/possible claims withheld. All accepted claims are labelled UNVERIFIED. |
| Storage | 🟡 Prototype | Seed graph/evidence/events/sources are JSON fixtures loaded in memory. Intake snapshot, resolution decisions, reviews/audit in three SQLite files. No graph DB. Uploaded content itself is stored inside one SQLite JSON payload. |
| Graph creation | ✅ Small-data | `IntakeStore.augment` deep-copies base repository and adds extracted nodes/relationships/events/evidence on requests. Entity resolution `project` makes canonical projection. |
| Graph algorithms | 🟡 Partial PS coverage | NetworkX bounded unweighted undirected shortest path; connected components inside transfer windows; clustering coefficient as anomaly feature. No influencer ranking, PageRank, betweenness view, communities, or link prediction. |
| Intelligence/alerts | 🟡 Implemented but scenario-bound | `lead_engine.run_engine`: communication burst, new contacts, connected transfer sequence, graph-context correlation, evidence gating. `behavioral_profiler.run_behavioral_profiler`: Isolation Forest triage. Anomaly signals are returned separately and not integrated into lead inbox. |
| Visualization | ✅ Implemented | Cytoscape preset layout; typed shapes/colors, dashed UNVERIFIED links, path fade/highlight, inspector. Fixed anchors for demo nodes; position is presentation only. |
| Evidence to investigator | ✅ Strong | `Evidence` includes source ID/file/type, row/span, exact excerpt, timestamp, related entity/relationship IDs, parser/version/status. UI can open evidence from edge, path, signal, anomaly profile. |

## Actual request flow

`DataIntake.tsx` → `POST /api/cases/demo/sources/upload` → request size/content/name validation → `IntakeStore.upload` stores manifest/content → `POST /process` → `parse()` → `extract()` → records/mentions/claims snapshot → `IntakeStore.augment()` builds request-time repository → `resolution.project()` canonicalizes confirmed pairs → `GraphResponse` to React/Cytoscape → `run_engine()` or `compute_path()` → evidence IDs → inspector calls `/api/evidence/{id}`.

Important split: seeded JSON evidence and uploaded evidence coexist in default case. A fresh case clears fixture projection inside `augment`, but the global `repository`, some audit calls, and several endpoints remain coded around `VEIL-DEMO-001`; multi-case is not real.

---

# PART 2 — Fundamental flaw audit

## 1. Problem–solution fit

SIH 26189 asks multi-source processing, entity extraction, relationship maps, influential people, unusual patterns, and investigator insight. VEIL covers ingestion (narrow), extraction (partial), graph maps (strong), suspicious-pattern triage (partial-good), and explainable investigator workflow (strong). It **does not cover key influencer identification**, one direct requirement.

Genuine investigator value exists: cross-source navigation, evidence-preserving path discovery, withheld uncertain claims, transparent lead calculations, reversible resolution, and human review. Therefore it is not “upload → pretty graph” only. But actionable intelligence is demonstrated on planted synthetic signals; no real investigator study or held-out accuracy establishes operational value.

**Decision:** influencer analysis **FIX NOW**; arbitrary-data claims **MITIGATE**; real-world impact **EXPLAIN**.

## 2. Dangerous data assumptions

| Assumption in code | What breaks | Decision |
|---|---|---|
| Exact CSV header order (`HEADERS`) | Common exports with renamed/reordered columns reject completely. | MITIGATE: document templates + header mapper later. |
| Every field non-empty | Legitimately missing tower/location/channel rows become invalid rather than partially useful. | MITIGATE. |
| Phone is 10–15 digits and normalized only by stripping space/`() + -` | Extensions, leading `00`, local numbers, reused/reassigned phones and invalid-yet-shaped values mishandled. | EXPLAIN + validation status. |
| Synthetic account/vehicle patterns only | Real bank/vehicle identifiers cannot be ingested. | EXPLAIN controlled demo; never claim real formats. |
| Fixed locations and people for Vehicle CSV | Any unseen person/location is rejected. This is demo grammar, not general ingestion. | FIX for unseen demo if possible. |
| UTF-8 CSV/TXT only | PDF/OCR/FIR scans/Excel/encoding variants unsupported. | EXPLAIN. |
| Report is one assertion per line and exact English templates | Natural prose, passive voice, Hindi/regional languages, cross-sentence relations fail. | MITIGATE; do not call universal NLP. |
| Timestamps always include timezone | Real sources often local/ambiguous; rows reject. | Correct safety posture, but add source timezone mapping later. |
| Duplicate detection uses content hash/source type | Semantically same record in edited/exported file duplicates. | MITIGATE. |
| Person identity is source-file scoped | Same person in two files becomes two nodes until resolution; safe against false merge but causes fragmentation. | EXPLAIN deliberate conservative design. |
| Non-person identifier globally normalizes to node | Shared/recycled phones/accounts may connect multiple people; identifier equality is not operator identity. | MITIGATE with temporal ownership intervals and relationship roles. |
| Source assertions treated as recorded edges | “Recorded” means recorded assertion, not independently verified fact; wording can be misunderstood. | FIX label/copy to “source-asserted / unverified.” |

Contradictory evidence is not reconciled. Positive and negative statements are retained separately, but no contradiction object/policy alerts investigator. Missing evidence simply shrinks graph and may erase paths/leads; absence is explicitly caveated but not quantified.

## 3. Entity resolution

Yes, entity resolution exists. `resolution.normalize` uses Unicode NFKC, casefold, punctuation removal and whitespace collapse. Candidate blocking uses same surname + first initial or exact shared phone. Score = SequenceMatcher name similarity × 0.2 + exact shared phone × 0.6 + shared vehicle × 0.2. `YES` requires ≥0.99 plus phone; `REVIEW` requires shared phone or name similarity ≥0.35. No proposal auto-merges; only `CONFIRM_MATCH` changes canonical projection; undo restores split nodes and original evidence remains.

False merge: family/shared phone, recycled number, jointly used vehicle, namesakes. False split: alias with different surname/script, missing identifiers, transliteration, new phone, spelling/OCR errors. A false merge combines edges/events of two people, changes shortest paths, features, lead participants, degrees/clustering and anomaly ranking. A false split hides connectivity and dilutes activity across nodes.

One code inconsistency: proposal endpoints call `current_matches()` dynamically, but `matches` global is computed at import and still used by `sync_resolution_audit`, `submit_review` merge assessment, and timeline projection. Fresh uploaded proposals can therefore have inconsistent audit/review behavior. **Do not defend this. Fix it** by replacing all remaining `matches` references with one request-scoped/current proposal map.

Judge defense: “We choose false splits over silent false merges. Score is an explainable ranking score, not probability. Human reviews exact identifiers/evidence and every confirmation is reversible. Current weights are prototype heuristics and need calibration on labelled agency-approved pairs.”

Severity: **Serious**, because identity errors contaminate downstream graph intelligence.

## 4. Relationship creation

Structured edges are explicit row assertions: caller→receiver, sender account→receiver account, person→vehicle. Report edges are inferred by deterministic exact template matching after extraction. Co-occurrence alone does **not** create edges. Negated and possible meetings are withheld. Edges have type, status, verification status, extractor version, evidence IDs, and sometimes event IDs; timestamps are on evidence/events rather than always directly on relationship.

Missing: calibrated relationship confidence, independent-source count, temporal validity/ownership periods, contradiction state, and clear operator-vs-subscriber distinction. `compute_path` only traverses `status == recorded`, but both fixture relationships and UNVERIFIED extracted claims use `recorded`; it does not exclude UNVERIFIED edges. Thus a path may look authoritative even when every edge is machine-extracted.

**FIX NOW:** path response/UI should show per-edge verification and a path-level “contains N unverified assertions” warning; optionally default to verified/source-asserted filter. Never say path proves conspiracy.

## 5. Evidence and provenance

This is the strongest subsystem. Graph/lead/path claims generally resolve to exact evidence. Fixture repository validates source/evidence/entity references at startup. Intake evidence retains exact row/excerpt, normalized fields and parser version. Lead creation refuses untraceable events.

Limitations: original uploaded bytes are embedded in mutable SQLite JSON state; no immutable object hash chain, signature, custody metadata, uploader identity, access authorization, or retention policy. Audit is append-only only through normal application methods and database admins can modify it. `GET /source-files` returns complete uploaded contents with no auth. Evidence access itself appends an audit event, but actor is always “Local demo session.”

## 6. Graph analytics correctness

| Algorithm | Question | Implementation | UI meaning | Validity |
|---|---|---|---|---|
| Bounded shortest path | Is any association chain ≤8 hops present? | NetworkX `MultiGraph`, recorded edges, unweighted undirected BFS; deterministic first parallel edge. | Hidden connection/path. | Correct only as shortest hop-count association. Reverse traversal is shown. It does not prove causation/coordination, and equal-cost semantics ignore edge quality/time/type. |
| Connected components in transfer window | Are ≥3 transfer records weakly connected in 90 min? | Undirected account graph for each sliding inclusive window; maximal groups retained. | Connected transfer sequence. | Correct for weak connectivity and timing; not money flow tracing, distinct funds, laundering or circularity. |
| Communication burst | Is current outgoing count ≥ max(5, 3× seven-day median)? | Baseline includes zero days; minimum 3 observed days; replay timestamp. | Reviewable activity spike. | Transparent heuristic, not anomaly probability. Sensitive to incomplete records and day boundary. |
| New contacts | Are ≥3 event-day recipients absent from baseline? | Set difference against prior seven days. | Contacts new to dataset baseline. | Must say “new in available records,” not new in real life. |
| Graph-context correlation | Do communication, transfers and bounded graph path coexist near time window? | Seed focus/default path, phone + ≥2 accounts + ownership evidence. | Multi-source contextual signal. | Scenario-specific correlation. Temporal proximity and path coexistence are not causation. |
| Local clustering coefficient | Are an entity’s neighbors mutually connected? | NetworkX undirected graph combining relationships and event co-participation. | One Isolation Forest feature. | Math valid, semantic mix questionable: ownership, calls, transfers and reports treated equally. |
| Isolation Forest | Which active entities have rare engineered feature combinations? | sklearn, 100 trees, contamination auto, seed 42; scores min-max normalized within same case. | Outlier triage rank/percentile. | Computation real; “statistically valid at N≥6” claim is too strong. Six samples cannot establish operational validity. Percentile is relative/rank-derived, not calibrated risk. |

Not implemented: PageRank, degree/betweenness centrality ranking, community detection, link prediction. **Never claim them.**

## 7. False positives and safe language

Innocent hub examples: telecom tower, shared family phone, merchant account, logistics company, police officer, bank clearing account, investigator, hospital or common location. High activity, high cross-domain entropy, clustering, graph centrality or unusual amounts can all be legitimate.

Use: “source-asserted association,” “candidate identity match,” “review priority,” “statistical outlier within this case cohort,” “evidence-backed path,” “requires investigator verification.” Avoid: “criminal,” “mastermind,” “risk probability,” “gang confirmed,” “AI proved.”

## 8. AI / ML / NLP truth table

| Claim | Real implementation | Input → output | Why / failure handling | Verdict |
|---|---|---|---|---|
| NLP/NER | spaCy `en_core_web_sm` in `ner_service.py` | Report line → Person/Org/Location spans | Useful for variable named entities; model may miss/mislabel. Regex/gazetteer supplements; all output UNVERIFIED. No confidence/calibration and offsets are lost downstream. | Real, partial. |
| Deterministic extraction | regex + exact grammar in `intake_parser.py` | Structured IDs / exact sentences → mentions/claims | Better than LLM for reproducible structured records. Unsupported text withheld. | Real, not AI. |
| Entity resolution | SequenceMatcher + fixed weights | Candidate pair features → recommendation/ranking score | Human decision protects against auto merge. No learned model, no accuracy metric. | Real heuristic, not ML. |
| Temporal leads | deterministic policy rules | events + graph + evidence → signals/lead | Explainable and reproducible. Wrong/incomplete data changes result; limitations shown. | Real analytics, not AI. |
| Behavioral anomaly | sklearn Isolation Forest | five engineered features/entity → relative outlier score/rank | Useful triage when no labels. Wrong cohort/data creates misleading ranks; evidence and driver text shown. No held-out validation. | Real ML, weakly validated. |
| Semantic search / embeddings / LLM / GNN | none | — | — | Missing; never claim. |

“AI-powered” can honestly mean hybrid NLP + unsupervised anomaly module, but core safety/value currently comes from deterministic graph analytics and human review. Do not market every component as AI.

---

# PART 3 — Database and graph architecture

- JSON (`backend/data/demo/*.json`): canonical synthetic seed case, loaded and referentially validated once by `DemoRepository`.
- SQLite intake DB: entire current intake state and uploaded contents as JSON snapshot plus outbox.
- SQLite resolution DB: append-only decisions.
- SQLite review DB: lead reviews and application audit journal.
- NetworkX: transient in-process computation for path, transfer connectivity and clustering.
- Cytoscape: browser visualization only.
- Neo4j: **not used at all.**

NetworkX does algorithms in this project; it does not persist graph. SQLite/JSON persist prototype state; neither provides native graph traversal/indexes. Graph is recreated/deep-copied and canonicalized on many API requests, then serialized fully to frontend. Cytoscape recreates elements when the entity/edge signature changes.

Could NetworkX be removed? Not without reimplementing three calculations. Could Neo4j be removed? It already does not exist. Adding Neo4j before scale evidence is unnecessary; at larger scale replace request-time deep copies/full graph transfer with durable normalized stores, indexed graph queries, cached projections and background computation.

Architectural flaw: three SQLite stores plus base JSON lack a single transaction/case boundary. Cross-store audit uses an outbox mirror for intake, but resolution/review/base projection are not one atomic case model. `api/index.py` places DBs in `/tmp`; hosted state is ephemeral and not multi-instance consistent.

---

# PART 4 — Backend/API audit

Framework FastAPI; validation Pydantic plus manual source bounds. Important endpoints are case, sources, graph, leads/signals, evidence, path, resolution proposals/decisions/undo, upload/process/records/claims, reviews, audit/timeline and hidden anomalies. DB access is synchronous `sqlite3`; graph/ML computation is synchronous in request handler; no external AI API.

| Severity | Fundamental weakness | Why |
|---|---|---|
| 🔴 Critical for real data | No authentication/authorization; all evidence/source contents/reviews/reset/create endpoints open. | Any reachable user can read sensitive PII, alter decisions or reset state. |
| 🔴 Critical | No case isolation; most routes hard-code `/cases/demo` and `repository.case.id`. | Multi-user/multi-case security and correctness impossible. |
| 🟠 Serious | `/api/cases/demo/source-files` exposes full uploads and hidden administrative demo endpoints have no authorization. | Data exfiltration and demo manipulation. |
| 🟠 Serious | Sync Isolation Forest, deep-copy/project, full graph serialization per request. | Event loop/thread resources can be exhausted; latency grows with graph. |
| 🟠 Serious | Dynamic/current proposal map is inconsistently mixed with import-time `matches`. | New intake decisions/audit can diverge. |
| 🟠 Serious | Three stores + JSON have no unified transaction/version snapshot. | A response may mix graph/lead/review states across revisions. |
| 🟡 Moderate | No rate limiting, request concurrency limits, CSRF protection or security headers. | DoS/state-changing browser requests. Same-origin JSON helps but is not auth. |
| 🟡 Moderate | Validation errors expose field rules but not stack traces. | Acceptable; avoid detailed internal exception strings in production. |
| 🟢 Good | Upload envelope 400 KB; actual file 64 KiB; filenames restricted; binary controls rejected; no filesystem path use. | Malformed/huge-file risk meaningfully bounded for demo. |
| 🟢 Good | No arbitrary execution, pickle, shell, unsafe Cypher/SQL interpolation found. | Query values parameterized. |

---

# PART 5 — Frontend / UX audit

What judge can expose:

- Anomaly view says “Minimum 6 required for statistically valid isolation forest triage.” This is overclaiming; N=6 is only a code guard, not statistical validation. Change to “minimum prototype execution threshold.” **FIX NOW.**
- Fixed Cytoscape anchor positions create a curated narrative. Algorithm does not use them, but say layout is deterministic presentation, not analytical discovery.
- All `recorded` edges can include UNVERIFIED machine claims. Dashed styling exists, but path emphasis can visually override uncertainty. Add aggregate warning.
- Full graph sent/rendered; at thousands of nodes it becomes unreadable before backend necessarily fails. Add server-side subgraph/query mode later.
- “Re-run engine” recomputes synchronously but has no job/progress/version comparison.
- Hidden case/create/load-demo endpoints and archived case cards can look functional beyond actual multi-case support. Never demo archived cases as real persisted workspaces.
- Frontend does not compute analytics; this is good. It formats/filter/presents backend outputs.

---

# PART 6 — Mock / hardcoded / fake functionality

| Feature shown | Real / Partial / Mock | Where | Risk |
|---|---|---|---|
| Operation Trinetra dataset | Synthetic fixture | `backend/data/demo`, generator | Safe only if labelled synthetic. |
| Graph visualization | Real over seeded + intake graph | `Graph.tsx`, graph endpoint | Curated preset positions may look discovered. |
| Rahul–Vikram path | Real computation on seeded topology | `demo_paths.py` | Dataset planted; path is not proof. |
| Lead 17 | Real deterministic calculation over planted events | `lead_engine.py` | Story is seeded; no population validity. |
| Resolution proposals | Real heuristic on seeded/current nodes | `resolution.py` | Weights/thresholds uncalibrated; partial stale-global bug. |
| spaCy NER | Real if model installed | `ner_service.py` | Fallback gazetteer contains demo names; deployment may run fallback. |
| Report relationship extraction | Partial deterministic templates | `intake_parser.py:204+` | Arbitrary prose will mostly become UNSUPPORTED. |
| Anomaly profiles | Real Isolation Forest | `behavioral_profiler.py` | Tiny cohort and no validation; rank can be mistaken for danger. |
| Audit identity | Mock/self-declared | `Local demo session`, review form | Not authenticated attribution. |
| Archived case list | Static display objects | `main.py:119–126` | Never call it a real case repository. |
| “Load demo report” | Hard-coded sample endpoint | `main.py:218+` | Explicit demo convenience, not ingestion connector. |
| Fresh case | Partial | `create_case`, `augment` | Same global API/stores; not secure multi-case lifecycle. |
| Timeline | Real projection | `activity.py` | Mixes source time, replay signal time, and wall-clock action time; categories correctly label them. |
| Centrality/community/influencer | Missing | — | Direct PS gap. |
| Neo4j/graph persistence | Missing | — | Never claim. |

Never misrepresent synthetic fixtures, fallback whitelist, static archived cases, self-declared reviewer, or fixed resolution weights as production intelligence.

---

# PART 7 — Security and privacy

## Must fix before internal hackathon

1. Put a clear always-visible “Synthetic demo / no real PII” boundary and do not upload real data.
2. Disable or gate `/source-files`, `/load-demo-report`, reset and create-case helpers outside demo mode.
3. Add a demo access gate or bind local-only; current local launcher binds `127.0.0.1`, which is good. Do not present public deployment as secure.
4. Fix dynamic `matches` inconsistency and label audit actor as unauthenticated demo identity.
5. Add unverified-path warning and revise statistical-validity wording.

## Production requirements, honest future work

OIDC/MFA, RBAC/ABAC per case, least privilege, tenant/case isolation, TLS, encryption at rest/KMS, immutable evidence store with hashes/signatures, malware sandbox/OCR isolation, audit export/SIEM, data minimization, retention/legal-hold/deletion workflows, purpose limitation, consent/legal authority, redaction, backups/DR, rate limits, secure headers/CSRF, secrets manager, dependency/SBOM scans, monitoring, incident response and model/data governance.

No plaintext secret or API key was found in active source. No external API key is required.

---

# PART 8 — Scale test

| Scale | Likely behavior |
|---|---|
| 100 nodes | Comfortable; current architecture appropriate. |
| 1,000 nodes | NetworkX path fine; request-time deep copies, repeated lead/anomaly computation and Cytoscape labels begin to feel slow/cluttered. |
| 10,000 nodes | Full JSON graph and browser layout/rendering become primary UX bottlenecks; Isolation Forest/features and repeated graph construction add seconds/memory; SQLite JSON snapshot rewriting is poor. |
| 100,000 nodes | Full response/browser graph unusable; deep-copy memory amplification and O(V+E) graph builds per request unacceptable. Need server-side neighborhood queries/caches/jobs. |
| 1M relationships | Python object overhead likely hundreds of MB to >1 GB across repository/deep copies/NetworkX, plus serialization. SQLite monolithic JSON update and single-process compute are architectural blockers. |

Complexities: BFS O(V+E) within reachable region; clustering can approach O(sum degree²) depending topology; transfer grouping repeatedly constructs window graphs and can degrade roughly quadratic in transfer count; temporal burst currently uses nested scan per entity, potentially O(events²); frontend rebuild/full serialization O(V+E). Isolation Forest training approximately O(trees × samples × log samples) after feature extraction, but feature extraction and graph construction dominate.

Judge answer: “Our MVP deliberately optimizes auditability on case-sized synthetic data. For deployment we would benchmark authorized workloads, normalize evidence/events in durable relational/object storage, persist/index graph adjacency in a graph-capable store, compute ingestion and heavy analytics asynchronously, cache versioned projections, and send only filtered neighborhoods/subgraphs to Cytoscape. We would retain the evidence IDs and API contracts while swapping storage/execution. We do not claim the current NetworkX/SQLite process handles national scale.”

---

# PART 9 — Real-world failure scenarios

| Scenario | Current behavior | Ideal | Classification / judge line |
|---|---|---|---|
| Same exact name, two people | Source-local Person IDs keep them separate; heuristic may propose if block/features match. | Add DOB/address/temporal assets, negative constraints and human review. | Prototype limitation; conservative split is intentional. |
| One person, 3 aliases | Likely 3 nodes; only candidate pairs matching block/shared assets appear. | Alias graph, transliteration, multi-field probabilistic linkage with calibrated review. | Serious coverage gap. |
| Shared family phone | Strong 0.6 feature can recommend merge with similar name. | Phone ownership time ranges and shared-asset semantics. | Fundamental identity risk; never auto-merge. |
| OCR wrong phone | PDF/OCR unsupported; if wrong shaped value enters text it becomes real-looking UNVERIFIED entity. | OCR confidence, source image span, validation and reviewer correction. | Explain unsupported; do not upload OCR as trusted. |
| Legitimate merchant in 500 transactions | Hub/outlier/path prominence likely; no legitimate-role suppression. | Entity role/type baselines, allowlist/context and reviewer disposition. | False-positive risk; signal ≠ guilt. |
| Missing records | Paths/signals disappear or baseline is biased; diagnostics catch incomplete evidence references, not missing real-world data. | Coverage/completeness indicators and uncertainty propagation. | Inherent limitation; explicitly state. |
| Huge/malformed upload | 400 KB envelope, 64 KiB/file, max 16, strict CSV/control checks reject it. | Streaming object store, sandboxed parsing and quotas. | Good MVP mitigation. |
| Central node is officer/provider | Could rank anomalous once active; currently no influencer view. | Role-aware exclusions/peer cohorts and disclosure. | Must solve before influencer claim. |
| Meaningless shortest path | Returned because all edges cost one and types/times ignored. | Typed/time-respecting constrained paths and evidence-strength cost. | Serious semantics limitation; call it association path. |
| NER wrong entity | UNVERIFIED mention/node; exact relationship only if grammar fits; evidence visible. | confidence, correction UI, model evaluation/version rollback. | Acceptable MVP with human review, not auto-trust. |

---

# PART 10 — Hostile SIH judge test

| Rank | Rejection argument | Severity | 5-day? | Decision |
|---:|---|---|---|---|
| 1 | Official “key influencer” requirement missing | 🔴 | Yes, bounded | FIX NOW |
| 2 | Arbitrary unseen prose does not produce useful relations | 🔴 | Partial | MITIGATE |
| 3 | No auth/RBAC for sensitive investigation data | 🔴 | Demo gate yes; full no | MITIGATE |
| 4 | No held-out accuracy/false-positive metrics | 🔴 | Yes, synthetic held-out | FIX NOW |
| 5 | Identity weights can merge namesakes/shared-phone users | 🔴 | Calibration partial | MITIGATE |
| 6 | Strongest lead is planted scenario-specific evidence | 🟠 | Demo unseen case | MITIGATE |
| 7 | Isolation Forest N≈small and “valid” wording overclaims | 🟠 | Yes | FIX NOW |
| 8 | Unverified extracted edges participate in paths | 🟠 | Yes | FIX NOW |
| 9 | Dynamic proposals mixed with stale global `matches` | 🟠 | Yes | FIX NOW |
| 10 | No Neo4j/durable graph; request-time rebuild | 🟠 | Architecture answer | EXPLAIN |
| 11 | Public/serverless SQLite state is ephemeral | 🟠 | Maybe | EXPLAIN |
| 12 | No multi-case isolation/lifecycle | 🟠 | No | EXPLAIN |
| 13 | Exact schemas/dictionaries reject ordinary agency exports | 🟠 | Partial | MITIGATE |
| 14 | Report English templates are brittle | 🟠 | Partial | MITIGATE |
| 15 | No contradiction management/confidence propagation | 🟡 | Partial | EXPLAIN |
| 16 | Path treats every edge equal and undirected | 🟡 | Yes, filters/wording | MITIGATE |
| 17 | Fixed graph layout makes demo feel staged | 🟡 | Yes | EXPLAIN |
| 18 | Audit is mutable DB and reviewer self-declared | 🟡 | Full no | EXPLAIN |
| 19 | 559 KB frontend chunk, full-graph rendering | 🟢 | Optional | IGNORE FOR NOW |
| 20 | PDF/OCR/social/criminal DB connectors absent | 🟢 | No | EXPLAIN scoped MVP |

Five rejection-grade today: 1, 2, 4, 5, 7/8 combined. Five most likely questions: hardcoded/new data, AI exact role, influencer method, entity-resolution accuracy, false accusation/security. Solvable in five days: influencer card, held-out evaluation, stale `matches`, unverified path warning, anomaly wording; a controlled unseen demo can also be added if scope is disciplined.

---

# PART 11 — Weakness decisions

- **FIX NOW:** missing influencer analysis; stale/current proposal inconsistency; unverified path summary; anomaly “statistically valid” overclaim; held-out evaluation.
- **MITIGATE:** narrow templates, false identity merges, no auth (demo gate/local-only), path semantics, role-aware false positives.
- **EXPLAIN:** synthetic data, NetworkX/SQLite scale, no Neo4j, no PDF/OCR, mutable demo audit, deterministic lead rules.
- **IGNORE FOR NOW:** bundle code splitting, enterprise queue/observability, GNN/link prediction, chatbot, pixel polish.

---

# PART 12 — Learning roadmap

## LEVEL 1 — MUST KNOW

Actual end-to-end data flow; REST/FastAPI/Pydantic; evidence vs claim vs signal vs decision; typed nodes/edges; source-asserted vs verified; NetworkX path semantics; deterministic lead thresholds; entity-resolution blocking/scoring/human confirmation; spaCy NER vs regex relations; Isolation Forest meaning and limitations; false positives; JSON/SQLite/NetworkX roles; no Neo4j; authentication/security boundary; synthetic/unseen-data limitation.

## LEVEL 2 — SHOULD KNOW

BFS complexity, directed vs undirected and weighted paths; canonical projection; normalization and false merge/split; baseline median and zero days; connected transfer windows; provenance/custody; anomaly features/IQR/entropy/clustering; idempotency/revisions/outbox; sync request bottlenecks; multi-case/RBAC architecture; evaluation precision/recall.

## LEVEL 3 — NICE TO KNOW

Graph DB migration, constrained temporal paths, PageRank/betweenness/community algorithms, calibration, entity-resolution pair metrics, asynchronous jobs, object storage, KMS, tamper-evident logs, graph sampling/virtualization, multilingual NER/domain fine-tuning.

---

# PART 13 — Must-know concepts using this project

## FastAPI + REST

### Simple Hinglish definition
Frontend aur backend ke beech HTTP contract; resource ko URL/method se request karte hain.
### OUR project
`backend/main.py` JSON endpoints expose karta hai; `frontend/src/api.ts` fetch karta hai.
### Before / after
User action → fetch/POST → Pydantic validation → repository/algorithm → response → React state/render.
### Why / alternative / limitation
Fast, typed Python prototype. Alternative Flask/Django/Node. Current sync handlers and hard-coded demo case scale/multi-user limitation hain.
### Judge question / ideal answer
“Validation?” — “Pydantic request/response contracts plus manual bounded upload checks; domain errors normalized. Valid schema correct evidence hona guarantee nahi karta.”
### Memory trick
**API contract hai, intelligence nahi.**

## Parsing and validation

### Simple Hinglish definition
Raw file ko records mein todna aur format/range rules check karna.
### OUR project
`intake_parser.parse/validate_row`; exact headers, phone/timestamp/money rules.
### Before / after
Uploaded text → validated `Record` → mentions/claims.
### Why / alternative / limitation
Deterministic and reproducible; schema mapper/ETL alternative. Real messy data coverage narrow.
### Judge question / ideal answer
“Any FIR upload?” — “No. MVP supports controlled UTF-8 CSV/TXT contracts; unsupported prose is retained without inventing relationships.”
### Memory trick
**Reject ambiguity before graph authority.**

## NER (spaCy)

### Simple Hinglish definition
Text mein named Person, Organization, Location spans identify karne wala statistical NLP model.
### OUR project
`ner_service.extract`, model `en_core_web_sm`; structured IDs always regex.
### Before / after
Report line → spaCy entities → `Mention`; exact grammar separately builds `Claim`.
### Why / alternative / limitation
Names vary, so NER useful; dictionaries/regex/LLM alternatives. Small English model domain/multilingual accuracy unproven.
### Judge question / ideal answer
“NER relation banata hai?” — “No. NER named spans extracts; current relation extraction deterministic templates use karti hai. Every output UNVERIFIED and evidence-linked hai.”
### Memory trick
**NER noun batata hai, relationship proof nahi.**

## Entity resolution

### Simple Hinglish definition
Do mentions same real-world entity hain ya nahi, iska cautious matching workflow.
### OUR project
`resolution.py`: block → feature score → human decision → reversible canonical projection.
### Before / after
Separate Person nodes → proposal/evidence → confirm → graph query sees canonical node; originals preserved.
### Why / alternative / limitation
Cross-source activity join karne ke liye; probabilistic/embedding/master-data alternatives. Fixed uncalibrated weights and shared assets risk.
### Judge question / ideal answer
“99% means certainty?” — “No, 0–100 ranking score hai, probability nahi. YES recommendation bhi auto-merge nahi karti.”
### Memory trick
**Suggest, show evidence, human decides, undo possible.**

## Graph / node / edge

### Simple Hinglish definition
Entity node hai; source-asserted connection typed edge hai.
### OUR project
Person/Phone/Account/Vehicle/Location/Organization nodes; CALLED/TRANSFERRED_TO/etc. edges with evidence IDs.
### Before / after
Claims → repository relationships → NetworkX/Cytoscape → investigator path/evidence.
### Why / alternative / limitation
Multi-hop links natural hain; relational joins alternative. Edge truth/quality/type/time ignore karke graph misleading ho sakta hai.
### Judge question / ideal answer
“Edge criminal link?” — “No, typed source assertion; verification and exact source shown.”
### Memory trick
**Edge association hai, accusation nahi.**

## NetworkX shortest path

### Simple Hinglish definition
Memory graph mein minimum-hop association chain find karta hai.
### OUR project
`compute_path`: recorded edges, undirected MultiGraph, cutoff 8, equal cost, stable edge choice.
### Before / after
Canonical graph + source/target → BFS → nodes/steps/evidence → Cytoscape highlight.
### Why / alternative / limitation
Small MVP and explainability. Neo4j query/custom weighted traversal alternatives. Equal-cost undirected path semantically weak.
### Judge question / ideal answer
“Shortest means strongest?” — “No. Sirf fewest recorded association hops. Direction per step and evidence shown; causation claim nahi.”
### Memory trick
**Shortest hops ≠ strongest truth.**

## Deterministic temporal lead engine

### Simple Hinglish definition
Fixed, readable policy thresholds se review lead generate hota hai.
### OUR project
`lead_engine.run_engine`: burst, new contacts, connected transfers, graph context; ≥2 categories needed.
### Before / after
Validated traceable events → signals → lead priority/revision → human review.
### Why / alternative / limitation
Auditable and reproducible; supervised model alternative needs labelled data. Thresholds externally validated nahi.
### Judge question / ideal answer
“HIGH means crime?” — “No, three traceable operational categories fired; it sets review order only.”
### Memory trick
**Rule triggers attention, not guilt.**

## Isolation Forest

### Simple Hinglish definition
Unsupervised model jo rare feature combinations ko tree isolation ke through rank karta hai.
### OUR project
Five features/entity, 100 trees, `contamination=auto`, seed 42; evidence-backed profile.
### Before / after
Events/graph → engineered vector → relative score/outlier → anomaly UI.
### Why / alternative / limitation
Labels absent ho to triage; z-score/rules/LOF alternatives. Tiny mixed cohort, no calibration or ground truth; min-max score case-relative.
### Judge question / ideal answer
“87% criminal probability?” — “Bilkul nahi. Ye within-case relative anomaly percentile/rank hai.”
### Memory trick
**Unusual ≠ unlawful.**

## Provenance and explainability

### Simple Hinglish definition
Har displayed assertion/result ka source, location, calculation and limitation trace hona.
### OUR project
Evidence IDs, excerpt/row/span/parser version; lead calculations and review history.
### Before / after
Source record → evidence reference → edge/signal → one-click inspector.
### Why / alternative / limitation
Investigative trust and contestability. Current custody/hash/audit immutability incomplete.
### Judge question / ideal answer
“A-B connection proof?” — “Path ke har hop ka source assertion and exact excerpt dikha sakte hain; path itself coordination prove nahi karta.”
### Memory trick
**Click result, reach record.**

## Storage: JSON + SQLite + NetworkX

### Simple Hinglish definition
Persistence aur computation alag layers hain.
### OUR project
JSON seed data; SQLite intake/decisions/audit; NetworkX transient algorithms.
### Before / after
Stored records → in-memory projection → calculation → JSON response.
### Why / alternative / limitation
Offline deterministic MVP. Graph DB/durable relational-object architecture later. Multi-store atomicity and scale weak.
### Judge question / ideal answer
“Neo4j?” — “Current code mein nahi. NetworkX computation karta hai; graph persists as JSON/SQLite-derived records.”
### Memory trick
**Store ≠ graph algorithm ≠ browser drawing.**

## Authentication/authorization

### Simple Hinglish definition
Authentication “kaun”; authorization “kya dekh/change kar sakta hai.”
### OUR project
Absent; reviewer self-declared and local demo session.
### Before / after
Production mein login/token → case/role policy → endpoint/data filter → audited action.
### Why / alternative / limitation
Sensitive PII ke liye mandatory. Local synthetic demo only is acceptable if honestly scoped.
### Judge question / ideal answer
“Secure?” — “Current build synthetic local POC hai, production security claim nahi. Deployment before real data requires OIDC/MFA, RBAC/ABAC, case isolation, encryption and tamper-evident audit.”
### Memory trick
**No auth means no real case data.**

---

# PART 14 — Actual data flow example

Sentence: **“Rahul called Aman from phone X and ₹50,000 was transferred to account Y.”**

1. Input: Report TXT JSON envelope can receive this line.
2. Parsing: becomes one VALID Report `Record`; there is no grammatical validation.
3. Validation: UTF-8/size/name/type checked only.
4. Extraction: spaCy may extract Rahul/Aman; current phone regex requires actual `+` and 10–15 digits, account requires `DEMO-A...`, money requires literal `INR 50000`, so “phone X”, “₹50,000”, “account Y” are not structured matches.
5. Entity objects: Person mentions may become source-scoped UNVERIFIED nodes. Results depend on spaCy; generic placeholders will not become Phone/Account.
6. Relationship: sentence matches none of the exact full-line templates. One `UNSUPPORTED` claim with null subject/object is created. **No CALLED or TRANSFERRED_TO edge.**
7. Storage: record, mentions and unsupported claim stored in intake SQLite snapshot; exact excerpt becomes evidence.
8. Graph nodes: only recognized named entities may appear; structured placeholders do not.
9. Graph edges: none from this sentence.
10. Algorithm: path/lead engine receives no call/transfer events from this Report record.
11. Intelligence: no lead caused by this sentence.
12. API response: processing summary increments mentions and withheld claims; extracted claims shows UNSUPPORTED.
13. Frontend: Data Sources/Report Intelligence shows record/entities and withheld status; graph may show isolated Person nodes.
14. Investigator: sees exact source line but no asserted relationship.

This is safe but narrow. To demonstrate successful current behavior use structured CDR and Transaction CSV rows, not that natural sentence. **Do not claim current system understands it end-to-end.**

---

# PART 15 — Judge defense sheet (40)

| Judge asks | Testing | My concise answer | Technical backup |
|---|---|---|---|
| 1. What did you build? | Clarity | Controlled evidence → typed graph → explainable leads → human review prototype. | `main.py`, `NetworkWorkspace.tsx` |
| 2. Is graph hardcoded? | Authenticity | Seed data is synthetic; graph/path APIs and intake augmentation are real computations. | `DemoRepository`, `augment`, `compute_path` |
| 3. Is Lead 17 hardcoded? | Authenticity | Scenario planted hai, output `run_engine` events se computes; fixture lead file runtime reads nahi. | `lead_engine.py` |
| 4. AI exactly where? | Honesty | spaCy NER and Isolation Forest; resolution/leads/path deterministic. | `ner_service.py`, `behavioral_profiler.py` |
| 5. Why not LLM? | Design | Structured evidence needs reproducibility; unsupported text withheld rather than hallucinated. | parser claim dispositions |
| 6. What if NER wrong? | Safety | UNVERIFIED, evidence-linked; exact relation grammar and human review limit propagation. | `intake_parser.extract` |
| 7. NER accuracy? | Validation | Not measured on real FIRs; this is a limitation. We need labelled held-out corpus. | honest scope |
| 8. Entity resolution how? | Depth | NFKC/name similarity + phone + vehicle, human confirmation and undo. | `resolution.py` |
| 9. Score probability? | Misuse | No, ranking score from fixed weights. | UI/README caveat |
| 10. Same name? | Failure | Source-local nodes remain separate unless evidence-backed human merge. | person ID hashing |
| 11. Shared phone? | Failure | It can over-score; never auto-merges; temporal ownership is future improvement. | phone weight 0.6 |
| 12. False merge impact? | Systems thinking | Combines edges/events and can distort path/leads/anomaly. Undo restores projection. | `project`, decision store |
| 13. Edge created how? | Semantics | Explicit structured row or supported report template; co-occurrence alone is not edge. | parser templates |
| 14. Negation? | NLP safety | NEGATED retained, never positive graph candidate. | `Claim.disposition` |
| 15. Relationship confidence? | Honesty | No calibrated confidence; status, extractor and evidence shown. | Relationship schema |
| 16. Path algorithm? | Graph depth | NetworkX unweighted undirected bounded BFS, max 8. | `demo_paths.py` |
| 17. Shortest = strongest? | Misinterpretation | No, minimum hops only; edge type/time/quality equal. | method behavior |
| 18. Direction? | Correctness | Traversal undirected, each step says forward/reverse relative to source edge. | `Step.traversal` |
| 19. PageRank? | Honesty | Not implemented today. Influencer analysis is P0. | no active code |
| 20. Central person = mastermind? | Safety | Never; centrality only network position and needs role/evidence context. | planned wording |
| 21. Community = gang? | Safety | No; dense graph partition only. | not implemented |
| 22. Temporal lead? | Depth | Burst + new contacts + connected transfers + graph context with evidence gates. | `Policy`, `run_engine` |
| 23. HIGH priority? | Misuse | Three distinct traceable categories; not guilt probability. | `priority_for` |
| 24. New contact? | Data limits | New only relative to previous seven days in available case records. | `historical_counts` |
| 25. Money laundering detected? | Overclaim | No; weakly connected transfers within 90 minutes trigger review. | `transfer_sequences` |
| 26. Isolation Forest input? | ML depth | Five engineered behavioral/graph features per active entity. | feature definitions |
| 27. Anomaly score meaning? | ML safety | Relative cohort rarity, min-max normalized; not risk/guilt probability. | profiler scoring |
| 28. Why fixed seed? | Reproducibility | Judge/demo output deterministic; not accuracy improvement. | random_state 42 |
| 29. N=6 valid? | Statistics | Only prototype execution guard; not scientific validation. | fix wording |
| 30. Evidence trace? | Trust | Every lead signal/path edge opens exact source row/span/excerpt. | Evidence API |
| 31. Audit immutable? | Honesty | Append-only through app, not cryptographically tamper-resistant. | `review_store.py` |
| 32. Reviewer identity? | Security | Self-declared/local demo, not authenticated. | Review input/UI |
| 33. Database? | Architecture | JSON seeds + three SQLite state stores; NetworkX transient. | repository/stores |
| 34. Neo4j? | Architecture | Not used. It is a possible scale migration, not current feature. | dependencies/code |
| 35. Why NetworkX? | Tradeoff | Low-ops, real algorithms, deterministic case-scale MVP. | three active uses |
| 36. Scale? | Feasibility | Current full in-memory graph is case-scale; production needs durable graph indexes, jobs, caches and subgraphs. | architecture plan |
| 37. 1M edges? | Honesty | Current design not credible; deep copies/NetworkX/serialization/browser fail first. | complexity |
| 38. Security? | Trust | Synthetic-only POC; no real data until auth/RBAC/isolation/encryption/audit controls. | missing middleware |
| 39. Innovation? | Differentiation | Evidence-first, contestable AI workflow: result → calculation → original record → reversible human decision. | end-to-end UI |
| 40. Biggest limitation? | Maturity | Generalization and validation: controlled formats, synthetic cohort, no real accuracy/user study. | audit verdict |
| 41. Why useful vs graph tool? | Value | It preserves epistemic states and investigator decision flow, not only visualization. | claims/signals/reviews |
| 42. What happens on missing data? | Honesty | Graph/signals may disappear or bias baseline; absence is not treated as real-world absence. | limitations/diagnostics |
| 43. Fresh uploads update system? | Integration | Graph/events do; resolution/audit path has a current-vs-global inconsistency we will fix before claiming full dynamic workflow. | `current_matches` vs `matches` |
| 44. Production deployment? | Feasibility | API/contracts retained; storage, identity, graph query and jobs replaced with governed services. | phased plan |

---

# PART 16 — Things I must never say

| Never say | Say instead |
|---|---|
| “Neo4j creates graph; NetworkX stores it.” | “Neo4j is not used. JSON/SQLite-derived records persist; NetworkX computes in memory; Cytoscape renders.” |
| “AI finds criminals.” | “AI/statistical modules surface unverified entities and unusual behavior for human review.” |
| “PageRank finds mastermind.” | “PageRank is not implemented; even if added it measures link-based prominence, not guilt or leadership.” |
| “Shortest path is strongest connection.” | “It is minimum equal-cost hops among recorded/source-asserted associations.” |
| “99 score = 99% same person.” | “It is an uncalibrated weighted ranking score.” |
| “High priority means high crime probability.” | “It means more distinct transparent signal categories fired.” |
| “Isolation Forest predicts criminal behavior.” | “It ranks feature combinations unusual within the current case cohort.” |
| “Our NER understands FIRs.” | “Small English spaCy NER extracts selected entity types; relation grammar is controlled and unvalidated on real FIRs.” |
| “Every edge is verified.” | “Every edge is evidence-linked; uploaded machine assertions remain UNVERIFIED.” |
| “Audit log cannot be changed.” | “Normal app flow appends; database is not cryptographically tamper-evident.” |
| “System supports any file.” | “Controlled UTF-8 CSV/TXT only; no PDF/OCR.” |
| “Graph DB is always faster.” | “Choice depends on workload; current case-scale NetworkX reduces ops, production needs benchmarks.” |
| “One million edges will work.” | “Current architecture is not designed for it; we have a migration plan.” |
| “Reviewer is authenticated.” | “Reviewer identity is self-declared in synthetic local demo.” |
| “Temporal proximity proves coordination.” | “It is a reviewable correlation; alternative benign explanations remain.” |

---

# PART 17 — 30-question oral viva (answers intentionally omitted)

1. VEIL ka one-sentence problem and one-sentence solution kya hai?
2. User upload se graph screen tak exact modules ka flow batao.
3. Evidence, claim, relationship, event, signal, lead and review mein difference kya hai?
4. Current supported file types and hard limits kya hain?
5. CDR row validate hote waqt kya checks lagte hain?
6. Report line aur CSV row parsing ka difference kya hai?
7. spaCy NER exactly kaunse entity types extracts karta hai?
8. NER unavailable ho to kya hota hai, aur UI ko kya claim karna chahiye?
9. NER entity extract karna aur relationship extract karna different kyun hai?
10. Same Person name different files mein initially alag node kyun banta hai?
11. Entity-resolution candidate blocking, scoring and decision flow explain karo.
12. Shared phone false merge kaise kara sakta hai?
13. Confirmed merge original evidence ko delete kyun nahi karta?
14. Current `matches` vs `current_matches()` inconsistency kya impact daal sakti hai?
15. Graph edge ka source and verification status kaise trace karoge?
16. Negated/uncertain report statement graph mein kyun nahi jata?
17. NetworkX `MultiGraph` kyun, and parallel edges ka selection kaise hota hai?
18. Undirected traversal aur directed evidence edge mein difference kya hai?
19. Shortest path ko criminal connection bolna dangerous kyun hai?
20. Communication burst exact threshold formula kya hai?
21. Baseline mein zero-call days include karne ka effect kya hai?
22. Connected transfer sequence money laundering kyun prove nahi karti?
23. HIGH lead priority ka exact meaning kya hai?
24. Isolation Forest ke five input features batao and each ka limitation do.
25. Anomaly percentile probability kyun nahi hai?
26. N=6 model validity prove kyun nahi karta?
27. JSON, SQLite, NetworkX and Cytoscape ki separate responsibilities batao.
28. 100k nodes par first three bottlenecks kya honge?
29. Real police data accept karne se pehle minimum security architecture kya hogi?
30. Judge agar kahe “ye seeded demo hai, real intelligence nahi,” to code evidence, limitation and next validation step ke saath answer do.

---

# PART 18 — Current product scorecard

| Area | Score /10 | Reason |
|---|---:|---|
| Problem-solution fit | 7.0 | Core flow real; influencer requirement missing. |
| Technical correctness | 7.0 | Strong contracts/provenance/tests; semantic and stale-map issues. |
| Architecture | 6.0 | Cohesive MVP, but multi-store/global-demo boundaries. |
| Data pipeline | 6.0 | Safe controlled intake, narrow schemas/prose. |
| Graph modelling | 6.5 | Typed/evidenced edges; verification/time/role semantics incomplete. |
| Entity resolution | 5.0 | Reversible human control; uncalibrated fixed heuristic. |
| Algorithms | 6.0 | Correct bounded analytics; limited breadth and scenario anchoring. |
| AI/NLP validity | 5.0 | Real spaCy/Isolation Forest; no domain/held-out validation. |
| Explainability | 9.0 | Calculations, caveats and evidence navigation are excellent. |
| Evidence/provenance | 8.5 | Exact records and referential checks; custody/immutability absent. |
| Security | 2.5 | Synthetic/local only; no identity or authorization. |
| Scalability | 3.5 | Fine at demo size, architectural changes required beyond thousands. |
| UI credibility | 8.0 | Professional and cautious; anomaly/path authority cues need fixes. |
| Real-world feasibility | 4.5 | Plausible workflow, no agency connectors/validation/governance. |
| SIH judge defensibility | 6.5 | Honest team can defend; overclaiming is easily exposed. |

## Current overall score

**6.2/10**

## Internal hackathon readiness

**7.6/10** after the five P0 corrections below; approximately **6.8/10 now**.

## Real-world architecture credibility

**4.0/10**

## Probability a technical judge exposes a major weakness

**High**, because influencer identification, real-data generalization, calibrated evaluation and security are obvious questions. Exposure need not mean rejection if the answer is honest and P0 gaps are fixed.

---

# PART 19 — Final priority list

## P0 — Must fix before judges see it (maximum 5)

### 1. Add explainable influencer analysis

- **Problem:** direct PS requirement missing.
- **Danger:** judge can reject for incomplete problem fit.
- **Exact fix:** person-focused degree + betweenness (optionally PageRank), role-aware exclusions, top contributing paths/edges/evidence, label “network prominence / review aid,” never guilt. One card/table is enough.
- **Files:** new backend analytics/service/schema + `main.py`; new frontend view/card/types; tests.
- **Complexity:** medium, 1–2 focused days.
- **Verify:** hand-computed small graphs, disconnected/hub/service-provider cases, deterministic tie tests, every displayed reason opens evidence.

### 2. Fix dynamic entity-resolution consistency

- **Problem:** request-time `current_matches()` mixed with import-time `matches`.
- **Danger:** uploaded proposal can display but audit/merge-review/timeline use stale set.
- **Exact fix:** remove global `matches`; compute/persist one proposal snapshot/revision per operation and pass it to projection/audit/review.
- **Files:** `backend/main.py`, possibly `resolution.py`, tests.
- **Complexity:** low-medium, half to one day.
- **Verify:** upload unseen matching people, proposal decision, audit, lead review and timeline all reference same proposal; restart remains consistent.

### 3. Prevent unverified paths from looking verified

- **Problem:** `recorded` UNVERIFIED machine edges are traversed and highlighted.
- **Danger:** visual authority can imply proven criminal relationship.
- **Exact fix:** path summary counts verification states; persistent warning; filter or constrained “verified only / include unverified” option; preserve per-edge status.
- **Files:** `demo_paths.py` schema, `main.py`, `InvestigationInspector.tsx`, `Graph.tsx`, tests.
- **Complexity:** low-medium.
- **Verify:** path with one unverified edge visibly warns; verified-only returns alternate/no path; evidence still opens.

### 4. Correct anomaly validity and evaluate it

- **Problem:** N≥6 wording implies statistical validity; model/cohort unvalidated.
- **Danger:** ML judge will attack immediately.
- **Exact fix:** wording “prototype minimum execution threshold”; require sensible cohort size or show exploratory status; create benign hub/merchant/officer counterexamples and report stability/false-positive observations.
- **Files:** `behavioral_profiler.py`, `BehavioralAnomalyView.tsx`, `tests/test_anomaly.py`, evaluation artifact.
- **Complexity:** low for wording, medium for evaluation.
- **Verify:** no UI/API says probability/valid; repeated/perturbed cohorts; evidence and drivers remain correct.

### 5. Build a held-out unseen-case proof

- **Problem:** no accuracy/generalization evidence.
- **Danger:** seeded-demo accusation cannot be answered quantitatively.
- **Exact fix:** separate dataset not used in code constants; positives, negatives, namesakes, aliases, shared assets, negation, malformed rows, legitimate hubs. Measure extraction precision/recall, resolution pair precision/recall/false-merge rate, expected paths/signals and latency.
- **Files:** `demo-data/evaluation`, test/evaluation runner, concise results doc; reduce whitelist dependence.
- **Complexity:** medium, 1–2 days.
- **Verify:** clean reset; one command regenerates report; no test imports expected output into algorithm.

## P1 — Fix if time allows (maximum 5)

1. Demo-only access gate and disable source-file/admin helpers outside local demo mode.
2. Role/time-aware identifier ownership to reduce shared-phone/provider false positives.
3. Flexible header mapping and one additional unseen report grammar or reviewed relation UI.
4. Versioned case snapshot so graph, leads, proposals and reviews share one revision.
5. Benchmark 100/1k/10k nodes and document measured latency/memory/render limits.

## P2 — Learn/prepare answer, do not rebuild (maximum 10)

1. Why NetworkX, not Neo4j, for current case-scale MVP.
2. Why path is undirected/equal-cost and its semantic limit.
3. Why deterministic rules are preferable to unsupported “AI everywhere.”
4. spaCy model, fallback, and relation-template separation.
5. Isolation Forest features and “unusual ≠ unlawful.”
6. False merge vs false split and conservative human control.
7. Evidence provenance vs legal chain of custody.
8. Production auth/RBAC/encryption/isolation/retention roadmap.
9. Scale migration: durable stores, graph indexes, async jobs, cached subgraphs.
10. Synthetic data, no real-world accuracy, no PDF/OCR/connectors—honest MVP boundary.
