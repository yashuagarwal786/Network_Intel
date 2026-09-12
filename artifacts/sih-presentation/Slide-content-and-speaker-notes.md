# VEIL slide-by-slide content and speaking notes

The supplied SIH template controls the six-slide structure. Its SIH images, badges, footer tags, section headings, masters and dimensions are retained. Official identity details remain placeholders.


## Slide 1




TITLE PAGE
SMART INDIA HACKATHON 2026
Problem Statement ID: [TO FILL]
Problem Statement Title: [TO FILL]
Theme: [TO FILL]
PS Category: Software
Team ID: [TO FILL]
Team Name: [REGISTERED NAME]
VEIL: Evidence-first investigation workspace

Purpose: Introduce the project and official submission identity.

Speaker script: VEIL connects fragmented investigation-style records into a reviewable evidence graph. Our prototype links reports, call records, transactions and vehicles, then lets investigators inspect the source behind each lead. The demonstration uses synthetic data. Official problem and team details must be filled before submission.

Judge takeaway: A working evidence workflow with human decision authority.

Likely question: Is this deployed with an agency?
Answer: No. This is a local prototype using synthetic records. Agency integration and validation remain future work.


## Slide 2


IDEA TITLE
2
@SIH Idea submission- Template
Your Team Name
Proposed Solution (Describe your Idea/Solution/Prototype)
VEIL connects separate records into entities, relationships and explainable leads.
Detailed explanation of the proposed solution
Reports, CDR, transactions and vehicle records in one workspace.
How it addresses the problem
Investigators can follow a connection and open its exact source record.
Actual prototype: a computed, sourced association path. Synthetic data.
Innovation and uniqueness of the solution
Cross-source graph + provenance + reversible human review.

Purpose: Explain the workflow and its differentiation.

Speaker script: The challenge is connecting information across separate records. VEIL builds a graph with traceable source evidence. This actual prototype screenshot shows a computed association path. Unlike manual cross-referencing, the same workspace links the relationship to its evidence and preserves reversible identity decisions. A connection is a lead for review, not proof of wrongdoing.

Judge takeaway: The differentiator is continuity from record to graph to reviewed lead.

Likely question: What is novel beyond a graph viewer?
Answer: The backend combines source provenance, reviewed identity resolution, bounded traversal and evidence-gated signals within one investigator workflow.


## Slide 3


TECHNICAL APPROACH
3
@SIH Idea submission- Template
Your Team Name
Technologies to be used
React / TypeScript / Cytoscape: investigator interface
Python / FastAPI / NetworkX: APIs and graph analysis; JSON + SQLite: records and decisions
Methodology and process for implementation

Source files
›

Parse + extract
›

Review identity
›

Evidence graph
›

Signals + leads
›

Human review
ML / NLP
spaCy en_core_web_sm extracts report entities; regex extracts structured identifiers.
Graph algorithms
Bounded shortest paths and connected components expose recorded associations.
Rules + statistical ML
Temporal rules generate leads. Isolation Forest supports secondary anomaly triage.
Human decision
Review uncertain mentions, inspect source evidence, confirm or reject, retain audit history.

Purpose: Separate ML, deterministic algorithms and human authority.

Speaker script: Local spaCy identifies entities in free text, while regex handles exact structured identifiers. Human review controls uncertain identity merges. NetworkX computes graph paths. Explicit temporal rules generate evidence-backed leads. Isolation Forest is implemented as secondary statistical triage over case features. It does not predict guilt and does not drive the primary lead-priority policy. SQLite persists review decisions.

Judge takeaway: Different methods serve distinct, auditable roles.

Likely question: Why not use ML everywhere?
Answer: Exact identifiers and source-linked temporal rules benefit from deterministic behavior. Probabilistic NLP helps with unfamiliar text, but its output remains subject to review.


## Slide 4


FEASIBILITY AND VIABILITY
4
@SIH Idea submission- Template
Your Team Name
Analysis of the feasibility of the idea
Implemented: local frontend + backend, four input types, NER, graph traversal and evidence review.
Verification: 98 backend tests passed on 5 September 2026 (two dependency warnings).
Potential challenges and risks
Synthetic case only; real-world accuracy and throughput remain unmeasured.
NER errors, ambiguous identities, incomplete records and small anomaly cohorts can mislead.
Strategies for overcoming these challenges
Current controls: source provenance, unverified extraction, reversible review and sample guards.
Production roadmap: agency validation, authenticated roles, encryption and protected audit storage.
Scale after profiling: asynchronous ingestion and indexed graph persistence.

Purpose: Establish engineering feasibility without implying production readiness.

Speaker script: The current implementation runs locally and the backend test suite passed all 98 tests in this session. The main risks are data quality, extraction errors and prototype scale. Current controls include source traces and reversible human review. Production still needs authenticated access, encryption, stronger audit storage and evaluation on authorized representative data. We would profile workloads before choosing a larger graph store.

Judge takeaway: The prototype is testable, with clear production gaps.

Likely question: Do 98 tests prove accuracy?
Answer: No. They verify implementation behavior and synthetic scenarios. They do not estimate operational accuracy or investigative outcomes.


## Slide 5


IMPACT AND BENEFITS
5
@SIH Idea submission- Template
Your Team Name
Potential impact on the target audience
Investigators can connect scattered records and inspect why a lead deserves review.
Benefits of the solution
Less repeated cross-referencing.
Source-linked explanations.
Reviewable human decisions.
Synthetic demonstration
11 calls vs a 2/day baseline; 3 connected transfers over 75 minutes; a 6-hop path.
Together, these create a review-priority lead.
Expected benefits; no measured time savings or crime-detection claim.

Purpose: Connect the evidence workflow to user benefit.

Speaker script: In our synthetic case, a phone records eleven calls against a median baseline of two a day. Three connected transfers occur within seventy-five minutes, and a sourced six-hop path provides graph context. The backend combines these categories into a review-priority lead. The investigator can inspect the calculation and source evidence. We expect less repeated cross-referencing, but have not measured time savings.

Judge takeaway: VEIL surfaces the connection; the investigator decides what it means.

Likely question: Could this be ordinary activity?
Answer: Yes. Business calls and legitimate transfers can produce the same pattern. Review priority is not a probability of crime.


## Slide 6


RESEARCH  AND REFERENCES
6
@SIH Idea submission- Template
Your Team Name
Details / Links of the reference and research work
spaCy English pipeline
Local named-entity extraction; en_core_web_sm
https://spacy.io/models/en#en_core_web_sm
NetworkX shortest paths
Graph traversal methods used by the prototype
https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html
scikit-learn Isolation Forest
Unsupervised anomaly detection for secondary triage
https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
Project evidence and validation
Source: backend/ner_service.py, behavioral_profiler.py, demo_paths.py and lead_engine.py.
Evidence: tests/ (98 passed), artifacts/first-round/api/ and actual prototype screenshots.
Evaluation boundary: synthetic data; operational accuracy requires agency validation.

Purpose: Make the technical foundation and evidence verifiable.

Speaker script: These references document the underlying NLP, graph and anomaly methods. Our contribution is their integration with evidence provenance and investigator review. The repository supplies implementation evidence, tests and captured API outputs. Our evaluation uses synthetic records, so it cannot support real-world accuracy claims. We can now demonstrate the exact route from a source record to a reviewed lead.

Judge takeaway: Claims are inspectable and limitations explicit.

Likely question: Where is your evaluation dataset?
Answer: The repository contains synthetic demonstration records and test cases. Representative authorized agency data and independent validation remain future work.