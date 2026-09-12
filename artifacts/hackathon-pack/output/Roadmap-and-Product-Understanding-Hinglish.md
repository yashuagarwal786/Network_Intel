# Network Intel: product understanding aur selection roadmap

## 1. PS ko kaise samajhna hai

Repo ka previous brief SIH26189 mention karta hai. Public mirrors isko “AI-Powered Criminal Network Analysis System” ke naam se list karte hain. Official portal wording abhi unverified hai. Isliye neeche ka alignment **working interpretation** hai, official certification nahi.

Public PS mirror ka short interpretation: multiple investigation data sources se entities extract karna, unke relationships map karna, relevant individuals aur unusual activity examine karna, aur investigators ko visual analytical context dena. Source: [public PS mirror](https://sihone.pages.dev/ps/26189). Mirror ki suggested stack ya speculative architecture ko official requirement mat samajhna.

PS ki language judges ke liye plain example mein bolo: “Ek naam report mein hai, phone CDR mein hai, account transaction file mein hai. Analyst ko source verify karte hue inka relationship samajhna hai.”

Official text milne par uski har requirement ke saamne demo screen, backend proof aur limitation likho. Jo feature partial hai usko partial hi mark karo.

## 2. Tumhara solution actually kya hai

Network Intel ek investigator workspace hai. Ismein controlled source ingestion, entity candidates, reversible identity review, graph exploration, temporal leads, evidence inspection aur review history ek flow mein milte hain.

**Input:** synthetic report TXT, CDR CSV, transactions CSV, vehicle CSV aur baseline JSON fixtures.

**Processing:** structured parsers aur identifiers, optional local spaCy NER, evidence references, heuristic identity matching, NetworkX path computation, temporal rules aur optional statistical triage.

**Output:** source-linked association path, review-priority lead, exact evidence locator aur investigator decision.

**Human control:** uncertain matches reviewable hain. Confirmed identity projection undo ho sakti hai. Lead ko Needs more evidence mark karke reason record kar sakte ho.

**Current delivery:** React/TypeScript/Cytoscape UI, FastAPI API, NetworkX, local SQLite; public Vercel demo bhi available hai. Koi agency integration ya real investigative deployment verify nahi hua.

## 3. Working PS coverage matrix

| Requirement area | Current proof | Status / honest boundary |
|---|---|---|
| Multiple source ingestion | Data Sources, controlled CSV/TXT validation | Implemented for defined formats; arbitrary databases aur live feeds nahi |
| Entity extraction | Parser, exact identifiers, optional spaCy NER | Constrained English extraction; model availability dependent; universal Hindi OCR nahi |
| Relationship maps | Typed graph, evidence links, path inspector | Working recorded associations; discovered edge ko new fact mat bolo |
| Identity disambiguation | Feature comparison, confirm/undo | Human-reviewed heuristics; calibrated match probability nahi |
| Unusual pattern detection | Call burst, new contacts, connected transfers | Rule-based signals; current case/replay assumptions apply |
| Statistical triage | Isolation Forest in behavioral profiler | Secondary exploration; case cohort, no guilt prediction |
| Influential/key individuals | Dedicated ranking not found in active backend inspection | Coverage gap; clustering coefficient/path centrality ranking nahi |
| Investigator insights | Lead explanations, timeline, exact source record | Core vertical slice working |
| Scale/security/deployment | Public prototype + local runtime | Live access available; durable hosting, security, multi-case workload proof pending |

## 4. Selection ke liye strongest story

“Investigator ka question tha: yeh records kaise connected hain? Hum source ingest karte hain, uncertain identity review karte hain, path compute karte hain, us path ke temporal signals explain karte hain, aur source evidence kholkar investigator decision save karte hain.”

Is story mein har next screen previous question ka answer deti hai. Landing page ko sirf 5–10 seconds do. Core score-worthy product proof workspace mein hai.

**Contribution ko precisely bolo:** provenance, reviewed identity, path computation aur evidence-gated leads ka integrated workflow. “World's first”, “existing tools se superior”, “police ke liye ready”, “95% accurate” ya “crime prevent kar diya” mat bolo jab supporting study nahi hai.

**Likely judge challenge:** “Graph tools pehle se exist karte hain.” Answer: “Haan. Hamara contribution is prototype mein source-to-review continuity aur reversible decisions ko demonstrate karna hai. Novelty ko established products ke against user evaluation se validate karna abhi baaki hai.”

## 5. Verified facts aur claims ka discipline

| Safe claim | Proof | Kya claim nahi karna |
|---|---|---|
| 101 product backend tests pass hue | 6 Sep 2026 scoped test run | 101 tests = real-world accuracy |
| Lead backend calculate karta hai | lead_engine.py, thresholds and evidence gate | System ne criminal detect kar diya |
| Synthetic baseline 2 calls/day, event day 11 | Replay fixtures and calculations | All real telecom data ka normal baseline 2 hota hai |
| 3 transfers, 75 minutes, INR 1,95,000 volume | Transfer sequence calculation | INR 1,95,000 unique laundered money |
| 6-hop demo path, search depth cap 8 | NetworkX response on seeded case | Chronological conspiracy chain |
| Local SQLite review persistence | review_store.py and local launcher | Hosted /tmp is durable production storage |
| Optional spaCy and secondary Isolation Forest | ner_service.py and behavioral_profiler.py | Universal NLP, trained crime-prediction model |
| Public demo available | Vercel deployment | Agency production rollout complete |

## 6. Priority order before internal selection

**P0: official PS aur round rules.** SPOC se exact PS, deadline, pitch/demo/Q&A allocation, required PPT/PDF aur team metadata confirm karo. Mandatory 6-slide format mila toh 12-slide deck submit mat karna. Is deck ko rehearsal source rakho aur official structure mein compress karo.

**P0: repeatable demo.** Clean local state par exact core flow rehearse karo. Network down hone par bhi local build aur backend run hona chahiye. Hosted cold start ko avoid karne ke liye page pehle open karo, lekin loaded page ko fresh computation ka claim mat banao.

**P0: state persistence.** Current hosted /tmp limitation ko samjho. Internal round se pehle architecture migrate karna mandatory nahi; local primary demo sufficient ho sakta hai. Judges ke saamne hosted durable storage promise mat karo. Real rollout ke liye durable database compulsory roadmap item hai.

**P1: PS gap check.** Agar official PS explicitly influence ranking expect karta hai, uski gap disclosure ready rakho. 48 hours se kam time mein rushed GNN mat add karo. Enough time aur requirement ho toh explainable degree/betweenness ranking ka small evaluated follow-up plan banao. Is pack ne code mein feature add nahi kiya.

**P1: one counterexample.** Similar names with different exact IDs ya missing-evidence event ka outcome ready rakho. Positive demo ke saath system ki restraint dikhana credible proof hai.

**P1: current visuals.** Deck mein previous screenshots labelled hain. New branded screenshots tab replace karo jab same flow fresh successfully rehearse ho. Image edit karke old screenshot ko new live result mat dikhana.

**P2: formatting and rehearsal.** Fonts, projector readability, pointers aur speaker transitions polish karo. Is stage par sirf visual effect ke liye new dependencies mat introduce karo.

## 7. Seven-day plan, event date se relative

Yeh recommended schedule hai, official SIH timeline nahi.

| Din | Work | Deliverable | Done ka matlab |
|---|---|---|---|
| D-7 | Official PS + rubric + format lock | One-page requirement mapping | Har requirement ke saamne proof/gap |
| D-6 | Product truth audit | Claims sheet and known limitations | Team bina guessing AI, graph, storage explain kare |
| D-5 | Local golden flow and failure recovery | Rehearsal log, source files ready | Same flow 3 consecutive runs complete |
| D-4 | Negative controls and current screenshots | Evidence pack | False merge/missing evidence example explain ho |
| D-3 | Deck and speech freeze | Final PPTX + timed script | Core pitch allotted time se 15 sec pehle khatam |
| D-2 | Mock judging with faculty/friends | Top 10 weak answers list | Har answer 20–30 sec mein proof ke saath |
| D-1 | Full dress rehearsal + backups | Laptop, offline deck/video, backup copies | Network-off fallback aur HDMI test complete |
| D-day | Preflight, concise pitch, demo | One coherent case story | Setup ke liye stage time waste nahi |

## 8. Agar sirf 48 hours bache hain

**First 4 hours:** official format confirm, claim corrections, direct workspace route verify.

**Next 6 hours:** local flow, data state, exact buttons, source evidence and audit demonstration practice. Blocking bug mile toh narrow fix only.

**Next 4 hours:** deck content freeze. 8 main slides ko allowed time ke hisaab se reduce karo. Members ko one-pager do.

**Next day:** 3 timed runs, 2 random Q&A rounds, laptop/projector check, backup copies. Last evening ke baad new analytical model ya backend migration avoid karo.

## 9. Practice scorecard

Official SIH College SPOC 2024 guidance mein novelty, clarity, feasibility, impact, UX aur future progression jaise dimensions listed hain. Yeh historical reference hai, current college rubric/weights ka substitute nahi. [Official historical guide](https://sih.gov.in/letters/Guidelines-College-SPOC.pdf).

Apna practice score 0–2 do: 0 = claim only, 1 = partial proof, 2 = clear proof + boundary. Koi official weighting assume mat karo.

| Area | Judge ko kya dikhna chahiye |
|---|---|
| Problem understanding | Specific user, fragmented-record pain, PS mapping |
| Technical understanding | NER, graph, rules aur ML ka correct separation |
| Contribution | Source-to-review workflow, explicit evidence trace |
| Working product | Core flow without manual rescue |
| Feasibility | Current stack rationale and honest deployment limits |
| Evaluation | Tests, negative controls, no fake accuracy |
| Communication | Short answer, readable slides, purposeful clicks |
| Team readiness | Presenter fail hone par second member continue kar sake |

Kisi bhi area mein 0 ho toh usko fix karna optional visual polish se zyada valuable hai.

## 10. Team roles

Team size unknown hai, isliye roles functions ke hisaab se assign karo: main narrator, demo driver, technical Q&A owner, PS/domain owner, timing/backup owner. Ek person multiple roles kar sakta hai. Team size ya gender rules historical document se assume mat karo, current SPOC instructions follow karo.

Technical question par presenter bole: “Is pipeline ko [actual member name] ne implement kiya hai, woh explain karenge.” Member ko mic dene ke baad interrupt mat karo. Har member input, algorithm, output aur limitation ek minute mein explain kar sake.

## 11. Product roadmap after selection

**Phase 1, evaluation foundation:** held-out synthetic variations, benign scenarios, missing data, alias ambiguity, precision/recall definitions, false-merge rate and evidence coverage.

**Phase 2, pilot reliability:** durable DB/storage, authenticated reviewers, case isolation, ingestion limits, retention, backup/restore and operational audit protection. Legal/compliance review authorized domain stakeholders ke saath hogi; current compliance certification claim nahi hai.

**Phase 3, PS coverage:** requirement-confirmed influence ranking, multilingual extraction evaluation, larger authorized workloads, scale profiling. Har feature se pehle metric aur fail condition define karo.

**Pilot impact test:** same source set aur task par manual cross-reference time vs tool-assisted time compare karo. Correctness also record karo, sample size disclose karo, order effects control karo. Result aane se pehle saved-hours claim mat publish karo.

**Cost plan:** fixed amount invent mat karo. Compute, durable DB, source storage, backup, monitoring aur extraction workload ka small workload-based estimate banao. Volunteer reviewers ko genuine investigator validation mat label karo.

## 12. Final preflight

- Official metadata aur final title consistent: Network Intel; old VEIL screenshots clearly labelled.
- Public link, local direct `/#/app`, charger, HDMI adapter aur hotspot available.
- Local server running; reset sirf rehearsal state par aur stopped server ke saath.
- Report/CDR/transaction/vehicle files processed; correct case state checked.
- No personal or real investigation data demo mein.
- PPTX local disk par, backup video/captured screenshots alag labelled.
- Notifications off, zoom/projector readable, cursor controlled.
- 3 clean runs; final timed result log karo. Old 107.054s run narration ke bina tha.
- Last line aur first line team ko yaad ho. Baaki script samajhkar bolo.

## Sources aur confidence

Primary product sources: backend/lead_engine.py, demo_paths.py, intake_parser.py, ner_service.py, behavioral_profiler.py, resolution.py, review_store.py, api/index.py, frontend/package.json, current workspace UI, scoped product tests.

Context sources: README-PREVIOUS.md, SIH-SCOPE-FREEZE.md, DEMO-RUNBOOK.md, previous presentation audit. In documents ke older “not deployed”, old test counts aur old product branding ko current facts se update kiya gaya hai.

Official PS confirmation, current college rubric aur exact event date abhi user/SPOC se pending hain. Isliye no official selection odds, deadlines, mandatory team composition ya precise rubric weights claim kiye gaye hain.
