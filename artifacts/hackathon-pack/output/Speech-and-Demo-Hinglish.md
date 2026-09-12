# Speech aur demo rehearsal

Timing below practice targets hain. College ka actual time limit final authority hoga. Bina timed rehearsal ke duration ko measured result mat bolo.

## 30-second opening

“Namaste judges. Ek report mein R.K. Sharma hai, call record mein ek phone number, aur transaction file mein ek account. Investigator ko samajhna hai ki yeh records kaise connected hain. Network Intel source-linked graph banata hai, jahan har surfaced lead ka evidence kholkar review kiya ja sakta hai. Aaj hum synthetic Operation Trinetra par yeh complete workflow dikhayenge.”

Pause. Judge ko screen dekhne do. Intro mein saari technologies ya team history list mat karo.

## Recommended round: 4-minute pitch + 2:30 demo + 30-second buffer

Yeh 7-minute round ki working assumption hai. Q&A ko organizer ke allocated time mein alag rakho. Slide 6 par demo par switch karo, phir slides 7–8 par wapas aao. Backup slides 9–12 ko normal pitch mein mat read karo.

### Slide 1: product introduction, target 25 seconds

“Network Intel ka focus fragmented evidence ko ek reviewable investigation workspace mein lana hai. Hamara prototype reports, call records, account transfers aur vehicles ko connect karta hai. Aaj ka poora data synthetic hai. Investigator har connection ka source dekh sakta hai aur apna decision record kar sakta hai.”

### Slide 2: problem and user, target 30 seconds

“Hamare target user authorized investigator aur analyst hain. Unke workflow mein ek identity alag files mein different naam ya identifiers se aa sakti hai. Sirf similar naam ko merge karna risky hai. Sirf graph line dikhana bhi enough context nahi deta. Hum identity aur relationships ko source evidence ke saath inspect karne ka workflow dete hain.”

Official PS confirm ho jaaye toh ek line add karo: “Yeh [verified PS title] ke [exact relevant requirement] ko address karta hai.” Abhi bracket line ko stage par mat read karo.

### Slide 3: solution and contribution, target 35 seconds

“Yeh hamare prototype ka previous captured run hai, jab naam VEIL tha. Ab product Network Intel hai. Input se extracted entities aati hain. Uncertain identity ko analyst confirm ya reject karta hai. Backend path compute karta hai aur har step ka evidence deta hai. Hamara contribution is continuity ko ek working flow mein demonstrate karna hai, including reversible decisions.”

### Slide 4: explainable signal, target 40 seconds

“Is synthetic example mein pichhle saat complete din ka median do outgoing calls per day hai. Event day par replay time tak gyarah calls record hui. Configured trigger max of five aur three times baseline hai, yani six. Isliye communication signal aata hai. Teen connected transfers pachhattar minutes mein total ek lakh panchanve hazaar ka volume dikhate hain. Yeh volume hai, unique funds ka claim nahi. Analyst supporting records verify karega.”

### Slide 5: architecture, target 35 seconds

“React aur Cytoscape frontend exploration handle karte hain. FastAPI typed APIs serve karta hai. Controlled parsers identifiers extract karte hain, aur local model available ho toh spaCy NER text extraction support karta hai. NetworkX paths compute karta hai. Temporal rules main lead engine hain; Isolation Forest secondary triage ke liye hai. Local SQLite decisions record karta hai.”

### Slide 6: demo transition, target 10 seconds

“Ab hum ek complete evidence chain dikhayenge: source, identity review, path, lead, exact record aur investigator decision.”

**Demo start. Detailed actions neeche hain.**

### Slide 7: proof and limitations, target 35 seconds

“Current product test suite mein 101 tests pass hue. Yeh implementation checks hain, real-world accuracy nahi. Public prototype available hai. Local review data SQLite mein persist hota hai, lekin hosted temporary storage ko durable storage se replace karna pending hai. Authenticated reviewers, real workload evaluation aur dedicated influential-node ranking bhi next-stage work hain.”

### Slide 8: close, target 30 seconds

“Selection ke baad hum representative test cases, false-merge evaluation aur supervised usability feedback par kaam karenge. Durable storage aur access controls pilot ki foundation honge. Aaj hum ek working source-to-review flow aur clear technical boundaries demonstrate kar rahe hain. Internal selection aur domain mentorship se hum is prototype ko measured pilot tak le jaana chahte hain. Thank you.”

Total speaking target: 240 seconds. Natural pauses aur screen-switch time rehearsal mein measure karo; word-by-word speedrun mat karo.

## 2:30 demo: exact intent, clicks aur narration

Precondition: local app running, baseline case known, four source files prepared, desired identity match not already confirmed. Public app mein state shared/temporary ho sakti hai; primary demo local rakho.

| Time target | Action | Bolo | Proof |
|---|---|---|---|
| 0:00–0:20 | Open `http://127.0.0.1:8000/#/app`, Case Overview then Data Sources | “Yeh synthetic case hai. Report, CDR, transactions aur vehicle sources yahan hain.” | Multiple controlled sources |
| 0:20–0:50 | Entity Resolution; R.K. Sharma candidate; exact phone and vehicle references inspect; reviewer/reason fill; Confirm Match | “Similar naam akela enough nahi. Exact identifiers aur evidence dekhkar investigator confirm karta hai.” | Explainable human decision |
| 0:50–1:15 | Network; start Rahul Kumar Sharma, end Vikram Singh; depth 8; Find Path | “Yeh backend-computed association path hai. Har relationship ka source inspect ho sakta hai.” | Computed six-hop seeded path |
| 1:15–1:35 | Lead Inbox; Open Lead 17; communication/transfer sections | “System overlapping signals ko review ke liye surface karta hai. Priority probability nahi hai.” | Transparent rules |
| 1:35–2:00 | Transfer evidence E-TX-01 open | “Exact filename, row aur raw excerpt yahan hai. Source verification state bhi visible hai.” | Provenance |
| 2:00–2:20 | Back to investigation; Record investigator review; Needs more evidence; reason; review and confirm submission | “Evidence insufficient ho toh investigator yeh decision record kar sakta hai.” | Human authority |
| 2:20–2:30 | Audit Trail; filter LEAD REVIEW SUBMITTED if needed | “Actor, reason aur state change recorded hai.” | Review history |

