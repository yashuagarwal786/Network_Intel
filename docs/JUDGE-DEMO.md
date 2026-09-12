# Network Intel — 7-Minute Judge Demonstration Script

> **Product Positioning:**  
> *"Network Intel helps investigators discover, understand, verify, and prioritise cross-source connections while keeping evidence, inference, and human decisions separate."*

---

## Demo Schedule & Timeline (Total: 7 Minutes)

### Minute 0:00 – 1:00: Problem & Grounding (The "Anti-Black-Box" Pitch)
- **Action:** Open Landing Page (`/`). Show clear mission statement and direct entry button: **"Open Golden Demo Case (Operation Riverglass)"**.
- **Speaker Script (Hinglish/English):**
  > "Respected judges, criminal investigations mein sabse bada risk hota hai black-box AI ka jo directly kisi suspect ko 'guilty' declare kar deta hai ya arbitrary percentage score de deta hai. Court mein ya senior IO ke saamne aisa 'AI prediction' inadmissible aur dangerous hota hai.  
  > **Network Intel** koi crime prediction ya autonomous guilt-scoring tool nahi hai. Yeh ek **Investigator-Support System** hai jismein 3 strict boundaries hain:
  > 1. **Direct Evidence:** Har node aur link ka exact source text span aur SHA-256 locator hota hai.
  > 2. **Algorithmic Inference:** Conservative, explainable graph algorithms with explicit confidence caveats.
  > 3. **Human Decisions:** AI kabhi auto-merge ya legal decision nahi leta; investigator verifies and decides."

---

### Minute 1:00 – 2:30: Multi-Source Intake & Exact Provenance
- **Action:** Click on **"Data Sources"** tab in the sidebar.
- **Showcase:**
  1. 4 controlled source formats: **Investigation Report (.txt)**, **CDR (.csv)**, **Bank Transactions (.csv)**, **Vehicle Observations (.csv)**.
  2. Point to the **Intake Stats**: 48 records, exact entity mentions, candidates, and withheld claims.
  3. Click **"Mentions"** tab: Highlight that every mention displays its exact character offset (e.g., `characters 78–90`), raw text excerpt, and honest extraction method badge (`spaCy Statistical NER`, `spaCy EntityRuler`, `Deterministic CSV Field`).
  4. Note the absence of fake probabilities (`characters null-null` eliminated, no artificial confidence scores).
  5. Show **Operation Crosswind** in Case Hub: 5-hop multi-modal corridor covering CDR, Transactions, Vehicles, and Report, with noise entities isolated.

---

### Minute 2:30 – 3:45: Explainable Entity Resolution (No Auto-Merge)
- **Action:** Click **"Entity Resolution"** tab.
- **Showcase:**
  1. Open proposal `MP-rahul-rk-sharma` (Rahul Sharma vs R.K. Sharma).
  2. Point to the **Rule Score**: `Rule score: 0.800 (Not a probability)`.
  3. Show the **Supporting Evidence (3)** vs **Uncorroborated / Absent Signals (1)** separation.
  4. Point out that **Vehicles are corroborating property, NOT personal identity assertions**. Two people seen near the same vehicle never triggers automatic merge.
  5. **Live Action:** Click **"Confirm Match"** with reviewer name and mandatory justification reason.
  6. **Live Action:** Show the graph update. Then click **"Undo"** to prove the action is 100% reversible with immutable audit logging.

---

### Minute 3:45 – 5:00: Graph Investigation & The "Verified Only" Gate
- **Action:** Click **"Network Investigation"** tab.
- **Showcase:**
  1. Show the Cytoscape graph. Point out the distinct visual edge styles:
     - **Dashed grey line:** `EXTRACTED_UNVERIFIED` (machine assertion).
     - **Solid green line:** `INVESTIGATOR_VERIFIED` (human confirmed).
     - **Thick teal line:** `INVESTIGATOR_CORROBORATED` (multiple independent sources).
     - **Dotted purple line:** `INFERRED_CANDIDATE` (algorithmic traversal).
  2. Toggle the **"Verified Only"** toolbar button:
     - Instantly filters out unverified machine noise, leaving only facts confirmed by investigators.
  3. Path Finding: Find path between `Rahul Sharma` and `Vikram Singh`. Show the **Signal Corridor** with step-by-step hops and evidence count.

---

### Minute 5:00 – 6:15: Lead Inbox & Grounded AI Explainer (Strict Guardrails)
- **Action:** Open **"Lead Inbox"**, click **Lead 17** (`Coordinated contact and financial transfer window`).
- **Showcase:**
  1. **Structured Facts First:** Point out the order:
     - `Why Flagged / Summary`
     - `Supporting Evidence & Signals`
     - `Who / What Was Involved?`
     - `What Remains Uncertain?`
     - `Next Investigator Action`
  2. Point to the **Grounded Evidence Explanation (Optional AI Assistance)**:
     - Shows `Deterministic Grounded Fallback (Rules)` if no Groq API key is present.
     - Strict guardrail: Cannot use accusatory language (`guilty`, `mastermind`, `culprit`).
     - Cannot introduce hallucinated numbers or unverified entities.
     - Every statement cites allowlisted `fact_ids`.

---

### Minute 6:15 – 7:00: Analysis Draft Export & Closing Q&A
- **Action:** Click **"Analysis Draft"** button in the top action bar.
- **Showcase:**
  1. Opens the **Investigation Analysis Draft** modal (completely replaced the legally flawed Court Dossier).
  2. Seven structured, neutral sections:
     - Executive Summary & Scope
     - Subject Entity Profiles
     - Verified Factual Associations
     - Algorithmic Corridors & Behavioral Signals
     - Epistemic Gaps & Limitations
     - Chain of Custody & Verification Log
     - Recommended Operational Actions
  3. Zero fabricated legal certificates, zero accusatory assertions, 100% verifiable citations.
- **Closing Punchline:**
  > *"Network Intel AI ko judge ya prosecutor nahi banata; yeh investigator ko unka sabse power-packed, verifiable, and evidence-grounded workbench deta hai."*

---

## Skeptical Judge Q&A Cheat Sheet

| Judge Question | Winning Technical Response |
|----------------|----------------------------|
| **"Kya aapka system court mein admissible evidence produce karta hai?"** | *"Nahi sir, aur hum aisi koi jhoothi claim nahi karte. Hamara system Court Dossier create nahi karta, balki ek Internal Investigation Analysis Draft generate karta hai jo IO ko lead deta hai. Har fact ka raw SHA-256 hash aur row/span locator recorded hota hai jise IO actual case diary mein cross-examine kar sakte hain."* |
| **"Agar do logo ke paas same phone ya car ho, toh kya system unhe auto-merge kar dega?"** | *"Kabhi nahi. Hamare entity resolution engine mein auto-merge prohibited hai. Vehicle ko hum property consider karte hain, identity proof nahi. Do logo ka vehicle match hone par bhi score sirf 0.100 rehta hai. Final decision hamesha human investigator ka hota hai with audit reason."* |
| **"LLM hallucination ko kaise control karte ho?"** | *"LLM ko raw database ka direct access hi nahi hai. Backend pehle deterministic FindingPacket banata hai with allowlisted fact IDs. LLM sirf us packet ko rephrase karta hai under strict JSON schema. Agar LLM ne koi naya number, entity, ya prohibited word ('guilty', 'criminal') introduce kiya, toh validator usse reject karke deterministic fallback show karta hai."* |
