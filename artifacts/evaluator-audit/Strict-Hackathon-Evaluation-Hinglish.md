# Network Intel — Strict SIH + General Hackathon Evaluation

**Audit date:** 8 September 2026  
**Current product:** [Live prototype](https://veil-network-intel.vercel.app/)  
**Target SIH problem statement:** SIH26189 — AI-Powered Criminal Network Analysis System  
**Assessment basis:** actual repository, APIs, local and public product flows, scoped tests, production behavior, and official SIH sources.

## Executive verdict

Network Intel sirf impressive-looking UI nahi hai. Isme real FastAPI backend, controlled data ingestion, NetworkX graph traversal, deterministic lead detection, evidence provenance, rule-based entity resolution, Isolation Forest anomaly scoring, aur human-review audit workflow implemented hai.

Lekin current build winner-level system bhi nahi hai. Sabse bade gaps hain: official PS ka **key influencer identification** feature missing hai; public deployment ka Data Sources state graph se contradict karta hai; production NER unavailable hai; uploaded entities ke resolution proposals dynamically refresh nahi hote; real-world evaluation metrics nahi hain; frontend judge-flow automation stale hai; aur security/scalability sirf prototype-level hai.

Best truthful positioning:

> Network Intel ek working, explainable investigation-workflow prototype hai jo controlled synthetic records ko evidence-linked graph mein convert karta hai, connection paths aur temporal leads compute karta hai, source provenance preserve karta hai, cautious entity-resolution review support karta hai, aur human decisions record karta hai.

Isko production-ready law-enforcement platform, arbitrary document-understanding engine, calibrated criminal-risk model, ya proven accuracy system claim mat karo.

### Evidence and sources used

- Official PS text: [SIH 2026 Problem Statements — SIH26189](https://www.sih.gov.in/sih2026PS).
- Official judging context: [SIH 2024 College SPOC Guidelines](https://sih.gov.in/letters/Guidelines-College-SPOC.pdf), which lists novelty, complexity, clarity, feasibility, practicability, sustainability, impact scale, UX and future progression.
- Selectivity context only: [SIH 2025 official page](https://www.sih.gov.in/sih2025), listing 72,165 submissions and 1,360 Grand Finale teams. Ye current-team probability nahi hai.
- Code evidence: `backend/demo_paths.py`, `backend/lead_engine.py`, `backend/intake_parser.py`, `backend/intake_store.py`, `backend/resolution.py`, `backend/behavioral_profiler.py`, `backend/review_store.py`, `backend/main.py`, and `api/index.py`.
- Runtime evidence: public APIs, isolated local demo state, manual browser flow, and controlled parser/path perturbation probes.
- Validation: frontend build pass; lint pass; backend `tests/` suite 101 passed; current frontend Playwright suite 1 passed/3 failed. Repository-root pytest also collects vendored NumPy tests and fails because `hypothesis` is unavailable, so test discovery configuration needs cleanup.

---

## PART 1 — Product actually kya hai?

### Implemented

| Capability | Actual status | Evidence-based assessment |
|---|---|---|
| Backend/API | Working | FastAPI endpoints case, graph, path, leads, evidence, intake, anomaly, resolution aur review flows serve karte hain. |
| Controlled ingestion | Working within narrow scope | CDR, transactions, vehicles aur report text ke controlled formats parse hote hain; invalid rows reject hote hain. |
| Graph construction | Working | Entities aur sourced relationships se NetworkX graph banta hai. |
| Hidden path discovery | Working | Bounded BFS shortest paths run hote hain. Default 6-hop path fixture response ki tarah directly return nahi hota; edge change par alternate path milta hai. |
| Lead generation | Working on the designed scenario | Calls, new contacts, transfers aur graph context se deterministic lead compute hota hai. Events remove karne par lead count zero ho jata hai. |
| Evidence provenance | Strongly implemented | File, row/span, excerpt, parser version aur evidence IDs preserved hain; graph assertions evidence-linked hain. |
| Entity resolution review | Working for seeded proposals | Normalized name, shared phone aur vehicle signals use hote hain; confirm/reject/defer/undo human decision flow hai; source evidence retained hai. |
| Behavioral anomaly model | Working computation | Five engineered features par scikit-learn Isolation Forest run hota hai, fixed seed aur small-sample guard ke saath. |
| Human review/audit | Working locally | SQLite mein review events, resolution decisions, revisions aur idempotency state store hota hai. |
| Investigator UI | Working | Case Overview, Data Sources, Resolution, Network, Lead Inbox, Timeline, Audit Trail present hain. |

### Partially implemented

| Capability | Partial kyun hai? |
|---|---|
| AI/NLP extraction | Local environment mein spaCy NER available tha, lekin live deployment `available: false` return karta hai. Fallback fixed demo whitelists use karta hai. |
| Unstructured reports | Entities broader extract ho sakti hain, par graph relationships sirf kuch exact sentence templates se banti hain. Arbitrary police/FIR prose supported nahi hai. |
| New data → resolution | Upload aur graph augmentation work karta hai, par resolution proposals module import par ek baar compute hote hain. Fresh uploaded aliases proposal queue mein automatically nahi aate. |
| New data → lead discovery | Lead engine real hai, par key graph-context logic seeded source/target aur synthetic case scenario se anchored hai. |
| End-to-end verification | Manual/local flow ka large portion works, backend tests pass; current frontend judge-flow tests stale hain aur 4 mein se 3 fail hue. |
| Deployment | Public site accessible hai, par `/tmp` SQLite transient hai; state durable ya multi-user safe nahi hai. |
| Impact | Workflow plausible hai, par investigator time-saved, false-positive rate, precision/recall ya field feedback measured nahi hai. |

### Demo-only / hardcoded

| Item | Reality |
|---|---|
| Operation Trinetra | Fully synthetic, deterministic case fixture. |
| Default actors, accounts, phones, dates | Seeded narrative data. |
| Default Rahul → Vikram investigation | Predetermined demo question; path algorithm real hai. |
| NER fallback entities/locations/orgs | Fixed whitelist includes demo names and locations. |
| Report relation grammar | Exact patterns such as “uses phone”, “associated with vehicle”, “is located at”, plus an August-2026 meeting pattern. |
| Two entity-resolution candidates | Baseline repository se startup par generated; new intake ke saath current API process mein refresh nahi hote. |
| Lead 17 story | Output calculations real deterministic logic se aate hain, par scenario and replay clock seeded hain. |

### Future scope / currently absent

- Influencer or kingpin identification: PageRank, betweenness, centrality, community detection ya role ranking implemented nahi hai.
- Production data connectors for FIR databases, social media intelligence, criminal history systems, or agency feeds.
- Real-world labelled evaluation and calibrated thresholds.
- Dynamic resolution and lead recomputation for arbitrary newly uploaded cases.
- Durable graph/data platform, background jobs, queues, caching, multi-case scaling.
- Authentication, RBAC, case isolation, encryption/key management, rate limiting, tamper-evident audit trail.
- Field deployment, user study, measurable impact proof.

### Demo end-to-end verdict

**Partially working, fully verified nahi.** Local controlled synthetic flow credible hai. Public deployment mein same case overview 42 entities, 43 relationships aur 1 lead dikhata hai, lekin Data Sources tab 0 records aur “No sources loaded” dikhata hai. Is inconsistency ko judge seed-data theater samajh sakta hai. Backend ke scoped tests **101 passed**. Frontend suite mein **1 passed, 3 failed**, mainly renamed/stale UI locators ke karan. Build aur lint pass hue.

### Actual technical depth

**Moderate-to-good prototype depth.** Real graph traversal, provenance checks, review state, validation, heuristic resolution aur ML anomaly computation UI ke neeche exist karte hain. Depth ek simple LLM wrapper se kaafi better hai. Winner-level depth ko three gaps rok rahe hain: generalizable intelligence logic, measured evaluation, aur production architecture/security.

---

## PART 2 — SIH-specific assessment

Official SIH26189 asks for multi-source collection, entity extraction, relationship maps, key influential individuals, suspicious-pattern detection, and visual/analytical investigator insights. Current mapping:

| Official PS requirement | Coverage | Strict verdict |
|---|---|---|
| Multiple sources | Partial | Four controlled source types hain; actual agency/database connectors nahi. |
| People, locations, vehicles, phones, organizations extraction | Partial | Controlled parsing and local spaCy support; public NER unavailable; relation grammar narrow. |
| Relationship maps | Strong | Evidence-linked graph and interactive exploration are credible. |
| Key influential individuals | Missing | No centrality/community/influence algorithm. This is a direct PS gap. |
| Suspicious patterns/unusual activities | Partial-to-good | Deterministic temporal/financial lead rules and Isolation Forest exist, but real-world validation absent. |
| Visual and analytical insights | Strong prototype | Network, lead explanation, timeline and inspector coherent hain. |
| Actionable investigator intelligence | Partial | Review workflow strong hai, but public intake coherence and deployment/security weak hain. |

### SIH judging factors

| Factor | Verdict |
|---|---|
| Problem understanding | Team investigation workflow ko evidence → inference → review ke form mein achhi tarah samajhti dikhti hai. PS ke influencer requirement ko miss karna understanding score reduce karta hai. |
| Relevance to PS | Core problem solve hota hai, side project nahi. Coverage incomplete hai. |
| Innovation | Explainable evidence-linked workflow useful differentiation hai. Graph intelligence category khud mature hai; sirf dark UI + graph innovative nahi mana jayega. |
| AI/ML value | Isolation Forest real hai; NER partial hai. AI central differentiator abhi weak hai aur model-quality proof nahi hai. |
| Technical implementation | Real backend and algorithms exist. New-upload recomputation and E2E regression failures credibility reduce karte hain. |
| Feasibility | Small controlled pilot feasible hai. Agency-scale deployment, data access and governance unproven hain. |
| Scalability | Prototype-level. In-memory NetworkX, deep-copy/recompute behavior, SQLite and small upload caps. |
| Security/privacy | Synthetic demo ke liye acceptable; sensitive investigation data ke liye inadequate. No auth/RBAC/case isolation/tamper evidence. |
| Explainability | Current strongest dimension. Score labels, uncertainty notes, exact evidence and human decision separation strong hain. |
| User experience | Professional and task-oriented. Dense inspector views aur small text/contrast judge projection par risk hain. |
| Demo strength | Strong memorable path + evidence flow possible hai. Live Data Sources contradiction demo ko damage kar sakta hai. |
| Judge defence | Honest positioning ke saath defendable; exaggerated “AI-powered, scalable, production-ready” claims immediately expose honge. |
| Impact | Significant potential, par no measured investigator outcome. |
| Completeness | Cohesive seeded workflow; arbitrary case lifecycle abhi incomplete. |

Official historic SIH criteria include novelty, complexity, clarity, feasibility, practicability, sustainability, scale of impact, UX, and future progression. Isi liye score UI polish se zyada PS coverage, working proof, feasibility aur evidence ko weight karta hai.

---

## PART 3 — SIH scorecard (62/100)

Suggested weights retain kiye hain because total 100 hai aur SIH-style judging mein PS alignment, technical proof aur working implementation highest leverage hain.

| Area | Weight | Score | Reason | Strongest point | Biggest weakness | Exact improvement |
|---|---:|---:|---|---|---|---|
| Problem/PS alignment | 15 | **9** | Core investigation-network problem addressed hai. | Multi-source-to-graph workflow. | Key influencer identification missing; sources limited. | Official PS checklist screen/document banao and influence-ranking module implement karo. |
| Innovation | 10 | **5** | Explainability workflow useful hai, but graph-analysis products already exist. | Evidence → inference → human review framing. | Unique algorithmic moat unclear. | Novel claim ko “auditable investigator workflow” par center karo and comparator matrix substantiate karo. |
| Technical depth | 15 | **10** | Real path, lead rules, anomaly model, parser, stores and API. | Evidence-backed graph and deterministic lead computation. | Generalization, dynamic recomputation and evaluation weak. | Fresh unseen case pipeline + held-out test corpus add karo. |
| Working implementation | 15 | **10** | Core local product works; build/lint/backend tests pass. | Local interactive depth. | Public source state inconsistent; 3/4 frontend E2E tests fail. | Public seed/preflight fix karo and judge flow tests green karo. |
| Feasibility | 10 | **6** | Controlled pilot feasible. | Simple portable stack. | Data partnerships, governance, deployment ops missing. | Pilot architecture and realistic phased adoption plan with costs/data assumptions add karo. |
| Explainability & evidence | 10 | **9** | Exact sources, uncertainty, calculation and human review separation. | Product ka clearest competitive strength. | Audit chain tamper-evident nahi. | Evidence manifest hash/version plus exported review bundle demonstrate karo. |
| UX/demo quality | 10 | **8** | Professional, coherent investigation console. | Inspector and lead explanation visually strong. | Public contradiction; dense small text on projector. | 3-minute fixed demo mode, preflight indicator, larger presentation typography. |
| Scalability & architecture | 5 | **1** | Prototype stack beyond small case unproven. | NetworkX is sensible for POC. | `/tmp` SQLite, in-memory rebuilds, no multi-case scale. | Measured scale test + graph DB/durable storage migration design; one implemented durable state path. |
| Impact | 5 | **1** | Potential high, evidence low. | Manual relationship discovery pain is real. | No time-saved/user/accuracy measurement. | 5-user investigator-style study or structured expert review with before/after task timing. |
| Team/judge defence readiness | 5 | **3** | Architecture explainable and testable. | Honest limitations are already visible in product copy. | AI, hardcoding, accuracy, security questions can expose gaps. | Every risky claim ke liye code proof, metric, limitation and answer rehearse karo. |
| **Total** | **100** | **62** | **Technically real, visually strong prototype; current national-winning case incomplete.** |  |  |  |

---

## PART 4 — SIH chances

These are assessment ranges, statistical guarantees nahi. Assumptions: internal judges prototype live dekhte hain; team fluent demo de sakti hai; current PS SIH26189 hi hai; college nomination competition normal-to-strong hai; code originality/rules satisfied hain; aur major live failure presentation ke time nahi hota.

| Stage | Current estimate | Reason |
|---|---|---|
| Internal/initial college screening | **Moderate-to-Strong: ~50–70%** | UI and real backend most college entries se stronger ho sakte hain; PS gap and public mismatch still material hain. College-specific competition se range sharply change hogi. |
| Advanced/national screening | **Low: ~2–6%** | Historical funnel extremely selective hai; exact ranking model, metrics, scale/security and deployment proof missing hain. |
| Strongest finalist group | **Very Low: ~1–3%** | Strong finalists usually PS-complete, validated and sharply differentiated hote hain. |
| Actually winning SIH | **Very Low: under ~1% current** | Current version ko missing direct requirement, weak validation and production credibility expose karte hain. |

Official SIH 2025 page lists 72,165 submissions and 1,360 Grand Finale teams; raw funnel roughly 1.9% tha, although ye current PS-specific probability nahi hai. Historic guidelines say 4–5 teams per PS may reach the finale and final decision belongs to the PS organization. Above ranges current product-quality judgement hain, mathematical forecast nahi.

---

## PART 5 — SIH winner se kya separate karta hai?

### Current real strengths

- Graph path actual compute hota hai; static SVG theater nahi.
- Provenance unusually strong hai: row/span/excerpt/evidence IDs visible hain.
- Product inference aur accusation ko separate karta hai; human review built in hai.
- Lead explanation calculation and uncertainty present hain.
- Entity resolution auto-merge nahi karta; reviewer decision preserve karta hai.
- UI cohesive and judge-friendly hai.
- Backend scoped tests broad hain: 101 pass.

### Current weaknesses

- Direct official PS requirement, key influential individual identification, absent hai.
- Public graph/lead exists while Data Sources says zero processed records.
- Deployed NER unavailable; fallback demo whitelist-based hai.
- Fresh intake new resolution proposals refresh nahi karta.
- Unstructured relation extraction exact grammar par dependent hai.
- No precision, recall, false-positive, task-time, scale or performance evaluation.
- Current frontend judge-flow automated regression is red.
- Architecture/security synthetic demo se aage credible nahi.

### Fatal weaknesses

Ye internal screening ko zaroor reject nahi karenge, but national winning ko derail kar sakte hain:

1. **“Key influencer kahan hai?”** — current answer: implemented nahi.
2. **“Data Sources zero hai to graph kis se bana?”** — public demo trust break.
3. **“AI production mein kahan chal rahi hai?”** — live NER unavailable; anomaly model unvalidated.
4. **“New data par same system work karta hai?”** — dynamic resolution pipeline incomplete.
5. **“Accuracy proof?”** — real-world metrics absent.
6. **“Sensitive police data secure kaise?”** — no auth/RBAC/durable controlled storage/tamper evidence.

### Winner-level missing pieces

- Full official PS coverage with explainable influencer ranking.
- One unseen-case, start-to-finish demonstration.
- Transparent evaluation on held-out synthetic/permissioned data.
- Public deployment where intake, graph, leads, reviews and audit share one coherent durable state.
- Credible security and scale architecture with at least one implemented boundary.
- Clear differentiation from mature link-analysis tools.
- Measured user or expert feedback.

### P0 — absolutely required

- Fix public demo coherence and frontend E2E judge flow.
- Dynamically recompute resolution and analytical outputs after intake.
- Implement official PS’s key-influencer capability with explainability.
- Create a held-out validation pack and publish honest metrics.
- Align AI claims with deployment reality; package NER or explicitly demo structured-only mode.

### P1 — strong competitive advantage

- Durable case state and minimum auth/RBAC/case isolation.
- Benchmark graph size, ingestion latency and query latency at increasing scales.
- Investigator-style usability evaluation and time-saving evidence.
- Competitor matrix against general graph DBs and mature investigation tools.
- Exportable evidence/audit bundle with integrity checks.

### P2 — nice to have

- Additional visual polish and animations.
- More theme customization.
- Generic chatbot/LLM assistant without retrieval/evidence guarantees.
- Extra dashboards without a PS requirement or measured user need.

---

## PART 6 — General hackathon evaluation

General hackathons mein product SIH se thoda better perform kar sakta hai because judges often 3–5 minute demo, polish, story and visible technical integration ko heavily reward karte hain. Yahan Network Intel ka graph reveal, evidence drawer and human-review story effective hai.

Weakness same rahegi: mature competitors ke against originality moderate hai; AI hackathons mein deployed NER and evaluation weak hai; engineering hackathons mein transient state and failing E2E tests hurt karenge.

---

## PART 7 — General hackathon scorecard

| Area | Score /10 | Strict reason |
|---|---:|---|
| Idea originality | **5** | Criminal-network graph analysis established category hai; provenance-first review framing differentiates somewhat. |
| Technical depth | **7** | Real backend, parser, graph traversal, lead rules, anomaly model and persistence. |
| Demo wow factor | **7** | Dense network + 6-hop reveal + exact evidence memorable ho sakta hai. |
| UI/product polish | **8** | Visually professional and cohesive. |
| Real-world usefulness | **7** | Clear investigation utility, but no field validation. |
| AI/ML strength | **4** | Isolation Forest real; NER partial/live unavailable; no accuracy proof. |
| Engineering execution | **6** | Build/lint/backend tests pass; production state and frontend E2E fail. |
| Story/pitch potential | **8** | “Fragmented clues → evidence-backed lead → human decision” strong narrative hai. |
| Differentiation | **5** | Stronger than an LLM wrapper; weaker than mature graph-intelligence products. |
| Overall completeness | **6** | Seeded demo cohesive; arbitrary-case lifecycle incomplete. |
| **Overall general hackathon score** | **63/100** | **Competitive college prototype, not yet national winner.** |

---

## PART 8 — Chances by hackathon type

| Hackathon type | Current rating | Stage breakdown / reason |
|---|---|---|
| College/local | **Competitive-to-Strong** | Shortlist: Strong; top 3: Competitive; win: Moderate. Polish and real backend help, public mismatch and missing validation limit. |
| Strong national | **Average** | Shortlist: Average; finals: Weak; podium: Weak; win: Weak. Winner-level teams will bring validation, PS completeness and stronger architecture. |
| AI-focused | **Average-to-Weak** | Model novelty, deployment availability and metrics are insufficient for AI-first judging. |
| Cybersecurity/intelligence | **Competitive** | Domain fit, provenance and review safety are strengths; security controls and production data realism remain gaps. |
| Generic product/innovation | **Average-to-Competitive** | Story and UI strong, but clear customer validation and business/adoption proof absent. |
| High-level developer/engineering | **Average** | Genuine code depth exists; test, scaling and deployment gaps will be scrutinized. |
| 24–48 hour hackathon | **Strong demo entry** | Scope and polish look impressive for time-boxed judging, assuming organizers permit prebuilt foundations and disclosure is clear. |

Same product different score karta hai because AI judges model quality dekhte hain, cyber judges trust/security, product judges user evidence, aur short college hackathons visible completion and presentation ko zyada weight karte hain.

---

## PART 9 — Best competitive fit ranking

1. **Cybersecurity / intelligence hackathons — 7.4/10**  
   Core workflow, provenance, graph investigation and human review fit strong hai.

2. **Government / public-safety hackathons — 7.1/10**  
   Problem relevance high; governance, scale and direct PS gaps score reduce karte hain.

3. **College software hackathons — 7.0/10**  
   Product polish plus real backend common field se stronger ho sakta hai.

4. **Open innovation / product hackathons — 6.3/10**  
   Strong story; user validation and differentiation weak.

5. **Graph/data visualization hackathons — 6.2/10**  
   Strong visual graph; algorithms still basic.

6. **Generic developer/engineering hackathons — 5.8/10**  
   Good breadth; reliability and scale proof incomplete.

7. **AI/ML model-focused hackathons — 5.0/10**  
   AI contribution real but neither novel nor benchmarked.

---

## PART 10 — Strong teams ke against comparison

### Network Intel likely beats

- **Excellent UI, shallow backend:** if judges inspect code, Network Intel ke real APIs, graph traversal, evidence model and review state advantage denge.
- **LLM wrapper with great demo:** unless wrapper has strong domain evaluation, your provenance and deterministic explainability more credible hai.
- **Strong ML, weak product:** short live demo mein Network Intel investigator workflow aur usability se beat kar sakta hai, though technical judges model team prefer kar sakte hain.
- **Deep system, poor presentation:** initial pitch/demo scoring mein Network Intel advantage le sakta hai.

### Teams that can beat Network Intel

- **Mature graph-intelligence product:** centrality/community/link prediction, dynamic ingestion, scale benchmark and real evaluation ke saath clearly stronger.
- **Strong ML + usable product:** validated entity resolution/NER/anomaly precision with explainable UI would beat you decisively.
- **Innovative hardware/software system:** if problem fit strong and functioning hardware proof hai, novelty and execution score higher ho sakta hai.
- **Polished SaaS with real users:** user adoption, measured outcomes and stable production deployment judges ko stronger evidence dete hain.
- **Technically deep secure platform:** auth, audit integrity, multi-case scale and deployment proof SIH/public-safety context mein decisive hai.

Your current advantage **presentation + provenance + working breadth** hai. Current disadvantage **generalization + validation + PS completeness + production credibility** hai.

---

## PART 11 — Wow factor

| Moment | Score /10 | Why |
|---|---:|---|
| First 10-second visual impression | **8** | Dark investigation console, graph and inspector polished feel dete hain. |
| First 60 seconds | **7** | Story clear ho sakti hai, but too many screens se cognitive load badh sakta hai. |
| Technical depth after questioning | **6** | Real code exists; AI, scale and dynamic-data questions gaps expose karte hain. |
| Uniqueness after 10 teams | **5** | Graph visualization and AI claims common honge; provenance review flow differentiator hai. |
| Memorability after judges leave | **7** | Operation Trinetra and evidence-path reveal memorable ban sakta hai. |
| Judges khud product explore karna chahenge | **7** | Interactive network and evidence drawers invite exploration. |

### ONE memorable demo moment

**“Find Path” click karo → Rahul se Vikram tak unexpected 6-hop connection reveal karo → ek edge/lead open karke exact source row/excerpt dikhao → calculation aur uncertainty show karo → investigator human review record kare.**

One-line narration:

> “System accusation nahi karta; fragmented records se explainable lead banata hai, aur har inference se original evidence tak judge ko one click mein le jaata hai.”

Ye current product ka real wow moment hai. Isse pehle public Data Sources contradiction fix karna mandatory hai.

---

## PART 12 — Judge risk analysis

| High-risk question | Likelihood | Risk | Strong answer supported now? | Fix / kya learn karna hai |
|---|---|---:|---|---|
| Graph hardcoded hai? | Very High | High | **Mostly yes:** traversal real hai, dataset seeded hai. | Live edge removal/alternate path proof rehearse karo; seed openly disclose karo. |
| ML exactly kahan hai? | Very High | High | **Partial:** Isolation Forest real; public NER unavailable. | Model features, thresholds, failure modes explain karo; live NER fix or claim reduce. |
| Key influencers kaise identify karte ho? | Very High | Critical | **No.** | Explainable PageRank/betweenness/community role module implement and validate karo. |
| Neo4j alone kyun nahi? | High | Medium | **Yes.** | Explain that DB storage/query solves graph persistence; your value is ingestion, evidence model, analytics and review workflow. |
| Entity-resolution accuracy kya hai? | Very High | High | **No metric.** | Held-out labelled alias/non-match set; precision/recall and false-merge rate report karo. |
| False accusation kaise prevent hota hai? | Very High | High | **Good product answer.** | Leads ≠ guilt, no auto-merge, evidence visible, human review. Add RBAC and policy controls. |
| Data kahan se aata hai? | High | Medium | **Synthetic only.** | Exact synthetic generator/schema explain karo; no claim of agency integration. Future integration interface show karo. |
| New files upload karun to full analysis update hoga? | High | High | **Partial.** | Dynamic proposal/lead recomputation and unseen-case demo implement karo. |
| Scale kaise karoge? | High | High | **Architecture answer only.** | Measured benchmark + graph DB/durable store/job queue phased design. |
| Existing i2/link-analysis tools se better kyun? | High | High | **Weak current differentiation.** | Provenance-first, cautious AI and Indian source-format workflow ko measurable differentiator banao; competitor matrix prepare karo. |
| AI wrong hua to? | High | High | **Partial-to-good.** | Withheld unsupported claims and human review strong; model versioning, confidence calibration and rollback add karo. |
| Evidence kya support karta hai? | Very High | Low | **Strong.** | Exact row/span/excerpt demonstration rehearse karo. |
| Team ne actually kya build kiya? | High | High | **Code can support depth; authorship audit nahi hua.** | Each member module ownership, commit evidence and 30-second architecture explanation prepare kare. |
| Police data secure kaise hai? | Very High | Critical | **No.** | Clearly say synthetic POC; auth/RBAC, encryption, isolation, logging and retention roadmap plus one implemented minimum control. |
| Public Data Sources zero kyun? | High if explored | Critical | **No good answer.** | Public state seed/coherence fix before sharing link. |

---

## PART 13 — Current vs winner-level

| Area | Current | Winner-level | Gap |
|---|---|---|---|
| UI | Polished investigator console | Polished plus presentation-mode readability and reliable states | Medium |
| End-to-end workflow | Strong seeded local flow; public contradiction | Fresh unseen input to reviewed output, reproducibly | High |
| Graph intelligence | BFS paths and context | Path + influence + communities + temporal/role analytics | High |
| AI | Isolation Forest; partial NER | Deployed, justified, evaluated models with failure handling | High |
| Entity resolution | Conservative weighted rules for seeded proposals | Dynamic candidates, labelled evaluation, calibrated policies | High |
| Explainability | Strong | Strong plus model-level explanations and decision export | Low-to-Medium |
| Evidence | Exact source provenance | Integrity-protected evidence lifecycle and access control | Medium |
| Validation | 101 backend tests; frontend E2E red; no accuracy metrics | Green regression suite plus held-out quality metrics | High |
| Performance | Tiny dataset only; no benchmark | Stated scale targets and measured latency/throughput | High |
| Security | No auth/RBAC/case isolation | Identity, roles, isolation, encryption, retention and audit controls | Critical |
| Architecture | In-memory graph + SQLite; transient serverless state | Durable multi-case data layer, jobs, observability, graph scale path | High |
| Demo | Visually strong but state mismatch | Deterministic preflighted demo with recovery path | High |
| Pitch | Strong narrative potential | Exact PS mapping, metrics, differentiation and honest scope | Medium |
| Technical defence | Good on graph/evidence | Strong on AI metrics, security, scale and alternatives | High |

---

## PART 15 — Highest-ROI next 5 actions

### 1. Public demo ko one coherent end-to-end truth banao

- **What:** Public Data Sources seed/load karo, graph/leads same processed state se derive karao, judge-flow Playwright tests update karke 100% green karo, and a pre-demo health check add karo.
- **Why:** Current contradiction trust instantly break kar sakti hai.
- **Difficulty:** Medium.
- **Impact on SIH:** Very High.
- **Impact on other hackathons:** Very High.

### 2. Fresh uploads ko complete intelligence pipeline se connect karo

- **What:** Source process hone ke baad resolution proposals, graph, leads and anomaly outputs dynamically recompute karvao. Ek unseen case se live proof do.
- **Why:** Ye “seeded showcase” aur “working platform” ka difference hai.
- **Difficulty:** High.
- **Impact on SIH:** Very High.
- **Impact on other hackathons:** High.

### 3. Official missing requirement: explainable influencer identification

- **What:** Degree/PageRank/betweenness/community-role signals combine karke evidence-linked influential-person ranking banao; score ko guilt probability mat label karo.
- **Why:** SIH26189 explicitly key influential individuals maangta hai.
- **Difficulty:** Medium-to-High.
- **Impact on SIH:** Critical.
- **Impact on other hackathons:** High.

### 4. Held-out evaluation pack aur honest metrics publish karo

- **What:** Seed narrative se alag positive/negative/uncertain cases banao; entity-resolution precision/recall/false-merge rate, relation extraction coverage, path correctness, lead false positives and latency measure karo.
- **Why:** Judge ke “accuracy?” question ka current answer weak hai.
- **Difficulty:** Medium.
- **Impact on SIH:** Very High.
- **Impact on other hackathons:** Very High, especially AI/engineering.

### 5. Minimum credible sensitive-data architecture implement karo

- **What:** Login/RBAC, case isolation and durable managed database ka smallest working slice add karo; remaining encryption, retention, tamper evidence and audit controls ka concrete architecture show karo.
- **Why:** Public-safety product bina trust boundary ke winner-level nahi lagta.
- **Difficulty:** High.
- **Impact on SIH:** High.
- **Impact on other hackathons:** Medium-to-High.

---

## PART 14 — Final Verdict

### SIH

**Current SIH competitiveness: 6.2/10**  
**Current SIH winning potential: Weak**

### After P0 fixes:

**7.4/10**

### After P0 + P1 fixes:

**8.2/10**

### Other Hackathons

**General hackathon competitiveness: 6.3/10**  
**General hackathon winning potential: Moderate**

### Best hackathon category for Network Intel:

**Cybersecurity / intelligence investigation hackathons**

### Weakest hackathon category:

**AI/ML model-focused hackathons where benchmarked model novelty and accuracy dominate judging**