Button wording product revisions ke saath slightly change ho sakti hai. Current UI ke exact labels rehearsal mein verify karo. Record source truth se explain karo, memorized stale label se nahi.

Suggested reviewer: `Demo Reviewer`. Suggested resolution reason: `Exact phone aur vehicle source references reviewed for this synthetic demonstration.` Suggested lead review reason: `Source claims ko further verification chahiye.` Yeh demo statements hain, real assessment nahi.

## Demo ko sharp kaise rakho

- Cursor ko target par le jao, ek click karo, result aane do, tab explain karo.
- Loading ke dauraan rapid repeat clicks mat karo.
- Har screen ka single purpose ho. Full feature tour avoid karo.
- Landing page show karni ho toh maximum 5–10 seconds, phir Get started.
- Behavioral Profiles aur report extraction Q&A follow-up mein dikhao; core flow mein unnecessary tabs mat add karo.
- Six-hop result seeded state par expected hai. Imported state ya confirmed aliases change hue hon toh current count honestly read karo.
- Demo ke beech reset, dependency install ya random upload experiment mat karo.
- Judge question kare toh 15–25 second answer do, phir bolo: “Isi evidence ko next screen par verify kar sakte hain.”

## Agar round sirf 5 minutes ka ho

Target: 2:30 speech + 2:00 demo + 30-second buffer. Slides 1, 2, 3, 5, 7, 8 use karo; signal calculation demo mein explain karo. Full identity confirmation skip karke already-reviewed comparison dikhana allowed hai, lekin clearly bolo “yeh pehle reviewed state hai”. Live submission ka false impression mat do.

Demo: Sources 15s, reviewed identity 20s, path 25s, Lead 17 and E-TX-01 40s, review/audit 20s. Actual 2-minute target rehearse karo. Time kam ho toh investigator review screen dikhakar explain karo; new persisted action claim tabhi karo jab actually save hua ho.

## Agar round 3 minutes ka ho

30s problem + 30s solution + 90s proof demo + 30s current boundary and next milestone. Sirf path, Lead 17 aur exact evidence dikhana priority hai. Architecture ki ek line enough hai. Backup questions ke liye slides retain karo.

## Failure recovery: 10 seconds se zyada fight mat karo

**Internet fail:** “Public link unreachable hai. Same prototype ka local build ready hai; main us par continue karta hoon.” Local direct workspace open karo.

**Hosted saved decision disappear:** “Current public demo temporary storage use karta hai. Local review history available hai; durable hosted storage pending hai.” Persistence issue ko hide mat karo.

**Local service fail:** One known restart only if quick. Otherwise: “Live run abhi interrupt hua. Yeh pehle captured synthetic run hai; main evidence chain isse explain karta hoon.” Labelled screenshots or actual saved recording use karo.

**Identity already confirmed:** “Yeh reviewed state hai. Original mentions preserve hain aur undo supported hai.” Timer tight ho toh undo/reconfirm sequence force mat karo.

**Lead empty:** Wrong case/state or rules not satisfied ho sakte hain. “Current input policy satisfy nahi karta; engine empty result de raha hai.” Labelled seeded fallback use karo, hardcoded live result mat invent karo.

**NER model unavailable:** “Optional spaCy model is environment mein available nahi. Controlled fallback parser active hai.” Core structured demo continue karo.

**Unknown technical question:** “Is point ko abhi benchmark nahi kiya. Hum [specific check] run karke verify karenge. Current prototype ka verified behavior yeh hai…”

## Local preparation commands

Commands project root `Z:\XLab\New\Network Intel` se. Dependency installation event se pehle complete karo. Existing server ko duplicate mat start karo.

```powershell
# Product test suite only
.\.venv\Scripts\python.exe -m pytest tests -q

# Existing decisions preserve karke local server start
.\.venv\Scripts\python.exe -m backend.serve_demo --port 8000
```

Fresh rehearsal chahiye toh server stop karne ke baad dedicated demo reset use karo. Yeh state-changing operation hai aur stage par nahi karna:

```powershell
.\.venv\Scripts\python.exe -m backend.serve_demo --reset --port 8000
```

README/DEMO-RUNBOOK mein reset archives ka behavior documented hai. Apne meaningful review data ko reset karne se pehle preserve karo.

## Speech practice

First run: script padhkar meaning samjho. Second run: sirf keywords se bolo. Third run: driver aur speaker different hon. Fourth run: random interruptions add karo. Fifth run: internet disabled local rehearsal.

Record: date, pitch duration, demo duration, failed click, unclear explanation, judge question, next correction. Old 107.054 seconds figure sirf prior click rehearsal tha, narration include nahi thi.

Best final sentence: “Aapne abhi ek source-backed connection aur uska human review dekha. Agla step isi flow ko representative cases aur investigator feedback se validate karna hai.”
