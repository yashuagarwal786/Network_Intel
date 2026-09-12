from pathlib import Path

import pytest

from backend.intake_models import Manifest
from backend.intake_parser import digest, extract, parse


ROOT = Path(__file__).parents[1] / "demo-data" / "live-demo-cases"
KINDS = {
    "report": "Report",
    "cdr": "CDR",
    "transactions": "Transaction",
    "vehicles": "Vehicle",
}


@pytest.mark.parametrize(
    ("case_name", "expected_invalid", "expected_uncertain"),
    [
        ("operation-riverglass", 0, 0),
        ("operation-cedar-loop", 0, 1),
        ("operation-northstar-fair", 1, 0),
        ("operation-crosswind", 0, 0),
    ],
)
def test_live_demo_case_pack_remains_ingestible(
    case_name: str, expected_invalid: int, expected_uncertain: int
):
    totals = {"records": 0, "invalid": 0, "negated": 0, "uncertain": 0}

    for path in sorted((ROOT / case_name).iterdir()):
        source_type = KINDS[path.stem.split("-")[-1]]
        content = path.read_text(encoding="utf-8")
        checksum = digest(content)
        manifest = Manifest(
            source_file_id="F-" + digest(source_type + "|" + checksum)[:20],
            filename=path.name,
            source_type=source_type,
            checksum=checksum,
            uploaded_at="2026-09-05T00:00:00+00:00",
            processing_status="VALIDATED",
        )

        records, file_errors = parse(manifest, content)
        assert file_errors == []
        _, claims = extract(records)
        totals["records"] += len(records)
        totals["invalid"] += sum(record.status == "INVALID" for record in records)
        totals["negated"] += sum(claim.disposition == "NEGATED" for claim in claims)
        totals["uncertain"] += sum(claim.disposition == "UNCERTAIN" for claim in claims)

    assert totals["records"] >= 17
    assert totals["invalid"] == expected_invalid
    assert totals["negated"] == 1
    assert totals["uncertain"] == expected_uncertain
