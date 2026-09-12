# VEIL — judge Q&A guide

Keep each spoken answer under 25 seconds. Start with the direct answer, show one concrete proof in the interface, then state the limitation.

## What problem does VEIL solve?

“Investigators often receive reports, call records, transactions and vehicle records as separate files. VEIL turns authorized records into a typed entity graph, computes reviewable connections and surfaces leads with exact evidence. It reduces manual cross-referencing while keeping the investigator responsible for conclusions.”

Show: Case Overview → Data Sources → Network.

## What is innovative here?

“The value is the evidence chain across the full workflow. An investigator can move from a generated signal to the exact source row, review an uncertain identity match, compute a multi-hop path and record a reversible human decision. The system explains why something was surfaced rather than presenting an opaque risk score.”

Show: Lead 17 → communication signal → evidence drawer.

## Is Lead 17 hardcoded?

“No. The backend recomputes it deterministically from event records, graph context and documented thresholds. The compatibility lead fixture is empty. The frontend only renders the lead returned by the API.”

Show: Lead detail with `temporal-leads-v1`, calculations and evidence; optionally re-run the engine.

## How is the Rahul–Vikram path found?

“The frontend sends source, target and maximum depth to FastAPI. NetworkX performs bounded breadth-first shortest-path traversal over the current canonical graph projection. The response contains the nodes, relationships, direction of each traversal and evidence IDs. Display coordinates never affect the result.”

Show: Find Connection → six-hop path inspector.

## How do you prevent false identity merges?

“Similar names are only candidates. Exact identifiers carry more weight than name similarity, REVIEW proposals never merge automatically, and the investigator sees feature-level evidence before deciding. Confirmation changes the graph projection without deleting original mentions, and it can be undone.”

Show: Rahul/R.K. Sharma comparison; mention that Amit/A. Verma remains ambiguous.

## Does a HIGH lead mean high probability of crime?

“No. HIGH only means examine earlier because three evidence-backed categories overlap. It is a transparent queue policy, not a calibrated probability and not an accusation.”

Show: the amber disclaimer in Lead 17.

## Does an anomaly mean criminal activity?

“No. Anomaly means statistical distance from the selected synthetic cohort. It is secondary triage context and cannot establish crime, leadership or guilt. The primary demo uses explicit temporal and transaction calculations because they are easier to audit.”

Do not lead the demonstration with Behavioral Profiles.

## How do you preserve evidence provenance?

“Each extracted mention, relationship and signal carries evidence IDs. Evidence records contain the filename, source type, exact row or report span, raw excerpt, timestamp, parser version and verification state. The evidence drawer also links back to related entities and relationships.”

Show: `E-TX-01`, `transactions-2026-08-15.csv`, Row 2.

## Why use a graph database alternative such as NetworkX instead of Neo4j?

“For a controlled SIH prototype, NetworkX gives real traversal and analytics without deployment overhead. JSON fixtures and SQLite keep the demo deterministic. Neo4j could be evaluated later when scale and multi-user query requirements are measured.”

## Where is AI used?

“The core judge route does not depend on an external AI service. Controlled extraction combines deterministic parsing with constrained local entity extraction where available. Entity resolution and lead generation are explainable rule-driven analytical pipelines. This keeps the prototype repeatable and auditable.”

Avoid claiming universal document understanding or autonomous investigation.

## Why not use a large language model?

“The primary records are structured and the relationships must be traceable. Deterministic parsers are easier to validate and reproduce. An LLM could later assist with text interpretation behind strict provenance and review controls, but it is not required for this demonstration.”

## How is the negative sentence handled?

“The report statement that Rahul did not meet Vikram is preserved with negative polarity. The extractor does not create a positive MET relationship. Negated and uncertain statements remain reviewable source claims.”

Show: Data Sources → Claims if requested.

## What happens when an investigator submits a decision?

“The review is persisted with the reviewer, action, reason and timestamp. The lead status updates, and an audit event records the old and new state. Duplicate accidental submissions use an idempotency key.”

Show: Needs More Evidence → Audit Trail.

## Can audit records be changed?

“Normal application behavior only appends audit events. This prototype does not claim cryptographic tamper resistance. Production would add authenticated identities, access controls, signing or immutable storage according to agency policy.”

## What data did you train this on?

“The official demo is deterministic synthetic data created for the scenario. We did not train a crime-prediction model. The temporal evaluation uses planted signals and benign controls only to verify implementation behavior, not real-world accuracy.”

## What are the current limitations?

“One synthetic case, controlled input formats, heuristic entity matching, bounded in-memory graph analytics, self-declared reviewer identity and no production security deployment. These limits are explicit in the UI and evidence package.”

## How would this scale?

“First we would profile real authorized workloads. Likely changes include durable object storage, a production relational store, indexed graph persistence, asynchronous ingestion and role-based access. The evidence and API contracts can remain stable while storage evolves.”

Avoid promising national-scale throughput without measurements.

## How will you use the 36-hour finale?

“We would harden the already working vertical slice: strengthen ingestion validation, add representative evaluation cases, improve investigator workflows, run performance tests and package deployment. We would not spend the finale replacing proven components with unnecessary infrastructure.”

## What prevents misuse?

“VEIL separates evidence, extracted claims, analytical signals and human decisions. It labels synthetic and unverified data, shows uncertainty, requires review for ambiguous matches and avoids guilt probabilities. A real deployment would additionally require authorization, case isolation, retention controls and governance.”

## If the live demo fails

“We have a deterministic reset, captured screenshots and exported API responses. Those artifacts are clearly labelled as previous synthetic runs; they are never presented as live computation.”

Open [`SIH-FIRST-ROUND-EVIDENCE.md`](../../docs/sih/SIH-FIRST-ROUND-EVIDENCE.md) and the screenshot folder.

## Team rehearsal format

Run two rounds:

1. One member performs the 2:45 product demonstration without interruption.
2. Another member asks the questions above in random order.
3. The presenter must answer directly, show one piece of evidence, and state one limitation.
4. Stop answers that exceed 25 seconds and repeat them more simply.

Never say “crime probability,” “criminal community,” “mastermind,” “leader,” “confirmed suspect,” or “the AI proved.” Prefer “review priority,” “graph community,” “central entity,” “recorded association,” “candidate match,” and “the system surfaced this for human review.”
