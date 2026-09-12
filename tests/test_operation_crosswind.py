from pathlib import Path
from backend.intake_store import IntakeStore
from backend.intake_models import UploadSource, CreateCaseInput
from backend.lead_engine import compute_path

ROOT = Path(__file__).parents[1] / 'demo-data' / 'live-demo-cases' / 'operation-crosswind'
KINDS = {
    'report.txt': 'Report',
    'cdr.csv': 'CDR',
    'transactions.csv': 'Transaction',
    'vehicles.csv': 'Vehicle',
}

def test_operation_crosswind_corridor_and_isolation(tmp_path):
    store = IntakeStore(tmp_path / 'crosswind.sqlite3')
    store.create_case(CreateCaseInput(
        name='Operation Crosswind',
        reference='NI-2026-025',
        purpose='Interstate narcotics and Hawala corridor demonstration.',
        event_timestamp='2026-08-18T20:00:00+05:30'
    ))

    # Ingest all 4 files
    for p in sorted(ROOT.iterdir()):
        kind_key = p.name.split('-', 1)[1]
        source_type = KINDS[kind_key]
        store.upload(UploadSource(
            filename=p.name,
            source_type=source_type,
            content=p.read_text(encoding='utf-8')
        ))

    summary = store.process()
    assert summary.records_processed >= 20
    assert summary.rejected_records == 0

    from backend import main
    repo = store.augment(main.repository)
    assert len(repo.entities) >= 10
    assert len(repo.relationships) >= 8

    # Find anchor entity IDs
    tariq = next(n for n in repo.entities.values() if 'tariq' in n.display_label.casefold())
    aman = next(n for n in repo.entities.values() if 'aman' in n.display_label.casefold())

    # Compute path
    result = compute_path(repo, tariq.id, aman.id, max_depth=8)
    assert result is not None
    # 4 to 6 hops
    assert 4 <= result.path_length <= 6
    assert len(result.evidence_ids) >= 4

    # Verify noise isolation: Rohan Mehra and Suresh Gupta are NOT in the corridor
    corridor_labels = [repo.entities[nid].display_label.casefold() for nid in result.node_ids]
    assert not any('rohan' in lbl for lbl in corridor_labels)
    assert not any('suresh' in lbl for lbl in corridor_labels)
