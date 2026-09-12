# VEIL alternate-case live demo guide

## What these case packs prove

The alternate packs prove that VEIL accepts controlled investigation-style
records, validates them, extracts mentions and constrained relationship
candidates, preserves negation and links every result to a source location.

They do not replace Operation Trinetra as the main analytical demonstration.
Lead 17 uses the tested deterministic Trinetra replay data.

## Safest judge sequence

1. Run the normal Operation Trinetra golden flow first.
2. If a judge asks about ingestion, open **Data Sources**.
3. Expand **Upload source documents or reload demo batches**.
4. Choose one case pack from `demo-data/live-demo-cases`.
5. For each file, choose its matching source type and select the file.
6. Click the upload button after each selection.
7. Select **Process sources**.
8. Open **Records** to show exact rows and validation errors.
9. Open **Mentions** to show extracted identifiers and names.
10. Open **Claims** to show graph candidates, uncertain claims, negated claims
    and unsupported statements.
11. Select an evidence reference to show filename, row/span and raw excerpt.

## Best pack for each question

- **Can VEIL connect different data sources?** Use Operation Riverglass.
- **How do you avoid overclaiming?** Use Operation Cedar Loop.
- **What happens with benign or bad data?** Use Operation Northstar Fair.

## What to say

> These are controlled synthetic records. VEIL validates each source, extracts
> source-local mentions and proposes only tightly supported relationships.
> Negated and uncertain sentences remain reviewable evidence but do not become
> verified graph facts.

## What not to say

- Do not say an alternate pack proves a crime.
- Do not say the report extractor understands arbitrary documents.
- Do not say every unusual pattern becomes a lead.
- Do not say the alternate packs are separate persisted cases in the current UI.
- Do not say a machine-generated claim is verified.

## Restore the official demonstration

In **Data Sources**, expand the upload section and select
**Load official samples / reset intake**, then process the sources if the screen
does not show them as processed.

For a completely fresh rehearsal state, stop the demo server and run:

```powershell
cd "Z:\XLab\New\Network Intel"
.\.venv\Scripts\python.exe -m backend.serve_demo --reset --port 8000
```

