# Cycle 6 product audit

Scope: active VEIL screens and their drawers at 1366×768. Captured before product edits in artifacts/cycle6-audit. Legacy screens are not mounted. Classification covers repeated elements as groups; the same evidence button or status badge keeps the same classification wherever repeated.

| Screen / visible element | Classification | Finding and action |
|---|---|---|
| Shared case name/ID, Active Review, synthetic notice | Essential | Preserve persistent case context. |
| Shared navigation: Network, Data intake, Resolution review, Lead inbox, Audit | Essential | Preserve; make active state accurate and Network leave resolution cleanly. |
| Timeline and full evidence register navigation | Useful but secondary | Preserve for questions; rename Source records to Evidence register to distinguish 13 collections from four processed files. |
| Brand link, case button | Useful but secondary | Brand used a hash link; replace with a real network button. |
| Shield icons, live dots, monogram, footer | Decorative | Restrained existing styling retained; no new decorative imagery/animation. |
| “Leads, not accusations” and timezone footer | Essential | Preserve. |
| Network search, path endpoints, Find path, computed-hop badge | Essential | Keep. Rank canonical case records ahead of unmerged intake mentions so Enter on Rahul selects the intended record. |
| Network maximum-depth selector, full-network toggle, fit | Useful but secondary | Keep. Add zoom/reset controls requested for presentation reliability. |
| Graph type shapes/colors, labels, arrows, legend | Essential | Keep; deterministic display positions, visible selection and path states. |
| Graph unrelated supporting nodes and overlapping lower labels | Confusing | Reduce initial focus to relevant case records; full network remains available. |
| Graph repeated reconstruction/refit on detail changes | Broken behavior | Keep one Cytoscape instance, update only changed data, fit after hidden-to-visible transitions when needed. |
| Graph selection and evidence availability | Confusing / missing | Add distinct selected node/edge styling and a source-direction/evidence legend. |
| Lead inbox title, priority, generation time, review status | Essential | Preserve backend values and separate priority from decision. |
| Lead inbox priority filter and re-run | Useful but secondary | Preserve with empty/busy/error states. |
| Lead disclaimer, why/when, signal calculations, evidence | Essential | Preserve; move technical method details behind disclosures. |
| Lead review form above explanation | Confusing | Collapse behind Record investigator review; explanation is visible first. |
| Lead involved-entity links and limitations | Essential | Preserve. |
| Raw signal IDs/version/threshold JSON | Useful but secondary | Retain in Method, thresholds and limitations disclosure. |
| Entity drawer identity, aliases, source links, relationship links | Essential | Preserve, including original IDs after merge. |
| Relationship drawer type/direction/source-status and references | Essential | Preserve; investigator assessment does not rewrite source verification. |
| Evidence filename, type, exact locator, timestamp, excerpt, verification | Essential | Preserve exact values and responsive wrapping. |
| Evidence parser IDs, related entity/relationship buttons | Useful but secondary | Preserve traceability and navigation. |
| Evidence Back button | Essential | Preserve context. |
| Resolution queue, both names, recommendation, score disclaimer | Essential | Preserve. |
| Resolution narrow drawer and long stacked technical text | Confusing | Use existing workspace width for evidence and decision columns; graph returns on Network. |
| Resolution name/phone/vehicle features and evidence | Essential | Make all three easier to scan together. |
| Resolution reviewer, reason, Confirm/Reject/Defer/Undo | Essential | Preserve validation and reversible behavior. |
| Resolution algorithm policy, original summaries, decision IDs/history | Useful but secondary | Retain in expandable details. |
| Intake four filename/type/status cards | Essential | Two-column grid makes all four available together. |
| Intake processing counts and intentional rejected-row count | Essential | Preserve; rejected row is a labelled validation example, not an app failure. |
| Intake large upload/reset controls in initial view | Confusing | Collapse under Load or replace sample files. |
| Intake validation details, manifests/checksums, Records/Mentions/Claims tabs | Useful but secondary | Keep available without dominating the source overview. |
| Intake Continue to resolution / extracted graph | Essential / secondary | Preserve real actions. |
| Source register 13 collections labelled ambiguously | Confusing | Explain original collections versus four uploaded files. |
| Timeline cards/category/time/entity/evidence | Essential to secondary story | Preserve distinctions between source assertion, claim, signal and action. |
| Timeline date/type/entity/source/category filters | Useful but secondary | Preserve backend filtering and empty/loading/error states. |
| Audit actor/action/object/reason/state transition | Essential | Preserve, with review filter for the final judge step. |
| Audit exact state JSON and IDs | Useful but secondary | Keep expandable; show key status transition plainly. |
| Audit/timeline stale entity drawer | Useful but secondary | Drawer remains available as evidence context; it does not replace the activity list. |
| Fake actions, lorem ipsum, dead product routes | None found | No fabricated controls or placeholder prose found in active screens. Legacy code remains unmounted. |

Audit evidence:

1. 01-network-lead.png: working graph and lead, but review controls dominate first fold.
2. 02-intake.png: two of four files visible before scrolling; setup controls consume height.
3. 03-resolution.png: names/score visible, matching evidence below the fold.
4. 04-register.png: thirteen collections can be confused with four processed uploads.
5. 05-timeline.png: explicit categories and evidence; filters work but are secondary to judge flow.
6. 06-audit.png: action and state transition are legible; filter is needed to reach current review.
7. 07-evidence.png: exact source locator/excerpt and verification state are intact.

Accessibility findings: visible keyboard focus already exists on controls; disclosures need equally visible focus. Small graph labels and narrow layouts require runtime checks, not screenshot-only assurance. This audit does not claim full WCAG conformance. Final screenshots and executable smoke results are separate from these pre-change captures.
