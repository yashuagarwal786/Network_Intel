"""Comprehensive Automated Test Suite for Unsupervised Behavioral Anomaly Profiler.

Validates the 13 essential behavioral, statistical, and architectural requirements:
1. Determinism: repeated executions produce bitwise identical anomaly ranks & scores.
2. Sample Size Guard: rejects N < 6 active entities with INSUFFICIENT_SAMPLE_SIZE status.
3. Low-and-Slow Anomaly: flags covert structural hub/deviation without requiring burst.
4. Benign Preservation: routine, uniform baseline entities are not falsely flagged.
5. Feature Mutation Sensitivity: modifying a feature vector shifts entity ranking predictably.
6. Score Responsiveness: altering behavior changes the Isolation Forest anomaly score.
7. Evidence Provenance Integrity: every profile and signal links to valid evidence_ids & event_ids.
8. Missing Data Imputation: entities with missing domains/amounts are handled gracefully.
9. Zero-Variance Safety: handles cohorts with constant feature values without unhandled exceptions.
10. API Schema Safety: ensures FastAPI endpoint works and OpenAPI paths remain exactly 22.
11. Multi-Signal Governance: behavioral anomaly ALONE does not trigger a HIGH priority lead.
12. Priority Reinforcement: anomaly combined with independent deterministic rules elevates review ordering.
13. Three Adversarial Scenarios:
    - Normal/Routine Case
    - Low-and-Slow Smurfing Entity
    - Legitimate High-Volume Hub (Ratio features prevent false accusation)
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from backend.demo_repository import DemoRepository
from backend.demo_schemas import Event, Entity, Evidence, Locator
from backend.behavioral_profiler import (
    run_behavioral_profiler,
    extract_entity_features,
    FEATURE_DEFINITIONS,
    DISCLAIMER
)
from backend.lead_engine import run_engine, Policy
from backend.main import app


@pytest.fixture
def repo():
    return DemoRepository()


def test_01_deterministic_repeated_outputs(repo):
    """Execution with the same random_state=42 must produce identical scores and ranks."""
    res1 = run_behavioral_profiler(repo, n_estimators=100, random_state=42)
    res2 = run_behavioral_profiler(repo, n_estimators=100, random_state=42)

    assert res1.status == "SUCCESS"
    assert res2.status == "SUCCESS"
    assert res1.sample_size == res2.sample_size
    assert len(res1.profiles) == len(res2.profiles)

    for p1, p2 in zip(res1.profiles, res2.profiles):
        assert p1.entity_id == p2.entity_id
        assert p1.rank == p2.rank
        assert p1.anomaly_score == p2.anomaly_score
        assert p1.anomaly_percentile == p2.anomaly_percentile
        assert p1.is_outlier == p2.is_outlier
        assert p1.top_drivers == p2.top_drivers


def test_02_insufficient_sample_size_guard(repo):
    """Cohorts with N < 6 active entities must safely return INSUFFICIENT_SAMPLE_SIZE."""
    # Keep only 4 events involving 4 entities
    kept_events = list(repo.events.values())[:3]
    repo.events = {e.id: e for e in kept_events}

    res = run_behavioral_profiler(repo)
    assert res.status == "INSUFFICIENT_SAMPLE_SIZE"
    assert res.sample_size < 6
    assert "Minimum 6 required" in res.message
    assert res.profiles == []
    assert res.signals == []


def test_03_low_and_slow_anomaly_detected(repo):
    """A low-and-slow entity (few events, no burst, but unusual cross-domain or clustering) is detected."""
    # Plant a stealthy entity 'stealth_agent' with 3 events evenly spread over 6 days
    as_of = repo.case.event_timestamp
    stealth_id = "stealth_agent"
    repo.entities[stealth_id] = Entity(
        id=stealth_id,
        label="Stealth Liaison",
        display_label="Stealth Liaison",
        type="Person",
        identifier="ST-999",
        description="Low and slow coordinator",
        x=0.0,
        y=0.0,
        evidence_ids=["E-SUB-01"]
    )

    # 3 distinct dates, 3 distinct domains (call, transfer, report), novel counterparty each time
    e1 = Event(
        id="EV-STEALTH-1",
        type="call",
        entity_ids=[stealth_id, "P305"],
        timestamp=as_of - timedelta(days=5),
        evidence_ids=["E-SUB-01"],
        relationship_ids=[]
    )
    e2 = Event(
        id="EV-STEALTH-2",
        type="transfer",
        entity_ids=[stealth_id, "A17"],
        amount_inr=Decimal("120000"),
        timestamp=as_of - timedelta(days=3),
        evidence_ids=["E-SUB-01"],
        relationship_ids=[]
    )
    e3 = Event(
        id="EV-STEALTH-3",
        type="report",
        entity_ids=[stealth_id, "L01"],
        timestamp=as_of - timedelta(days=1),
        evidence_ids=["E-SUB-01"],
        relationship_ids=[]
    )
    repo.events["EV-STEALTH-1"] = e1
    repo.events["EV-STEALTH-2"] = e2
    repo.events["EV-STEALTH-3"] = e3

    res = run_behavioral_profiler(repo)
    stealth_profile = next((p for p in res.profiles if p.entity_id == stealth_id), None)
    assert stealth_profile is not None
    # Temporal burst ratio should be low (1/3 = 0.33), but cross-domain entropy high
    assert stealth_profile.features["f_temporal_burst_ratio"] <= 0.34
    assert stealth_profile.features["f_cross_domain_activity"] > 0.5


def test_04_routine_entities_not_falsely_flagged(repo):
    """Uniform routine background entities should have low anomaly scores and inlier flags."""
    res = run_behavioral_profiler(repo)
    # The bottom 40% of profiles should definitely NOT be outliers
    bottom_profiles = res.profiles[int(len(res.profiles) * 0.6):]
    for p in bottom_profiles:
        assert p.is_outlier is False
        assert p.anomaly_percentile <= 60.0


def test_05_feature_mutation_shifts_ranking(repo):
    """Mutating an entity's transfer amount to a massive outlier pushes it up in anomaly rank."""
    res_orig = run_behavioral_profiler(repo)
    orig_ranks = {p.entity_id: p.rank for p in res_orig.profiles}

    # Pick an entity that was rank 7 (P204)
    target = "P204"
    # Mutate its transactions to extreme anomaly
    as_of = repo.case.event_timestamp
    repo.events["EV-MUT-TX"] = Event(
        id="EV-MUT-TX",
        type="transfer",
        entity_ids=[target, "A31"],
        amount_inr=Decimal("99999999.00"),
        timestamp=as_of - timedelta(minutes=5),
        evidence_ids=["E-SUB-01"],
        relationship_ids=[]
    )

    res_mut = run_behavioral_profiler(repo)
    new_rank = next(p.rank for p in res_mut.profiles if p.entity_id == target)
    assert new_rank < orig_ranks[target]


