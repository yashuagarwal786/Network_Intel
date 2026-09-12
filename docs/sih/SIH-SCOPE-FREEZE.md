# VEIL — SIH first-round scope freeze

## Primary judge route

1. Case Overview
2. Data Sources
3. Entity Resolution
4. Network
5. Lead Inbox and Lead 17
6. Evidence drawer
7. Human review and Audit Trail

Timeline is the preferred follow-up screen when judges ask about chronology.

## Secondary demonstrations

Report extraction and Behavioral Profiles remain available as tabs within Data Sources. They are excluded from the timed presentation. Demonstrate them only when a judge asks about text extraction or broader analytical exploration.

Behavioral profiles must always be described as statistical triage. An anomaly is not crime, guilt, leadership or a verified relationship.

## Frozen technical boundary

- React and TypeScript frontend with Cytoscape.
- FastAPI typed APIs.
- NetworkX traversal and graph analysis.
- Controlled synthetic JSON/CSV/TXT inputs.
- SQLite for reversible decisions and audit persistence.
- No external AI API required for the primary route.

Do not add databases, distributed services, authentication, facial recognition, link prediction, external LLMs or new analytical models before first-round submission.

## Change gate

Accept only changes that fix a demonstrated bug, strengthen evidence traceability, improve the timed presentation, correct a misleading claim, or repair a submission artifact. Re-run backend tests, lint, type checking, production build and browser smoke tests after accepted changes.
