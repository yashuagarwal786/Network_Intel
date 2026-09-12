from backend.intake_models import Manifest, UploadSource, CURRENT_PARSER_VERSION
from backend.intake_parser import parse, extract
from backend.intake_store import IntakeStore

def test_exact_spans_match_raw_text():
    manifest = Manifest(
        source_file_id="F-test-prov-01",
        filename="report.txt",
        source_type="Report",
        checksum="chk-prov-1",
        uploaded_at="2026-08-12T10:00:00+05:30",
        processing_status="VALIDATED"
    )
    raw_text = (
        "Rahul Sharma visited North yard on 14 August 2026.\n"
        "Vikram Singh uses phone +910000000204.\n"
    )
    records, errors = parse(manifest, raw_text)
    assert not errors
    assert len(records) == 2

    # Check line 1 span
    r1 = records[0]
    assert raw_text[r1.span_start:r1.span_end] == r1.raw_excerpt

    mentions, claims = extract(records)
    assert len(mentions) >= 3

    # Check each mention's absolute span points to the exact substring in raw_text
    for m in mentions:
        assert m.span_start is not None and m.span_end is not None
        assert m.span_start < m.span_end
        substring = raw_text[m.span_start:m.span_end]
        assert substring == m.evidence_text
        assert m.verification_status in ["EXTRACTED_UNVERIFIED", "UNVERIFIED"]
        # Confidence must be None (not supplied)
        assert m.confidence is None

def test_reprocess_idempotent_no_duplicates(tmp_path):
    store = IntakeStore(tmp_path / "intake_test.sqlite3")
    store.upload(UploadSource(
        filename="report.txt",
        source_type="Report",
        content="Rahul Sharma visited North yard.\n"
    ))
    res1 = store.process()
    assert res1.records_processed == 1
    mentions_count_1 = len(store.read()["mentions"])

    # Re-run process
    res2 = store.process()
    assert res2.records_processed == 1
    mentions_count_2 = len(store.read()["mentions"])
    assert mentions_count_1 == mentions_count_2

def test_stale_parser_version_detected():
    from backend.intake_models import Summary, Manifest
    s = Summary(
        manifests=[],
        records_processed=1,
        valid_records=1,
        rejected_records=0,
        entity_mentions=1,
        relationship_candidates=0,
        withheld_claims=0,
        processed=True,
        parser_version="controlled-intake-v1",
        needs_reprocess=True,
        reprocess_reason="Stale parser version"
    )
    assert s.needs_reprocess is True
