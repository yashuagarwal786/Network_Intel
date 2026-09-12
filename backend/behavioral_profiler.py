"""Unsupervised Multi-Modal Behavioral Anomaly Detection Profiler.

Core Principle:
The profiler is strictly an investigative TRIAGE tool.
It computes whether an entity's observed multimodal activity is statistically unusual
compared with other entities in the same case.
It NEVER predicts criminal probability, guilt, intent, or threat level.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Literal
import networkx as nx
import numpy as np
from sklearn.ensemble import IsolationForest

from .demo_schemas import Model
from .lead_models import TimeWindow, ComputedSignal

FEATURE_DEFINITIONS = [
    {
        "name": "f_temporal_burst_ratio",
        "label": "Temporal Burst Ratio",
        "description": "Proportion of total entity events concentrated within the single densest 24-hour window.",
        "type": "ratio",
        "range": "[0.0, 1.0]",
        "direction": "Higher indicates temporal concentration (burstiness) rather than smooth cadence."
    },
    {
        "name": "f_novel_counterparty_rate",
        "label": "Novel Counterparty Rate",
        "description": "Ratio of first-time counterparties observed in the case window relative to total observed counterparties.",
        "type": "ratio",
        "range": "[0.0, 1.0]",
        "direction": "Higher indicates rapid outward expansion of communication or financial contacts."
    },
    {
        "name": "f_amount_deviation",
        "label": "Amount Robust Deviation",
        "description": "Robust deviation (absolute deviation from case median normalized by IQR) of financial transfer values.",
        "type": "float",
        "range": "[0.0, inf)",
        "direction": "Higher indicates transfer amounts atypical compared to the case financial baseline."
    },
    {
        "name": "f_cross_domain_activity",
        "label": "Cross-Domain Activity Entropy",
        "description": "Normalized Shannon entropy across observable domains (telecom/calls, financial/transfers, intelligence/reports, vehicles).",
        "type": "ratio",
        "range": "[0.0, 1.0]",
        "direction": "Measures multi-modal breadth. 0 indicates single-channel activity; 1 indicates even spread across all 4 domains."
    },
    {
        "name": "f_graph_clustering_coefficient",
        "label": "Graph Clustering Coefficient",
        "description": "Local clustering coefficient in the case co-occurrence / interaction graph (undirected projection).",
        "type": "ratio",
        "range": "[0.0, 1.0]",
        "direction": "Measures degree to which an entity's neighbors are connected to each other (clique density vs bridge/hub)."
    }
]

DISCLAIMER = (
    "Behavioral anomaly scores measure statistical distance from case cohort norms. "
    "Statistical anomaly is NOT evidence of wrongdoing, criminality, guilt, or intent. "
    "Scores serve solely to prioritize manual analyst review order."
)


@dataclass
class EntityBehavioralProfile:
    entity_id: str
    entity_label: str
    entity_type: str
    total_events: int
    features: dict[str, float]
    raw_metrics: dict[str, Any]
    supporting_evidence_ids: list[str]
    event_ids: list[str]
    time_window: TimeWindow
    anomaly_score: float = 0.0
    anomaly_percentile: float = 0.0
    is_outlier: bool = False
    rank: int = 0
    top_drivers: list[str] = field(default_factory=list)
    feature_deviations: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class ProfilerResult:
    status: Literal["SUCCESS", "INSUFFICIENT_SAMPLE_SIZE", "ZERO_VARIANCE"]
    message: str
    sample_size: int
    min_required_sample_size: int
    case_id: str
    generated_at: datetime
    disclaimer: str
    feature_definitions: list[dict[str, Any]]
    cohort_stats: dict[str, dict[str, float]]
    profiles: list[EntityBehavioralProfile]
    signals: list[ComputedSignal]


def _shannon_entropy_ratio(counts: list[int]) -> float:
    """Computes normalized Shannon entropy in [0, 1] across non-zero categories."""
    total = sum(counts)
    if total == 0:
        return 0.0
    k = len(counts)
    if k <= 1:
        return 0.0
    probs = [c / total for c in counts if c > 0]
    if len(probs) <= 1:
        return 0.0
    ent = -sum(p * math.log2(p) for p in probs)
    max_ent = math.log2(k)
    return float(min(1.0, max(0.0, ent / max_ent)))


def extract_entity_features(repo, as_of: datetime, window_days: int = 7) -> list[EntityBehavioralProfile]:
    """Extracts 5 behavioral features for all active entities in the case up to as_of."""
    window_start = as_of - timedelta(days=window_days)
    
    # 1. Build interaction graph for clustering coefficient
    G = nx.Graph()
    for entity_id in repo.entities:
        G.add_node(entity_id)
    for r in repo.relationships.values():
        if r.source in repo.entities and r.target in repo.entities:
            G.add_edge(r.source, r.target)
    for e in repo.events.values():
        if e.timestamp <= as_of and len(e.entity_ids) >= 2:
            for i in range(len(e.entity_ids)):
                for j in range(i + 1, len(e.entity_ids)):
                    if e.entity_ids[i] in repo.entities and e.entity_ids[j] in repo.entities:
                        G.add_edge(e.entity_ids[i], e.entity_ids[j])
    
    clustering_dict = nx.clustering(G)
    
    # 2. Gather case transfer amounts for global median & IQR
    case_transfer_amounts = [
        float(e.amount_inr)
        for e in repo.events.values()
        if e.type == "transfer" and e.timestamp <= as_of and getattr(e, "amount_inr", None) is not None and e.amount_inr > 0
    ]
    if case_transfer_amounts:
        c_median = float(np.median(case_transfer_amounts))
        q75, q25 = float(np.percentile(case_transfer_amounts, 75)), float(np.percentile(case_transfer_amounts, 25))
        c_iqr = max(1.0, q75 - q25)
    else:
        c_median = 0.0
        c_iqr = 1.0

    # 3. Index events by entity
    entity_events: dict[str, list[Any]] = {eid: [] for eid in repo.entities}
    for e in repo.events.values():
        if e.timestamp <= as_of:
            for eid in e.entity_ids:
                if eid in entity_events:
                    entity_events[eid].append(e)

    profiles: list[EntityBehavioralProfile] = []

    for entity_id, events in sorted(entity_events.items()):
        if not events:
            continue
        
        entity = repo.entities[entity_id]
        events_sorted = sorted(events, key=lambda x: (x.timestamp, x.id))
        total_ev = len(events_sorted)
        
        # Feature 1: f_temporal_burst_ratio (max events in 24-hr sliding window / total events)
        max_in_24h = 1
        for i, ev in enumerate(events_sorted):
            cutoff = ev.timestamp + timedelta(hours=24)
            count = sum(1 for other in events_sorted[i:] if other.timestamp <= cutoff)
            if count > max_in_24h:
                max_in_24h = count
        f_burst = float(max_in_24h / total_ev) if total_ev > 0 else 0.0
        
        # Feature 2: f_novel_counterparty_rate
        # For call and transfer events, counterparties are other entity_ids
        counterparties: list[str] = []
        prior_counterparties: set[str] = set()
        recent_novel_counterparties: set[str] = set()
        
        for ev in events_sorted:
            others = [other for other in ev.entity_ids if other != entity_id]
            if ev.timestamp < window_start:
                prior_counterparties.update(others)
            else:
                for o in others:
                    if o not in prior_counterparties:
                        recent_novel_counterparties.add(o)
                    counterparties.append(o)
        
        distinct_total_cps = len(set(counterparties) | prior_counterparties)
        if distinct_total_cps > 0:
            f_novel_cp = float(len(recent_novel_counterparties) / distinct_total_cps)
        else:
            f_novel_cp = 0.0

        # Feature 3: f_amount_deviation
        entity_amounts = [
            float(ev.amount_inr)
            for ev in events_sorted
            if ev.type == "transfer" and getattr(ev, "amount_inr", None) is not None and ev.amount_inr > 0
        ]
        if entity_amounts:
            e_median = float(np.median(entity_amounts))
            f_amount_dev = float(abs(e_median - c_median) / c_iqr)
        else:
            f_amount_dev = 0.0

        # Feature 4: f_cross_domain_activity
        # Count events across: call, transfer, report, vehicle/other
        domain_counts = [
            sum(1 for ev in events_sorted if ev.type == "call"),
            sum(1 for ev in events_sorted if ev.type == "transfer"),
            sum(1 for ev in events_sorted if ev.type == "report"),
            sum(1 for ev in events_sorted if ev.type not in ["call", "transfer", "report"])
        ]
        f_cross_domain = _shannon_entropy_ratio(domain_counts)

        # Feature 5: f_graph_clustering_coefficient
        f_clustering = float(clustering_dict.get(entity_id, 0.0))

        # Supporting evidence & events
        ev_ids = sorted({eid for ev in events_sorted for eid in ev.evidence_ids if eid in repo.evidence})
        event_ids = [ev.id for ev in events_sorted]
        
        t_start = min(ev.timestamp for ev in events_sorted)
        t_end = max(ev.timestamp for ev in events_sorted)

        features = {
            "f_temporal_burst_ratio": round(f_burst, 4),
            "f_novel_counterparty_rate": round(f_novel_cp, 4),
            "f_amount_deviation": round(f_amount_dev, 4),
            "f_cross_domain_activity": round(f_cross_domain, 4),
            "f_graph_clustering_coefficient": round(f_clustering, 4)
        }
        raw_metrics = {
            "total_events": total_ev,
            "max_events_24h": max_in_24h,
            "novel_counterparty_count": len(recent_novel_counterparties),
            "total_counterparties": distinct_total_cps,
            "transfer_count": len(entity_amounts),
            "median_transfer_amount": float(np.median(entity_amounts)) if entity_amounts else None,
            "domain_counts": {
                "telecom_calls": domain_counts[0],
                "financial_transfers": domain_counts[1],
                "intelligence_reports": domain_counts[2],
                "vehicle_other": domain_counts[3]
            },
            "clustering_coefficient": f_clustering
        }

        profiles.append(EntityBehavioralProfile(
            entity_id=entity_id,
            entity_label=entity.label,
            entity_type=entity.type,
            total_events=total_ev,
            features=features,
            raw_metrics=raw_metrics,
            supporting_evidence_ids=ev_ids,
            event_ids=event_ids,
            time_window=TimeWindow(start=t_start, end=t_end)
        ))

    return profiles


def run_behavioral_profiler(
    repo,
    n_estimators: int = 100,
    random_state: int = 42,
    as_of: datetime | None = None
) -> ProfilerResult:
    """Executes the unsupervised Isolation Forest anomaly detection over active case entities.

    Guards:
    - If N < 6 active entities: returns INSUFFICIENT_SAMPLE_SIZE
    - If all entities have identical feature representations: returns ZERO_VARIANCE
    - Deterministic execution via fixed random_state.
    """
    if as_of is None:
        as_of = repo.case.event_timestamp.astimezone(timezone(timedelta(hours=5, minutes=30)))

    profiles = extract_entity_features(repo, as_of)
    sample_size = len(profiles)
    min_required = 6

    if sample_size < min_required:
        return ProfilerResult(
            status="INSUFFICIENT_SAMPLE_SIZE",
            message=f"Only {sample_size} active entities observed. Minimum {min_required} required for statistically valid isolation forest triage.",
            sample_size=sample_size,
            min_required_sample_size=min_required,
            case_id=repo.case.id,
            generated_at=as_of,
            disclaimer=DISCLAIMER,
            feature_definitions=FEATURE_DEFINITIONS,
            cohort_stats={},
            profiles=[],
            signals=[]
        )

    feature_keys = [f["name"] for f in FEATURE_DEFINITIONS]
    X = np.array([[p.features[k] for k in feature_keys] for p in profiles], dtype=float)

    # Check for zero-variance across all features
    variances = np.var(X, axis=0)
    if np.all(variances < 1e-9):
        return ProfilerResult(
            status="ZERO_VARIANCE",
            message="Zero variance detected across all behavioral features in this cohort. Isolation Forest requires variation.",
            sample_size=sample_size,
            min_required_sample_size=min_required,
            case_id=repo.case.id,
            generated_at=as_of,
            disclaimer=DISCLAIMER,
            feature_definitions=FEATURE_DEFINITIONS,
            cohort_stats={},
            profiles=profiles,
            signals=[]
        )

    # Calculate cohort baseline statistics (median, IQR) for explainability
    cohort_stats: dict[str, dict[str, float]] = {}
    for idx, k in enumerate(feature_keys):
        col = X[:, idx]
        med = float(np.median(col))
        q75, q25 = float(np.percentile(col, 75)), float(np.percentile(col, 25))
        std = float(np.std(col))
        iqr = float(q75 - q25) if (q75 - q25) > 1e-4 else (std if std > 1e-4 else 0.1)
        cohort_stats[k] = {
            "median": round(med, 4),
            "q25": round(q25, 4),
            "q75": round(q75, 4),
            "iqr": round(iqr, 4),
            "mean": round(float(np.mean(col)), 4),
            "std": round(float(np.std(col)), 4)
        }

    # Run Isolation Forest
    clf = IsolationForest(
        n_estimators=n_estimators,
        contamination="auto",
        random_state=random_state
    )
    clf.fit(X)

    # IsolationForest.score_samples returns negative anomaly score.
    # Lower (more negative) values indicate more anomalous / isolated samples.
    # We transform it into an intuitive anomaly score where higher = more anomalous.
    raw_scores = clf.score_samples(X)  # typically in [-0.8, -0.3]
    preds = clf.predict(X)            # -1 for outlier, 1 for inlier

    # Invert so higher score = higher anomaly: anomaly_score = -raw_score
    inv_scores = -raw_scores
    min_s, max_s = float(np.min(inv_scores)), float(np.max(inv_scores))
    span = max_s - min_s if max_s > min_s else 1.0

    # Sort indices by anomaly score descending
    order = np.argsort(-inv_scores)

    signals: list[ComputedSignal] = []

    for rank_idx, idx in enumerate(order):
        p = profiles[idx]
        norm_score = float((inv_scores[idx] - min_s) / span)
        # Percentile rank (0% to 100%): Rank 1 is top percentile (highest anomaly)
        percentile = float((sample_size - rank_idx) / sample_size * 100.0)

        p.anomaly_score = round(norm_score, 4)
        p.anomaly_percentile = round(percentile, 1)
        p.is_outlier = bool(preds[idx] == -1)
        p.rank = rank_idx + 1

        # Compute robust feature deviations and top 2-3 behavioral drivers
        feature_devs: dict[str, dict[str, Any]] = {}
        driver_candidates = []

        for f_idx, f_name in enumerate(feature_keys):
            f_val = p.features[f_name]
            f_med = cohort_stats[f_name]["median"]
            f_iqr = cohort_stats[f_name]["iqr"]
            dev_iqr = (f_val - f_med) / f_iqr
            feature_devs[f_name] = {
                "value": f_val,
                "cohort_median": f_med,
                "cohort_iqr": f_iqr,
                "iqr_deviation": round(float(dev_iqr), 2)
            }
            if dev_iqr > 0.5:
                driver_candidates.append((dev_iqr, f_name, f_val, f_med))

        driver_candidates.sort(key=lambda x: -x[0])
        top_drivers = []
        for dev, f_name, f_val, f_med in driver_candidates[:3]:
            f_def = next(d for d in FEATURE_DEFINITIONS if d["name"] == f_name)
            top_drivers.append(
                f"{f_def['label']}: observed {f_val:g} vs cohort median {f_med:g} (+{dev:.1f} IQR deviation)"
            )
        if not top_drivers:
            top_drivers.append("Activity metrics fall within typical cohort spread.")

        p.top_drivers = top_drivers
        p.feature_deviations = feature_devs

        # If entity is flagged as an outlier, generate a ComputedSignal
        if p.is_outlier and p.supporting_evidence_ids:
            sig = ComputedSignal(
                signal_id=f"SIG-BEH-{p.entity_id}",
                case_id=repo.case.id,
                signal_type="ANOMALOUS_BEHAVIORAL_PROFILE",
                category="BEHAVIORAL_ANOMALY",
                independent_category=True,
                title=f"Statistical Behavioral Outlier: {p.entity_label} ({p.anomaly_percentile:.0f}th %tile)",
                involved_entity_ids=[p.entity_id],
                time_window=p.time_window,
                baseline_definition=f"Cohorts of {sample_size} active entities in case {repo.case.id}. Unsupervised Isolation Forest (n_estimators={n_estimators}, contamination=auto, seed={random_state}).",
                observed_value={
                    "anomaly_score": p.anomaly_score,
                    "anomaly_percentile": p.anomaly_percentile,
                    "rank": p.rank,
                    "top_drivers": p.top_drivers,
                    "features": p.features,
                    "raw_metrics": p.raw_metrics
                },
                expected_value={
                    "cohort_median_features": {k: cohort_stats[k]["median"] for k in feature_keys}
                },
                calculation=(
                    f"Multimodal feature vector mapped via Isolation Forest tree ensemble. "
                    f"Anomaly score {p.anomaly_score:.2f} ({p.anomaly_percentile:.1f}th percentile). "
                    f"Top drivers: {'; '.join(p.top_drivers)}."
                ),
                threshold={
                    "model": "IsolationForest",
                    "contamination": "auto",
                    "min_sample_size": min_required
                },
                supporting_evidence_ids=p.supporting_evidence_ids,
                event_ids=p.event_ids,
                algorithm_version="isolation-forest-v1",
                limitations=[
                    DISCLAIMER,
                    "Unsupervised behavioral scoring does not verify ground truth, legality, or criminal intent.",
                    "Anomalous score indicates mathematical divergence from case cohort, not evidence of wrongdoing."
                ],
                generated_at=as_of
            )
            signals.append(sig)

    # Sort profiles by rank
    profiles.sort(key=lambda p: p.rank)

    return ProfilerResult(
        status="SUCCESS",
        message=f"Isolation Forest completed successfully over {sample_size} entities. {len(signals)} statistical outliers flagged for triage review.",
        sample_size=sample_size,
        min_required_sample_size=min_required,
        case_id=repo.case.id,
        generated_at=as_of,
        disclaimer=DISCLAIMER,
        feature_definitions=FEATURE_DEFINITIONS,
        cohort_stats=cohort_stats,
        profiles=profiles,
        signals=signals
    )
