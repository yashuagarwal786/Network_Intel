import { useState, useEffect } from 'react';
import { api } from '../api';
import {labColors} from '../designTokens';
import { Activity, AlertTriangle, ChevronRight, RefreshCw, BarChart2 } from 'lucide-react';


interface AnomalyProfile {
  entity_id: string;
  entity_label: string;
  entity_type: string;
  total_events: number;
  anomaly_score: number;
  anomaly_percentile: number;
  is_outlier: boolean;
  rank: number;
  top_drivers: string[];
  feature_deviations: Record<string, { value: number; cohort_median: number; cohort_iqr: number; iqr_deviation: number }>;
  features: Record<string, number>;
  raw_metrics: any;
  supporting_evidence_ids: string[];
  event_ids: string[];
}

interface FeatureDef {
  name: string;
  label: string;
  description: string;
  type: string;
  range: string;
  direction: string;
}

export default function BehavioralAnomalyView({
  onEvidence,
  onInspectEntity,
}: {
  onEvidence: (id: string) => void;
  onInspectEntity: (entityId: string) => void;
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<AnomalyProfile | null>(null);
  const [filterOutliersOnly, setFilterOutliersOnly] = useState(false);

  async function loadAnomalies() {
    setLoading(true);
    setError('');
    try {
      const res = await api.anomalies();
      setData(res);
      if (res.profiles && res.profiles.length > 0) {
        setSelectedEntity(res.profiles[0]);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to compute behavioral anomalies.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAnomalies();
  }, []);

  if (loading && !data) {
    return (
      <div className="anomaly-container" style={{ padding: '24px', textAlign: 'center' }}>
        <RefreshCw className="animate-spin" size={24} style={{ margin: '0 auto 12px' }} />
        <p>Computing unsupervised Isolation Forest behavioral profiles across case cohort…</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="anomaly-container" style={{ padding: '24px' }}>
        <div className="banner error" role="alert">
          <AlertTriangle size={18} />
          <div>
            <strong>Profiling Error</strong>
            <p>{error}</p>
          </div>
          <button onClick={loadAnomalies}>Retry</button>
        </div>
      </div>
    );
  }

  const profiles: AnomalyProfile[] = data?.profiles || [];
  const filteredProfiles = filterOutliersOnly ? profiles.filter(p => p.is_outlier) : profiles;
  const featureDefs: FeatureDef[] = data?.feature_definitions || [];
  const cohortStats = data?.cohort_stats || {};

  return (
    <div className="anomaly-view-root" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Banner */}
      <div style={{
        background: 'rgba(30, 41, 59, 0.7)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        padding: '16px 20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ maxWidth: '680px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Activity size={18} color="#38bdf8" />
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
              Unsupervised Behavioral Anomaly Profiler
            </h3>
            <span style={{
              background: 'rgba(56, 189, 248, 0.15)',
              color: labColors.cyan,
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '4px',
              border: '1px solid rgba(56, 189, 248, 0.3)'
            }}>
              Experimental Triage Aid • Isolation Forest (Statistical Only)
            </span>
          </div>
          <p style={{ margin: 0, fontSize: '0.85rem', color: labColors.muted, lineHeight: 1.4 }}>
            Unsupervised statistical triage. Measures distance from case cohort norms.
            <strong style={{ color: labColors.amber, marginLeft: '6px' }}>
              Anomaly ≠ Guilt. Scores reflect statistical divergence, not criminality.
            </strong>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={loadAnomalies}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '6px',
              color: '#f1f5f9',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            {loading ? 'Re-profiling…' : 'Re-run Isolation Forest'}
          </button>
        </div>
      </div>

      {/* Insufficient Sample Size Notification */}
      {data?.status === 'INSUFFICIENT_SAMPLE_SIZE' && (
        <div style={{
          background: 'rgba(234, 179, 8, 0.1)',
          border: '1px solid rgba(234, 179, 8, 0.3)',
          borderRadius: '8px',
          padding: '16px',
          color: '#fbbf24'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
            <AlertTriangle size={18} /> Insufficient Active Entity Sample Size
          </div>
          <p style={{ margin: '8px 0 0', fontSize: '0.9rem', color: '#e2e8f0' }}>
            {data.message} The model requires at least {data.min_required_sample_size} active entities to construct reliable isolation trees without high variance.
          </p>
        </div>
      )}

      {/* Main Grid: Entity Triage Ranking Table vs Deep-Dive Driver Inspector */}
      {data?.status === 'SUCCESS' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', minHeight: '480px' }}>
          {/* Left Column: Triage Ranking Table */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                  Case Entity Triage Queue ({profiles.length} profiled)
                </h4>
                <small style={{ color: labColors.muted }}>
                  Sorted by Anomaly Percentile (most statistically distant first)
                </small>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: labColors.secondary, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={filterOutliersOnly}
                  onChange={e => setFilterOutliersOnly(e.target.checked)}
                />
                Outliers only ({profiles.filter(p => p.is_outlier).length})
              </label>
            </div>

            <div style={{ overflowX: 'auto', maxHeight: '520px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: labColors.muted }}>
                    <th style={{ padding: '8px 6px' }}>Rank</th>
                    <th style={{ padding: '8px 6px' }}>Entity</th>
                    <th style={{ padding: '8px 6px' }}>Type</th>
                    <th style={{ padding: '8px 6px' }}>Percentile</th>
                    <th style={{ padding: '8px 6px' }}>Triage Flag</th>
                    <th style={{ padding: '8px 6px' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProfiles.map(p => {
                    const isSelected = selectedEntity?.entity_id === p.entity_id;
                    return (
                      <tr
                        key={p.entity_id}
                        onClick={() => setSelectedEntity(p)}
                        tabIndex={0}
                        onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();setSelectedEntity(p)}}}
                        style={{
                          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                          cursor: 'pointer',
                          background: isSelected ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                          transition: 'background 0.15s ease'
                        }}
                      >
                        <td style={{ padding: '8px 6px', fontWeight: 600, color: labColors.muted }}>#{p.rank}</td>
                        <td style={{ padding: '8px 6px', fontWeight: 600, color: labColors.text }}>
                          {p.entity_label}
                        </td>
                        <td style={{ padding: '8px 6px', color: labColors.secondary }}>
                          <span style={{
                            padding: '2px 6px',
                            background: 'rgba(255, 255, 255, 0.06)',
                            borderRadius: '4px',
                            fontSize: '0.75rem'
                          }}>
                            {p.entity_type}
                          </span>
                        </td>
                        <td style={{ padding: '8px 6px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <div style={{
                              width: '40px',
                              height: '6px',
                              background: 'rgba(255, 255, 255, 0.1)',
                              borderRadius: '3px',
                              overflow: 'hidden'
                            }}>
                              <div style={{
                                width: `${p.anomaly_percentile}%`,
                                height: '100%',
                                background: p.is_outlier ? labColors.amber : labColors.cyan,
                                borderRadius: '3px'
                              }} />
                            </div>
                            <span style={{ fontWeight: 600, color: p.is_outlier ? labColors.amber : labColors.secondary }}>
                              {p.anomaly_percentile.toFixed(0)}%
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '8px 6px' }}>
                          {p.is_outlier ? (
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              background: '#2b2214',
                              color: labColors.amber,
                              padding: '2px 6px',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: 600
                            }}>
                              <AlertTriangle size={11} /> Outlier
                            </span>
                          ) : (
                            <span style={{
                              color: '#64748b',
                              fontSize: '0.75rem'
                            }}>
                              Typical Cohort
                            </span>
                          )}
                        </td>
                        <td style={{ padding: '8px 6px' }}>
                          <button aria-label={'Inspect profile '+p.entity_label} onClick={()=>setSelectedEntity(p)}><ChevronRight size={14} color={isSelected ? labColors.cyan : '#64748b'} /></button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Column: Selected Entity Driver & Explainability Inspector */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            {selectedEntity ? (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <h4 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: labColors.text }}>
                        {selectedEntity.entity_label}
                      </h4>
                      <span style={{ fontSize: '0.8rem', color: labColors.muted }}>({selectedEntity.entity_id})</span>
                    </div>
                    <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: labColors.muted }}>
                      Rank #{selectedEntity.rank} · {selectedEntity.anomaly_percentile.toFixed(1)}th Anomaly Percentile · {selectedEntity.total_events} events
                    </p>
                  </div>

                  <button
                    onClick={() => onInspectEntity(selectedEntity.entity_id)}
                    style={{
                      padding: '4px 10px',
                      background: 'rgba(56, 189, 248, 0.15)',
                      border: '1px solid rgba(56, 189, 248, 0.3)',
                      color: labColors.cyan,
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      cursor: 'pointer',
                      fontWeight: 500
                    }}
                  >
                    Inspect in Graph
                  </button>
                </div>

                {/* Primary Behavioral Drivers */}
                <div style={{
                  background: 'rgba(30, 41, 59, 0.5)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: '6px',
                  padding: '12px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 600, color: '#e2e8f0' }}>
                    <BarChart2 size={15} color="#38bdf8" />
                    Top Behavioral Deviation Drivers
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: labColors.secondary, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {selectedEntity.top_drivers.map((d, i) => (
                      <li key={i} style={{ lineHeight: 1.4 }}>{d}</li>
                    ))}
                  </ul>
                </div>

                {/* Feature Vector Table */}
                <div>
                  <h5 style={{ margin: '0 0 8px', fontSize: '0.85rem', color: labColors.muted, fontWeight: 600 }}>
                    5-Feature Multi-Modal Decomposition
                  </h5>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {featureDefs.map(fd => {
                      const dev = selectedEntity.feature_deviations[fd.name];
                      const val = selectedEntity.features[fd.name];
                      const med = cohortStats[fd.name]?.median ?? 0;
                      const isElevated = dev && dev.iqr_deviation > 0.8;
                      return (
                        <div
                          key={fd.name}
                          style={{
                            background: isElevated ? 'rgba(248, 113, 113, 0.08)' : 'rgba(255, 255, 255, 0.03)',
                            border: `1px solid ${isElevated ? 'rgba(248, 113, 113, 0.25)' : 'rgba(255, 255, 255, 0.05)'}`,
                            borderRadius: '6px',
                            padding: '8px 10px',
                            fontSize: '0.8rem'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
                            <span style={{ fontWeight: 600, color: isElevated ? '#fca5a5' : '#f1f5f9' }}>
                              {fd.label}
                            </span>
                            <span style={{ fontWeight: 600, color: isElevated ? labColors.amber : labColors.cyan }}>
                              {val.toFixed(3)} (cohort median: {med.toFixed(3)})
                            </span>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: labColors.muted }}>
                            {fd.description}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Provenance References */}
                <div>
                  <h5 style={{ margin: '0 0 6px', fontSize: '0.85rem', color: labColors.muted, fontWeight: 600 }}>
                    Supporting Source Evidence ({selectedEntity.supporting_evidence_ids.length} records)
                  </h5>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedEntity.supporting_evidence_ids.map(eid => (
                      <button
                        key={eid}
                        onClick={() => onEvidence(eid)}
                        style={{
                          padding: '2px 8px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.12)',
                          borderRadius: '4px',
                          color: '#e2e8f0',
                          fontSize: '0.75rem',
                          cursor: 'pointer'
                        }}
                      >
                        {eid}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <p style={{ color: labColors.muted, fontSize: '0.9rem', textAlign: 'center', margin: 'auto' }}>
                Select an entity from the triage queue to examine its behavioral deviation drivers.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
