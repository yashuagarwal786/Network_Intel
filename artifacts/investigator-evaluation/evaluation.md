# Network Intel — Controlled Prototype Evaluation Report

**Generated:** 2026-09-11T18:02:36.386147+00:00  
**Evaluation Target:** 9.0 / 10 internal prototype  
**Criteria Passed:** 12 / 12  

## Evaluation Matrix

| # | Criterion | Status | Technical Details |
|---|-----------|--------|-------------------|
| 01 | Exact Provenance Spans | **PASSED** | All mentions match exact substring spans in source text |
| 02 | Honest Extraction Methods | **PASSED** | Methods accurately declare deterministic vs NER without fake probabilities |
| 03 | Stale Parser Version Detection | **PASSED** | IntakeStore flags needs_reprocess when parser specs differ |
| 04 | Resolution Name Cleaning | **PASSED** | Source filenames are stripped from entity resolution comparison |
| 05 | Resolution Conflict Penalties | **PASSED** | Conflicting surnames receive <= 0.25 compatibility penalty |
| 06 | Vehicle Property Demotion | **PASSED** | Vehicles treated as corroborating property, never standalone proof of identity |
| 07 | Bounded Rule Score | **PASSED** | Rule scores bounded in [0.0, 1.0] and explicitly documented as not a probability |
| 08 | Epistemic Status Lifecycle | **PASSED** | Epistemic state correctly transitions from EXTRACTED_UNVERIFIED to INVESTIGATOR_VERIFIED |
| 09 | Graph Verification Gate | **PASSED** | Investigator-rejected claims are strictly excluded from graph augmentation |
| 10 | Multi Hop Crosswind Corridor | **PASSED** | Operation Crosswind verified with a 6-hop cross-modal corridor |
| 11 | Noise Entity Isolation | **PASSED** | Unrelated entities (Rohan Mehra, Suresh Gupta) remain isolated from corridor |
| 12 | Grounded Explanation Guardrails | **PASSED** | Strict guardrails against hallucinations, accusatory labels, and API absence |

## Investigator Positioning Summary

- **Evidence vs Inference:** Machine-extracted entities and claims start as `EXTRACTED_UNVERIFIED`.
- **Resolution Rules:** Fixed weights bounded in `[0.0, 1.0]`, clearly marked as non-probabilistic with conflict penalties.
- **Vehicle Property Demotion:** Shared vehicle records are corroborating property, not personal identity assertions.
- **AI Grounding:** Explanations strictly rephrase allowlisted finding facts with no guilt scoring or external numbers.
- **Multi-Hop Corridor:** Operation Crosswind demonstrates a 5-hop cross-source path with distractor entity isolation.