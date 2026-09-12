# Judges Q&A: short spoken answers

Formula: direct answer, ek concrete proof, phir relevant boundary. Har answer roughly 20–30 seconds mein rehearse karo. “Pata nahi” ke baad verification plan do; invented number se answer fill mat karo.

## Problem, PS aur novelty

### 1. Aap exactly kya problem solve kar rahe ho?

“Investigation records alag reports, CDR aur transactions mein bikhre hote hain. Network Intel unko source-linked graph mein connect karta hai, taaki analyst relationship aur lead ka original evidence inspect kar sake. Current demo controlled synthetic case hai.”

Proof: Data Sources, Network, evidence drawer.

### 2. Iska user kaun hai?

“Primary intended user authorized investigator ya intelligence analyst hai. Current prototype mein hum unka evidence-review workflow simulate kar rahe hain. Actual agency users ke saath usability validation abhi pending hai.”

Proof: investigation case, analyst review flow. Actual police endorsement imply mat karo.

### 3. PS se kitna match karta hai?

“Working brief ke multi-source processing, extraction, graph aur pattern-analysis parts ka prototype hai. Dedicated influential-node ranking abhi verified feature nahi hai. Official PS wording ko SPOC se confirm karke requirement-wise coverage finalize karenge.”

Proof: roadmap coverage matrix. Official PS milne par answer update karo.

### 4. Innovation kya hai? Graph viewer toh pehle se hote hain.

“Haan, link-analysis existing category hai. Hamare prototype ka contribution source evidence, reviewed identity, computed path aur review history ko ek continuous workflow mein lana hai. Established products ke against superiority claim karne ke liye comparative evaluation abhi baaki hai.”

Proof: path edge se evidence kholna; reversible match.

### 5. Excel mein kyun nahi kar sakte?

“Excel se cross-reference possible hai. Graph multi-hop relationships explore karna aur har step ka evidence inspect karna more explicit banata hai. Manual baseline ke against time aur correctness measure karna hamare pilot evaluation ka part hoga.”

Proof: six-hop path. Unmeasured efficiency percentage mat bolo.

### 6. Aapka impact kya hoga?

“Expected benefit repeated cross-referencing kam karna aur review context improve karna hai. Hum impact ko same task par manual versus assisted completion time, correctness aur source coverage se measure karenge. Real-world savings abhi measure nahi hui.”

Proof: proposed evaluation plan, not fabricated results.

## Data aur extraction

### 7. Data kahan se aaya? Real police records hain?

“Demo data synthetic hai aur repository mein deterministic scenario ke liye authored hai. Ismein real police databases ya personal investigation records use nahi hue. Authorized real-data pilot separate future step hoga.”

Proof: Synthetic Demonstration Data label, demo fixtures.

### 8. New file upload karun toh chalega?

“Defined CSV/TXT formats par controlled ingestion supported hai. Schema aur identifiers validate hote hain. Arbitrary PDF, scanned report ya every possible CSV ka universal parser claim nahi hai. Supported fixture se fresh ingestion demonstrate kar sakte hain.”

Proof: Data Sources and existing prepared file. Unknown external upload ko guaranteed result mat bolo.

### 9. AI exactly kahan hai?

“Local model available ho toh spaCy NER report entities extract karta hai. Secondary behavioral triage mein Isolation Forest hai. Main Lead 17 temporal rules se generate hota hai aur NetworkX graph algorithm paths compute karta hai. In methods ko alag roles diye hain.”

Proof: ner_service.py, behavioral_profiler.py, lead_engine.py.

### 10. Kya aapne model train kiya?

“Humne crime-prediction model train nahi kiya. spaCy pretrained NER optional use hota hai. Isolation Forest case cohort ki statistical features par fit hota hai, labelled criminal identities par nahi. Demo scenario synthetic hai.”

Proof: model loading and profiler. “No model training anywhere” mat bolo because Isolation Forest fit hota hai.

### 11. Hindi ya scanned FIR process hoti hai?

“Current verified extraction controlled English text aur structured identifiers par hai. Hindi, multilingual documents aur OCR ki representative evaluation abhi pending hai. Production scope mein language-specific test sets aur human validation chahiye.”

Proof: ner_service.py default model and format boundary.

### 12. Negation ko kaise handle karte ho?

“Controlled report case mein ‘did not meet’ negative claim ke roop mein preserve hota hai. Usse positive MET relationship nahi banana chahiye. Is boundary ka example/test hai, lekin arbitrary natural-language negation par universal accuracy claim nahi hai.”

Proof: report claims, existing NER/intake tests.

### 13. Same person ke multiple naam kaise identify hote hain?

“Name similarity candidate generate kar sakti hai, par exact phone aur vehicle identifiers stronger evidence dete hain. Investigator feature-level source evidence inspect karke decision leta hai. Original mentions preserve rehte hain aur confirmed projection undo ho sakti hai.”