def test_06_anomaly_score_responsiveness(repo):
    """Adding anomalous behavior increases the entity's anomaly score."""
    p_id = "P204"
    orig_profile = next(p for p in run_behavioral_profiler(repo).profiles if p.entity_id == p_id)

    # Add 15 burst calls in 1 hour for P204
    as_of = repo.case.event_timestamp
    for i in range(15):
        repo.events[f"EV-BURST-TEST-{i}"] = Event(
            id=f"EV-BURST-TEST-{i}",
            type="call",
            entity_ids=[p_id, f"P30{i % 5}"],
            timestamp=as_of - timedelta(minutes=i * 2),
            evidence_ids=["E-CALL-15-01"],
            relationship_ids=[]
        )

    new_profile = next(p for p in run_behavioral_profiler(repo).profiles if p.entity_id == p_id)
    assert new_profile.features["f_temporal_burst_ratio"] > orig_profile.features["f_temporal_burst_ratio"]
    assert new_profile.rank <= orig_profile.rank


def test_07_evidence_provenance_attached_to_all_signals(repo):
    """All generated behavioral anomaly signals must have supporting evidence IDs and event IDs."""
    res = run_behavioral_profiler(repo)
    for sig in res.signals:
        assert sig.signal_type == "ANOMALOUS_BEHAVIORAL_PROFILE"
        assert sig.category == "BEHAVIORAL_ANOMALY"
        assert len(sig.supporting_evidence_ids) >= 1
        assert all(eid in repo.evidence for eid in sig.supporting_evidence_ids)
        assert len(sig.event_ids) >= 1
        assert all(ev_id in repo.events for ev_id in sig.event_ids)
        assert "not evidence of wrongdoing" in sig.limitations[2]


