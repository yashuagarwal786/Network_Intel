# Technical truth audit

Verified 5 September 2026. This is a prototype over synthetic data. Test success is not a real-world accuracy measure.

| Claim in PPT | Verified from | Implemented? | Safe to tell judges? |
|---|---|---|---|
| Four controlled input types | backend/intake_parser.py; tests/test_intake.py | Yes | Yes, controlled formats only |
| spaCy en_core_web_sm extracts entities | backend/ner_service.py; tests/test_ner.py | Yes | Yes, constrained English NER with review and fallback |
| Regex extracts identifiers | backend/intake_parser.py | Yes | Yes |
| NetworkX bounded paths | backend/demo_paths.py; tests/test_golden_flow.py | Yes | Yes, recorded associations, not proof of coordination |
| Connected components | backend/lead_engine.py transfer_sequences | Yes | Yes, account connectivity within a time window |
| Isolation Forest triage | backend/behavioral_profiler.py; tests/test_anomaly.py | Yes | Yes, secondary case-cohort anomaly triage, not guilt prediction |
| Rule-based lead generation | backend/lead_engine.py | Yes | Yes, explicit thresholds and evidence gating |
| Human-reviewed reversible identity | backend/resolution.py; tests/test_resolution.py | Yes | Yes |
| SQLite decisions and audit | backend/resolution.py; review_store.py; activity.py | Yes | Yes, no cryptographic tamper-resistance claim |
| React, TypeScript, Cytoscape | frontend/package.json | Yes | Yes |
| FastAPI APIs | backend/main.py; tests/test_backend.py | Yes | Yes |
| 98 tests passed | Fresh .venv/Scripts/python.exe -m pytest -q | Yes | Yes, 98 passed with 2 dependency warnings in 22.72 seconds |
| 11 calls; 2/day baseline; 3 transfers in 75 minutes; 6-hop path | lead_engine.py; tests/test_golden_flow.py; artifacts/first-round/api | Synthetic demonstration | Yes, label synthetic and explain baseline |
| Prototype screenshots | artifacts/first-round/screenshots/03-network-path.png and 04-lead-explanation.png | Actual stored UI captures | Yes, existing synthetic demo captures |
| Reduced repeated cross-referencing | Workflow design | Expected benefit | Yes as potential impact; no measured savings claimed |
| Agency deployment and large-scale accuracy | Not evaluated | No | Roadmap only |
| Authentication, encryption, protected audit storage | SIH-FIRST-ROUND-EVIDENCE.md limitations | No production implementation verified | Roadmap only |

## Format audit

Six slides including title, using the supplied PPTX directly. Retained original slide dimensions, masters, logos, team badges, SIH footer tags and required section headings. The instruction-only seventh slide is excluded. No extra backup slides are added to the submission. Team identity and problem statement fields remain explicit placeholders until provided.

## Judge perspective audit

- Domain: shows cross-source correlation; official PS alignment needs the missing PS details.
- Technical: separates NLP, graph algorithms, temporal rules and Isolation Forest.
- Product: shows actual graph and lead screens with evidence review.
- SIH: uses all six required sections with implementation and feasibility evidence.
- Skeptical: labels synthetic data and avoids accuracy, guilt and production-security claims.