Proof: R.K. Sharma comparison.

### 14. Agar galat merge ho gaya toh?

“Original source mentions delete nahi hote. Reviewer reason ke saath undo karke separate mentions restore kar sakta hai. Hum false-merge rate ko labelled ambiguity cases par evaluate karna chahte hain; heuristic score calibrated probability nahi hai.”

Proof: Resolution undo, only if time permits.

### 15. Source galat ya incomplete hua toh?

“System source claim ki factual truth guarantee nahi karta. Verification state visible rakhta hai aur lead engine incomplete evidence trace wale events omit karta hai. Missing data baseline aur connections ko affect kar sakta hai, isliye source coverage disclose karte hain.”

Proof: evidence drawer verification state; lead engine diagnostics.

## Graph aur lead calculations

### 16. Lead 17 hardcoded hai?

“Scenario aur default endpoints synthetic fixtures mein fixed hain. Lead ka eligibility, signals aur evidence backend rules se recompute hote hain. Hum arbitrary cases par generalization claim nahi karte. Qualifying input hataane par result change ya empty hona chahiye.”

Proof: lead_engine.py, tests and re-run engine. “Re-run” alone non-hardcoding proof nahi, input-change test stronger hai.

### 17. Path kaise find hota hai?

“Frontend source, target aur maximum depth bhejta hai. Backend NetworkX current graph projection par bounded shortest-path traversal karta hai. Response mein ordered nodes, relationships aur evidence references aate hain. Screen coordinates computation ko affect nahi karte.”

Proof: Find Path and path inspector.

### 18. Six-hop path ka matlab kya?

“Seeded scenario mein selected entities ke beech six recorded association steps hain. Traversal undirected association search hai, edge ka source direction separately shown hai. Isko chronological movement ya coordination ka proof nahi bol sakte.”

Proof: path direction disclaimer.

### 19. 11 calls suspicious kyun hain?

“Selected synthetic history ka median two outgoing calls per day hai. Policy max of five calls aur three times median use karti hai, yani threshold six. Eleven current records us threshold ko cross karte hain. Yeh activity signal hai, criminal intent ka evidence nahi.”

Proof: communication calculation. Celebration, incident response jaise benign explanations possible hain.

### 20. INR 1,95,000 kya laundering amount hai?

“Nahi, yeh three connected transfers ka total recorded volume hai, seventy-five minutes mein. Same funds multiple transfers mein count ho sakte hain. Purpose ya illegality establish karne ke liye independent investigation chahiye.”

Proof: transaction signal limitation.

### 21. HIGH priority ka matlab high crime probability?

“HIGH current queue policy mein three signal categories overlap karne par review priority hai. Yeh calibrated crime probability nahi hai. Communication ke related signals ko separate independent vote ki tarah count nahi karte.”

Proof: signal_categories and priority_for in lead engine.

### 22. Isolation Forest score ka meaning kya hai?

“Score case cohort ke comparison mein statistical unusualness measure karta hai. Temporal concentration, counterparties, amount deviation aur graph features input ho sakte hain. Cohort small ya uniform ho toh result limited ho sakta hai. Isse guilt, intent ya leadership infer nahi karte.”

Proof: Behavioral Profiles disclaimer; INSUFFICIENT_SAMPLE_SIZE and ZERO_VARIANCE states.

### 23. Key influencer identify karte ho?

“Dedicated influential-node ranking current active implementation mein verify nahi hui. Paths aur local clustering available hain. Official requirement ke according degree/betweenness ranking ko explainable, source-coverage-aware evaluation ke saath add karna next iteration hai.”

Proof: backup slide 10. High degree = gang leader mat bolo.

### 24. NetworkX kyun, Neo4j/GNN kyun nahi?

“Bounded synthetic case ke liye NetworkX simple aur inspectable graph computation deta hai. Neo4j tab evaluate karenge jab persistence, concurrent queries aur workload justify kare. GNN ke liye suitable training/evaluation data chahiye; current problem slice explicit rules se demonstrable hai.”

Proof: actual stack. Technology addition ko innovation proxy mat banao.

## Engineering, security aur deployment

### 25. Aapka application live hai?

“Haan, public synthetic prototype Vercel par available hai aur no-sign-in workspace open hota hai. Production security aur durable hosted state complete nahi hain. Live demo access aur agency deployment readiness ko alag treat karte hain.”

Proof: public link and current deployment.

### 26. Data persist hota hai?

“Local launcher SQLite files mein decisions preserve karta hai. Current Vercel entrypoint temporary `/tmp` SQLite use karta hai, jo instances/restarts ke across durable guarantee nahi deta. Isliye judged review demo local primary hai; hosted durable storage hardening pending hai.”

Proof: api/index.py, local review history. Yeh important candid answer hai.

### 27. Sign-in nahi hai, privacy kaise maintain hogi?

