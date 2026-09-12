# AI system note

## What is AI here?

- spaCy `en_core_web_sm` suggests Person, Organization and Location mentions in free-text reports. Its output stays `UNVERIFIED` and records the exact source span and extraction method.
- Optional Groq (`openai/gpt-oss-20b`) rephrases an allowlisted packet of backend-computed facts. It does not receive authority to discover graph edges, assign guilt, rank suspects or create evidence.

## What is deterministic?

- Phone, account, vehicle, date and money extraction.
- EntityRuler fallback and reliable report/CSV relationship templates.
- Normalization, candidate blocking and fixed entity-resolution features.
- NetworkX paths, temporal signals, graph construction, evidence IDs and review/audit persistence.
- The evidence explanation shown when `GROQ_API_KEY` is absent, rate-limited, invalid or fails grounding validation.

## What can fail?

- Small spaCy models can miss or misclassify names, organizations and locations.
- A shared phone, account or vehicle can have legitimate multiple users.
- Rule templates have limited phrasing coverage and deliberately withhold unsupported or uncertain relations.
- Groq is an external, rate-limited service. Its draft can be rejected for unknown fact references, invented numbers or accusatory language.
- Neither a graph path nor temporal proximity establishes intent, causation or guilt.

## Why is human review required?

Extraction creates candidates, resolution creates suggestions, graph algorithms create findings, and the explainer creates readable wording. Only an investigator can inspect the cited source, consider missing context, Confirm/Reject a possible match and record a decision. Original mentions and evidence are preserved so that decisions remain reviewable and reversible.

## Runtime configuration

- No key: fully functional deterministic grounded explanation; the UI does not claim external AI ran.
- Optional free-tier Groq: set `GROQ_API_KEY` outside source control. `GROQ_MODEL` may override the default `openai/gpt-oss-20b`.
