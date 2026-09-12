from backend.resolution import clean_name, normalize, name_compatibility, proposals
from backend import main

def test_clean_name_strips_filenames():
    assert clean_name('Rahul Sharma (report.txt)') == 'Rahul Sharma'
    assert clean_name('Vikram Singh (cdr.csv)') == 'Vikram Singh'
    assert clean_name('R.K. Sharma') == 'R.K. Sharma'
    assert normalize('Rahul Sharma (report.txt)') == 'rahul sharma'

def test_conflicting_surnames_penalized():
    # Similar first names, but completely different multi-letter surnames
    score = name_compatibility('Vikram Singh', 'Vikram Patel')
    assert score <= 0.25

    # Initials matching is allowed when compatible
    compatible_score = name_compatibility('R.K. Sharma', 'Rahul Sharma')
    assert compatible_score >= 0.85

def test_shared_vehicle_not_strong_identity():
    matches = proposals(main.repository)
    # Check proposal where entities share a vehicle but not phone/account
    for p in matches.values():
        veh = next((f for f in p.feature_comparisons if f.feature == 'Exact shared vehicle'), None)
        phone = next((f for f in p.feature_comparisons if f.feature == 'Exact shared phone'), None)
        if veh and veh.value > 0 and (not phone or phone.value == 0):
            assert 'Vehicle' not in p.strong_identifier_matches
            assert p.recommendation != 'YES'
            assert 'Vehicles are corroborating property' in p.match_reason or 'No shared identifier' in p.match_reason or 'Possible match' in p.match_reason

def test_rule_score_bounded_and_not_probability():
    matches = proposals(main.repository)
    for p in matches.values():
        assert 0.0 <= p.score <= 1.0
        # Verification that each feature weight sums to <= 1.0
        total_weights = sum(f.weight for f in p.feature_comparisons)
        assert round(total_weights, 4) <= 1.0