“No-sign-in route synthetic demonstration ke liye intentional hai. Real records ke liye authenticated users, case-level permissions, retention, secure storage aur governance required honge. Current public prototype ko real confidential data ke liye position nahi karte.”

Proof: synthetic label and roadmap. Legal compliance certification invent mat karo.

### 28. Audit tamper-proof hai?

“Normal application behavior audit events append karta hai. Local administrator ya storage access ke against cryptographic tamper resistance implement nahi hai. Production design mein authenticated identity aur protected immutable audit storage evaluate karna hoga.”

Proof: Audit Trail; documented boundary.

### 29. Duplicate clicks se duplicate decisions?

“Review submission idempotency key use karti hai taaki same accidental retry duplicate decision na create kare. Behavior tests se check hota hai. Idempotency durable multi-instance storage ka substitute nahi hai.”

Proof: LeadReview flow and review store tests.

### 30. Internet fail ho toh?

“Installed dependencies ke saath core demo local backend aur frontend se run ho sakta hai, external AI API required nahi. Public deployment network dependent hai. Labelled previous recording/screenshots last fallback hain.”

Proof: prepared local demo, not just promise.

### 31. Kitna scale handle kar sakta hai?

“Current verified scope bounded synthetic case hai. Million-node throughput ya national scale benchmark nahi hua. Pehle graph size, ingestion latency aur memory profile karenge, phir durable indexed graph storage aur asynchronous jobs decide karenge.”

Proof: max depth and in-memory architecture. Unsupported TPS/latency mat invent karo.

## Evaluation aur team defense

### 32. Accuracy kitni hai?

“Real-world detection accuracy abhi measure nahi hui. Current scoped product suite mein 101 tests pass hain, jo implementation behavior check karte hain. Entity precision/recall, false merges aur source coverage held-out records par measure karne ka plan hai.”

Proof: current scoped test result dated 6 Sep 2026. Test pass rate ko model accuracy mat bolo.

### 33. Judges aapko select kyun karein?

“Hum working source-to-review slice demonstrate kar sakte hain, exact calculations explain kar sakte hain aur limits clearly state karte hain. Next iteration ka measurable plan bhi hai. Hamara focus evidence traceability aur dependable investigator workflow par hai.”

Proof: demo; answer ko selection guarantee ya boast mein mat badlo.

### 34. Agle hackathon phase mein kya karoge aur cost kya hogi?

“Pehle representative evaluation, false-merge controls aur ingestion reliability improve karenge. Phir durable storage aur reviewer access harden karenge. Cost compute, storage, backup aur expected workload ke estimate se nikalegi; abhi unsupported rupee figure quote nahi karte.”

Proof: staged roadmap with measurable outcomes. Organizer ka actual finale duration unknown hai, fixed hours mat assume karo.

### 35. Team ne khud kya banaya? AI tools use kiye?

“Development mein coding assistance use hui hai. Hum apne contribution aur tools ko transparently disclose karenge aur college rules follow karenge. Team ko parser, path computation, lead thresholds aur review storage explain aur modify karna aana chahiye. Individual ownership actual contribution ke basis par batayenge.”

Proof: each member apne implemented module ko input, output, test aur limitation ke saath explain kare. Jo code samajh nahi aata uski authorship/expertise overstate mat karo.

## Random-fire rehearsal

Ek teammate questions shuffled order mein pooche. 30 seconds ke baad answer stop karo. Score: direct answer mila? one proof diya? limitation relevant thi? Unknown point par guessing toh nahi hui?

Most important questions pehle rehearse karo: 3, 4, 9, 16, 21, 23, 26, 32, 35. Yeh PS alignment, novelty, AI honesty, deterministic demo, scoring, feature gap, hosting, evaluation aur team ownership test karte hain.

## Agar judge kahe “demo designed lag raha hai”

“Haan, scenario intentionally synthetic aur repeatable hai. Isse workflow inspect karna easy hota hai. Generalization prove karne ke liye unseen variants, benign controls aur false-merge tests chahiye. Hum deterministic demo ko real-world validation ke equal nahi bol rahe.”

Phir existing independent test ka outcome dikhana. Stage par unprepared external dataset import karke uncertain result promise mat karo.

## Agar judge kahe “AI add karo, tab innovative lagega”

“AI ka role clear evidence se justify karna chahte hain. Text extraction aur statistical triage suitable applications hain. Exact transaction arithmetic aur source provenance deterministic rehna useful hai. Additional model tab add karenge jab uska measured benefit aur error behavior evaluate ho.”

## Source pointers

Answers current repository inspection, SIH-JUDGE-QA.md, DEMO-RUNBOOK.md aur fresh scoped test run par based hain. Current name/deployment/test facts purane VEIL materials se update kiye gaye hain. PS coverage provisional hai jab tak official statement confirm nahi hota. Team achievements, agency approval aur live model availability assume nahi ki gayi.
