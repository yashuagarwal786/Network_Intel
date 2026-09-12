# Network Intel UI Audit

## Scope

Network Investigation flow: find entities → discover connection → inspect graph → understand why it matters → verify evidence → human review.

## Captured steps

1. **Current network workspace — needs polish**  
   Screenshot: `artifacts/network-intel-audit/01-current-network.png`  
   The graph is understandable, but VEIL branding remains prominent, copper reads as a theme rather than a semantic system, the connection finder resembles a standard form, and the default inspector lacks an immediate intelligence summary.

2. **Final connection-path state — healthy**  
   Screenshot: `artifacts/network-intel-audit/02-final-path.png`  
   Network Intel branding is clear, the violet path dominates without obscuring context, unrelated nodes dim correctly, the Signal Corridor mirrors the graph path, and the inspector separates review posture, evidence coverage, related leads, source verification, and explanation.

## Highest-impact changes implemented

- Replaced visible VEIL branding with Network Intel and added an original violet network-signal mark.
- Converted the layout from horizontal editorial navigation to a compact command-console rail.
- Turned Find Connection into a labeled query ribbon with a dominant violet CTA.
- Added a default-open Intelligence Inspector and a path-specific intelligence hierarchy.
- Added a real, interactive Signal Corridor derived from the computed backend path.
- Strengthened selected-path styling and dimmed unrelated graph elements.
- Kept green for trusted/source-backed states and muted red for risk/review states.

## Accessibility notes

- Primary controls retain accessible names and visible focus states.
- Meaning is not conveyed by color alone: risk, evidence, source, and review labels remain textual.
- The inspector and Signal Corridor remain keyboard-addressable through native buttons and selects.
- Screenshot review cannot prove full keyboard order, screen-reader narration quality, or contrast ratios in every state; those require dedicated automated and manual accessibility testing.
