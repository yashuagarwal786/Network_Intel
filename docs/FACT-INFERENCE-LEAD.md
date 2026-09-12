# Epistemic Architecture: Facts, Inferences, and Leads

> **Core Axiom:**  
> *"Evidence is recorded. Inferences are computed. Decisions are made by humans."*

In investigative computing, confusion between what a source said, what an algorithm inferred, and what an investigator decided is the primary cause of wrongful accusations and legal failure.

Network Intel enforces strict technical and epistemic boundaries between these three layers.

---

## 1. The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: HUMAN DECISIONS & LEADS                           │
│ - Investigator Verification Reviews                         │
│ - Entity Resolution Decisions & Justifications              │
│ - Surfaced Lead Queue (Ordered by Review Urgency)           │
│ - Immutable Audit Trail (Who decided what, when, and why)   │
└──────────────────────────────▲──────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│ LAYER 2: COMPUTED INFERENCES & PROJECTIONS                  │
│ - Bounded Shortest Path Traversal (Breadth-First Search)    │
│ - Rule-Based Entity Resolution Scoring (Bounded [0.0, 1.0]) │
│ - Cross-Modal Corroboration Corridors                       │
│ - Epistemic Status Tracking (UNVERIFIED -> VERIFIED)        │
└──────────────────────────────▲──────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│ LAYER 1: RAW SOURCE EVIDENCE (IMMUTABLE)                    │
│ - Verifiable SHA-256 Hashes of Source Documents             │
│ - Exact Character Spans (start_offset, end_offset)          │
│ - Row & Line Identifiers from Original Raw Files            │
│ - Zero Auto-Modifications / Raw Excerpt Preservation        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Epistemic States Matrix

Every entity and relationship in Network Intel carries an explicit epistemic status:

| Status Code | Epistemic Meaning | Graph Display | Graph Filter Behavior |
|-------------|-------------------|---------------|-----------------------|
| `EXTRACTED_UNVERIFIED` | Extracted by deterministic rules or spaCy NER from raw file. Not verified by a human. | Dashed grey edge | Hidden when "Verified only" is ON |
| `INVESTIGATOR_VERIFIED` | Human investigator reviewed raw source evidence and verified the link. | Solid green edge (2.4px) | Visible always |
| `INVESTIGATOR_CORROBORATED` | Multiple independent source documents confirm the relationship. | Thick teal edge (3.2px) | Visible always |
| `INFERRED_CANDIDATE` | Surfaced algorithmically via multi-hop path traversal or temporal correlation. | Dotted purple edge (2.0px) | Hidden when "Verified only" is ON |
| `INVESTIGATOR_REJECTED` | Human investigator reviewed and determined this link is a false positive. | Completely removed from graph | Excluded from all projections |

---

## 3. What Network Intel NEVER Does

1. **No Crime Prediction:** We do not compute "risk scores" or "probability of guilt".
2. **No Autonomous Merges:** Two records are never merged automatically, even with identical names or phone numbers.
3. **No Fabricated Legal Weight:** We do not issue "Court Certifications" or claim that AI output constitutes judicial proof.
4. **No Unconstrained LLM Generation:** The language model cannot search databases, create relationships, or output un-grounded numbers.
