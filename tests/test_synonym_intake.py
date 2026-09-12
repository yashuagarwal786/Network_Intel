from backend.intake_parser import parse, extract
from backend.intake_models import Manifest

def test_synonym_cdr_intake_different_order():
    manifest = Manifest(
        source_file_id="src-syn-01",
        filename="cdr_varied.csv",
        source_type="CDR",
        checksum="syn123",
        uploaded_at="2026-08-12T10:00:00+05:30",
        processing_status="VALIDATED"
    )
    # Different order and synonym column names
    text = (
        "Calling Number,Dialed Number,Call ID,Start Time,Duration Sec,Cell Tower\n"
        "+910000000101,+910000000204,CALL-SYN-101,2026-08-12T18:00:00+05:30,60,Rivergate depot\n"
    )
    records, errors = parse(manifest, text)
    assert not errors
    assert len(records) == 1
    rec = records[0]
    assert rec.status == "VALID"
    assert rec.normalized_fields["call_id"] == "CALL-SYN-101"
    assert rec.normalized_fields["caller_phone"] == "+910000000101"
    assert rec.normalized_fields["receiver_phone"] == "+910000000204"
    assert rec.normalized_fields["duration_seconds"] == "60"
    assert rec.normalized_fields["tower_location"] == "Rivergate depot"

    mentions, claims = extract(records)
    assert len(claims) == 1
    assert claims[0].relationship_type == "CALLED"
    phones = [m.normalized_value for m in mentions if m.kind == "Phone"]
    assert "+910000000101" in phones
    assert "+910000000204" in phones

def test_synonym_transaction_intake():
    manifest = Manifest(
        source_file_id="src-syn-02",
        filename="bank_statement.csv",
        source_type="Transaction",
        checksum="syn456",
        uploaded_at="2026-08-12T10:00:00+05:30",
        processing_status="VALIDATED"
    )
    text = (
        "Txn ID,Debit Account,Credit Account,Txn Date,Amount,Currency,Payment Mode\n"
        "TX-SYN-99,DEMO-A1001,DEMO-A2002,2026-08-13T12:00:00+05:30,5000.00,INR,UPI\n"
    )
    records, errors = parse(manifest, text)
    assert not errors
    assert len(records) == 1
    rec = records[0]
    assert rec.status == "VALID"
    assert rec.normalized_fields["transaction_id"] == "TX-SYN-99"
    assert rec.normalized_fields["sender_account"] == "DEMO-A1001"
    assert rec.normalized_fields["receiver_account"] == "DEMO-A2002"
    assert rec.normalized_fields["amount"] == "5000.00"

    mentions, claims = extract(records)
    assert len(claims) == 1
    assert claims[0].relationship_type == "TRANSFERRED_TO"

def test_unmappable_header_rejected():
    manifest = Manifest(
        source_file_id="src-syn-03",
        filename="unknown.csv",
        source_type="CDR",
        checksum="syn789",
        uploaded_at="2026-08-12T10:00:00+05:30",
        processing_status="VALIDATED"
    )
    text = "random_col1,random_col2\n1,2\n"
    records, errors = parse(manifest, text)
    assert len(errors) == 1
    assert "Header must match or map to required columns" in errors[0]