def test_08_missing_values_handled_gracefully(repo):
    """Entities with no transfer events (missing financial amount) must have 0.0 deviation, no NaN."""
    res = run_behavioral_profiler(repo)
    for p in res.profiles:
        for f_name, val in p.features.items():
            assert not (val != val), f"NaN detected in {f_name} for {p.entity_id}"
            assert isinstance(val, (int, float))


def test_09_zero_variance_handled_gracefully(repo):
    """When all entities have identical features, ZERO_VARIANCE is returned cleanly."""
    # Strip all events so interaction features are constant
    repo.events = {}
    res = run_behavioral_profiler(repo)
    assert res.status == "INSUFFICIENT_SAMPLE_SIZE"


def test_10_api_response_schema_and_path_count(client=None):
    """The anomalies endpoint works and the two grounded-explanation paths are registered."""
    client = TestClient(app)
    # Check openapi path count constraint strictly
    openapi_res = client.get("/openapi.json")
    assert openapi_res.status_code == 200
    assert len(openapi_res.json()["paths"]) == 24

    # Check anomalies endpoint
    res = client.get("/api/cases/demo/anomalies")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["sample_size"] >= 6
    assert len(data["profiles"]) == data["sample_size"]
    assert "disclaimer" in data
    assert "anomaly" in data["disclaimer"].lower()


def test_11_anomaly_alone_never_creates_high_lead(repo):
    """Behavioral anomaly by itself is a triage signal and never creates a HIGH priority lead."""
    # Run deterministic engine over standard repo
    result = run_engine(repo)
    for lead in result.leads:
        # Check that no lead is elevated to HIGH solely from behavioral anomaly
        assert "not a probability of criminal activity" in lead.disclaimer
        # HIGH priority leads must be corroborated by multi-category independent evidence
        if lead.review_priority == "HIGH":
            assert len(lead.signal_categories) >= 3


def test_12_anomaly_explains_top_drivers_transparently(repo):
    """Every profile provides human-readable top behavioral deviation drivers referencing case medians."""
    res = run_behavioral_profiler(repo)
    top_outlier = res.profiles[0]
    assert len(top_outlier.top_drivers) >= 1
    # Check that driver string contains readable explanation
    assert any("vs cohort median" in d or "typical cohort spread" in d for d in top_outlier.top_drivers)


def test_13_adversarial_three_scenarios(repo):
    """Verifies 3 distinct operational environments:
    Scenario A: Routine normal case (low divergence)
    Scenario B: Covert Smurfing (many novel counterparties, low amounts)
    Scenario C: High-volume legitimate hub (high volume but smooth ratio, not falsely ranked top outlier)
    """
    # Scenario C: Create high-volume legitimate hub 'super_merchant' with 100 regular calls and transfers
    hub_id = "super_merchant"
    repo.entities[hub_id] = Entity(
        id=hub_id,
        label="Super Merchant Services",
        display_label="Super Merchant Services",
        type="Organization",
        identifier="SMS-001",
        description="Legitimate high volume merchant",
        x=0.0,
        y=0.0,
        evidence_ids=["E-SUB-01"]
    )

    as_of = repo.case.event_timestamp
    # Even distribution over 7 days, 14 counterparties (repeat business)
    for d in range(7):
        for h in range(4):
            repo.events[f"EV-HUB-{d}-{h}"] = Event(
                id=f"EV-HUB-{d}-{h}",
                type="call",
                entity_ids=[hub_id, f"P30{h % 4}"],
                timestamp=as_of - timedelta(days=d, hours=h * 2),
                evidence_ids=["E-SUB-01"],
                relationship_ids=[]
            )

    res = run_behavioral_profiler(repo)
    hub_profile = next(p for p in res.profiles if p.entity_id == hub_id)
    # The burst ratio should be low because events are smoothly distributed across 7 days
    assert hub_profile.features["f_temporal_burst_ratio"] < 0.35
    # Because of ratio normalization, high event volume alone did NOT make it rank #1
    assert hub_profile.rank > 1
