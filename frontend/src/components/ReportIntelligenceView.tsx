import React, { useState, useMemo } from 'react';
import {labColors} from '../designTokens';
import { Sparkles, Cpu, ArrowRight, ExternalLink, Network, FileText, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import type { Mention, Claim, SourceRecord, NerStatus, SourceFile, Manifest } from '../intakeTypes';

interface ReportIntelligenceViewProps {
  files: SourceFile[];
  manifests: Manifest[];
  records: SourceRecord[];
  mentions: Mention[];
  claims: Claim[];
  nerStatus: NerStatus | null;
  onEvidence: (id: string) => void;
  onNetworkWithEntity?: (entityId: string) => void;
  onNavigateResolution: () => void;
  onLoadDemoReport: () => Promise<void>;
  busy: boolean;
}

const KIND_COLORS: Record<string, { bg: string; text: string; border: string }> = Object.fromEntries(Object.entries({Person:labColors.blue,Phone:labColors.cyan,Account:labColors.green,Vehicle:labColors.amber,Organization:labColors.purple,Location:labColors.rose,Money:labColors.secondary,Date:labColors.muted,CaseIdentifier:labColors.secondary,TransactionIdentifier:labColors.secondary}).map(([kind,color])=>[kind,{bg:labColors.elevated,text:color,border:color}]));

export default function ReportIntelligenceView({
  files,
  manifests,
  records,
  mentions,
  claims: _claims,
  nerStatus,
  onEvidence,
  onNetworkWithEntity,
  onNavigateResolution,
  onLoadDemoReport,
  busy,
}: ReportIntelligenceViewProps) {
  const reportManifests = useMemo(() => manifests.filter(m => m.source_type === 'Report'), [manifests]);
  const [selectedFileId, setSelectedFileId] = useState<string>(() => reportManifests[0]?.source_file_id || '');

  // Active report manifest & content
  const activeManifest = reportManifests.find(m => m.source_file_id === selectedFileId) || reportManifests[0];
  const activeFile = files.find(f => f.manifest.source_file_id === activeManifest?.source_file_id);

  // If content is in activeFile use it, else assemble from records for this report
  const rawReportText = useMemo(() => {
    if (activeFile?.content) return activeFile.content;
    const repRecords = records.filter(r => r.source_file_id === activeManifest?.source_file_id);
    if (repRecords.length > 0) {
      return repRecords.map(r => r.raw_excerpt).join('\n');
    }
    return 'No report content available. Load samples or upload an investigation report.';
  }, [activeFile, records, activeManifest]);

  // Mentions for this report
  const reportMentions = useMemo(() => {
    if (!activeManifest) return [];
    return mentions.filter(m => m.source_file_id === activeManifest.source_file_id);
  }, [mentions, activeManifest]);

  // Filter for the entity table
  const [extractorFilter, setExtractorFilter] = useState<'ALL' | 'ML' | 'REGEX'>('ALL');
  const [kindFilter, setKindFilter] = useState<string>('ALL');
  const [searchFilter, setSearchFilter] = useState<string>('');

  const filteredMentions = useMemo(() => {
    return reportMentions.filter(m => {
      const isMl = m.extraction_method === 'spacy-ner';
      if (extractorFilter === 'ML' && !isMl) return false;
      if (extractorFilter === 'REGEX' && isMl) return false;
      if (kindFilter !== 'ALL' && m.kind !== kindFilter) return false;
      if (searchFilter && !m.raw_value.toLowerCase().includes(searchFilter.toLowerCase())) return false;
      return true;
    });
  }, [reportMentions, extractorFilter, kindFilter, searchFilter]);

  // Highlight text with non-overlapping matches
  const highlightedLines = useMemo(() => {
    const lines = rawReportText.split('\n');
    if (reportMentions.length === 0) return lines.map((l, i) => <div key={i} className="report-line">{l || '\u00A0'}</div>);

    // Sort entities by length descending to match longest spans first
    const sortedTargets = [...reportMentions].sort((a, b) => b.raw_value.length - a.raw_value.length);

    return lines.map((line, lineIdx) => {
      if (!line.trim()) return <div key={lineIdx} className="report-line">&nbsp;</div>;

      // Find all matches on this line
      const intervals: { start: number; end: number; mention: Mention }[] = [];
      for (const m of sortedTargets) {
        const needle = m.raw_value;
        if (!needle) continue;
        let pos = 0;
        while ((pos = line.indexOf(needle, pos)) !== -1) {
          const start = pos;
          const end = pos + needle.length;
          // Check collision with already found intervals
          const collides = intervals.some(inv => (start >= inv.start && start < inv.end) || (end > inv.start && end <= inv.end));
          if (!collides) {
            intervals.push({ start, end, mention: m });
          }
          pos += needle.length;
        }
      }

      intervals.sort((a, b) => a.start - b.start);

      if (intervals.length === 0) {
        return <div key={lineIdx} className="report-line">{line}</div>;
      }

      const elements: React.ReactNode[] = [];
      let lastIdx = 0;
      intervals.forEach((inv, invIdx) => {
        if (inv.start > lastIdx) {
          elements.push(line.slice(lastIdx, inv.start));
        }
        const colors = KIND_COLORS[inv.mention.kind] || { bg: '#1f242d', text: '#e2e8f0', border: '#334155' };
        const isMl = inv.mention.extraction_method === 'spacy-ner';

        elements.push(
          <mark
            key={invIdx}
            className="ner-highlight-span"
            tabIndex={0} role="button" onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onEvidence(inv.mention.evidence_id)}}}
            style={{
              backgroundColor: colors.bg,
              color: colors.text,
              borderBottom: `2px solid ${colors.border}`,
              padding: '2px 5px',
              borderRadius: '3px',
              margin: '0 2px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
            title={`${inv.mention.kind} [${isMl ? 'ML / spaCy NER' : 'Deterministic Regex'}] • ${inv.mention.normalized_value}`}
            onClick={() => onEvidence(inv.mention.evidence_id)}
          >
            <span>{line.slice(inv.start, inv.end)}</span>
            <span
              style={{
                fontSize: '9px',
                opacity: 0.85,
                background: colors.border,
                color: '#ffffff',
                padding: '0 4px',
                borderRadius: '2px',
                textTransform: 'uppercase',
                fontWeight: 600,
                letterSpacing: '0.4px',
              }}
            >
              {inv.mention.kind}
            </span>
          </mark>
        );
        lastIdx = inv.end;
      });

      if (lastIdx < line.length) {
        elements.push(line.slice(lastIdx));
      }

      return <div key={lineIdx} className="report-line">{elements}</div>;
    });
  }, [rawReportText, reportMentions, onEvidence]);

  const mlCount = useMemo(() => reportMentions.filter(m => m.extraction_method === 'spacy-ner').length, [reportMentions]);
  const regexCount = useMemo(() => reportMentions.filter(m => m.extraction_method !== 'spacy-ner').length, [reportMentions]);

  return (
    <div className="report-intelligence-view">
      {/* 1. Intelligence Pipeline Visualization Banner */}
      <div className="pipeline-banner" role="region" aria-label="Investigation Intelligence Pipeline">
        <div className="pipeline-heading">
          <Layers size={15} />
          <strong>NETWORK INTEL PIPELINE</strong>
          <span className="pipeline-sub">End-to-End Evidence &amp; Graph Provenance</span>
        </div>
        <div className="pipeline-steps">
          <div className="pipeline-step active">
            <span className="step-num">1</span>
            <span className="step-label">Raw Report</span>
            <span className="step-tech">UTF-8 Prose</span>
          </div>
          <ArrowRight size={14} className="pipeline-arrow" />
          <div className="pipeline-step active highlight-ml">
            <span className="step-num">2</span>
            <span className="step-label">ML Entity Extraction</span>
            <span className="step-tech">spaCy en_core_web_sm</span>
          </div>
          <ArrowRight size={14} className="pipeline-arrow" />
          <div className="pipeline-step" onClick={onNavigateResolution} tabIndex={0} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onNavigateResolution()}}} role="button" title="Open Entity Resolution Review">
            <span className="step-num">3</span>
            <span className="step-label">Entity Resolution</span>
            <span className="step-tech">Pairwise Review</span>
          </div>
          <ArrowRight size={14} className="pipeline-arrow" />
          <div className="pipeline-step" onClick={() => onNetworkWithEntity?.('')} tabIndex={0} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onNetworkWithEntity?.('')}}} role="button" title="Open Knowledge Graph">
            <span className="step-num">4</span>
            <span className="step-label">Knowledge Graph</span>
            <span className="step-tech">Association Network</span>
          </div>
          <ArrowRight size={14} className="pipeline-arrow" />
          <div className="pipeline-step">
            <span className="step-num">5</span>
            <span className="step-label">Anomaly Signals</span>
            <span className="step-tech">Burst &amp; Flow Analysis</span>
          </div>
          <ArrowRight size={14} className="pipeline-arrow" />
          <div className="pipeline-step">
            <span className="step-num">6</span>
            <span className="step-label">Investigative Lead</span>
            <span className="step-tech">Multi-Category Review</span>
          </div>
        </div>
      </div>

      {/* 2. Controls & Model Status Header */}
      <div className="ner-control-bar">
        <div className="ner-status-pill">
          {nerStatus?.available ? (
            <span className="ner-status-badge active" title="spaCy 3.8 model is loaded in backend memory">
              <CheckCircle2 size={13} />
              <strong>NER Model: {nerStatus.model}</strong>
              <span className="pill-dot" /> Active (Pretrained ML)
            </span>
          ) : (
            <span className="ner-status-badge unavailable" title="Using deterministic fallback rules">
              <AlertTriangle size={13} />
              <strong>NER Model unavailable</strong> • Structured regex only
            </span>
          )}
        </div>

        <div className="report-selector">
          <label htmlFor="report-select"><FileText size={13} /> Document:</label>
          <select
            id="report-select"
            value={activeManifest?.source_file_id || ''}
            onChange={e => setSelectedFileId(e.target.value)}
          >
            {reportManifests.map(m => (
              <option key={m.source_file_id} value={m.source_file_id}>
                {m.filename} ({m.record_count} lines)
              </option>
            ))}
          </select>
        </div>

        <div className="demo-report-action">
          <button
            className="demo-report-btn primary"
            onClick={onLoadDemoReport}
            disabled={busy}
            title="Uploads and extracts a realistic intelligence report containing unseen names (Vikram Singh, Arjun Mehta, Kavya Rao, Meridian Logistics) through the live backend NER model"
          >
            <Sparkles size={14} />
            <span>Load additional synthetic report</span>
          </button>
        </div>
      </div>

      {/* 3. Main Split View: Source Document (Left) + Extracted Entities Panel (Right) */}
      <div className="report-inspection-grid">
        {/* Left Column: Raw Document View with Highlighting */}
        <div className="report-source-card">
          <div className="card-header">
            <div className="header-title">
              <FileText size={15} />
              <h3>Source Report Text</h3>
              <span className="header-tag">{activeManifest?.filename || 'report.txt'}</span>
            </div>
            <div className="header-legend">
              <span className="legend-chip person"><span className="swatch" /> PERSON</span>
              <span className="legend-chip org"><span className="swatch" /> ORG</span>
              <span className="legend-chip loc"><span className="swatch" /> LOCATION</span>
              <span className="legend-chip regex"><span className="swatch" /> REGEX (PHONE/VEHICLE/MONEY)</span>
            </div>
          </div>
          <div className="report-content-body">
            {highlightedLines}
          </div>
          <div className="card-footer">
            <span className="evidence-provenance">
              SHA-256: <code>{activeManifest?.checksum?.slice(0, 16)}...</code> • Source-record evidence available for each extracted mention
            </span>
          </div>
        </div>

        {/* Right Column: Structured Extracted Entity Table */}
        <div className="report-entities-card">
          <div className="card-header">
            <div className="header-title">
              <Cpu size={15} />
              <h3>Extracted Entities &amp; Graph Transition</h3>
              <span className="badge-count">{reportMentions.length} total</span>
            </div>
            <div className="filter-pills">
              <button
                className={`filter-btn ${extractorFilter === 'ALL' ? 'active' : ''}`}
                onClick={() => setExtractorFilter('ALL')}
              >
                All ({reportMentions.length})
              </button>
              <button
                className={`filter-btn ml-btn ${extractorFilter === 'ML' ? 'active' : ''}`}
                onClick={() => setExtractorFilter('ML')}
              >
                <Sparkles size={11} /> ML / NLP ({mlCount})
              </button>
              <button
                className={`filter-btn regex-btn ${extractorFilter === 'REGEX' ? 'active' : ''}`}
                onClick={() => setExtractorFilter('REGEX')}
              >
                Regex ({regexCount})
              </button>
            </div>
          </div>

          <div className="table-search-bar">
            <input
              type="text"
              placeholder="Search extracted entities..."
              value={searchFilter}
              onChange={e => setSearchFilter(e.target.value)}
              className="entity-search-input"
            />
            <select
              value={kindFilter}
              onChange={e => setKindFilter(e.target.value)}
              className="entity-kind-select"
            >
              <option value="ALL">All Entity Types</option>
              <option value="Person">Person</option>
              <option value="Organization">Organization</option>
              <option value="Location">Location</option>
              <option value="Phone">Phone</option>
              <option value="Account">Account</option>
              <option value="Vehicle">Vehicle</option>
              <option value="Money">Money</option>
              <option value="Date">Date</option>
            </select>
          </div>

          <div className="entity-table-container">
            <table className="entity-table">
              <thead>
                <tr>
                  <th>Entity</th>
                  <th>Type</th>
                  <th>Extraction Pipeline</th>
                  <th>Graph Transition</th>
                  <th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {filteredMentions.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="empty-cell">
                      No matching entities found in this view.
                    </td>
                  </tr>
                ) : (
                  filteredMentions.map(m => {
                    const isMl = m.extraction_method === 'spacy-ner';
                    const colors = KIND_COLORS[m.kind] || { bg: '#1c2630', text: '#cbd5e1', border: '#475569' };
                    return (
                      <tr key={m.mention_id} className={isMl ? 'row-ml' : 'row-regex'}>
                        <td className="cell-entity">
                          <strong>{m.raw_value}</strong>
                          {m.normalized_value !== m.raw_value && (
                            <small className="cell-normalized">norm: {m.normalized_value}</small>
                          )}
                        </td>
                        <td>
                          <span
                            className="kind-badge"
                            style={{
                              backgroundColor: colors.bg,
                              color: colors.text,
                              borderColor: colors.border,
                            }}
                          >
                            {m.kind}
                          </span>
                        </td>
                        <td>
                          {isMl ? (
                            <div className="extractor-info ml">
                              <span className="badge-ml">
                                <Sparkles size={11} /> Pretrained spaCy NER
                              </span>
                                <small>{m.extraction_method} · {m.span_start != null ? `characters ${m.span_start}–${m.span_end}` : 'span unavailable'}</small>
                            </div>
                          ) : (
                            <div className="extractor-info regex">
                              <span className="badge-regex">
                                <Cpu size={11} /> Rule-based extraction
                              </span>
                              <small>{m.extraction_method} · {m.field || `characters ${m.span_start}–${m.span_end}`}</small>
                            </div>
                          )}
                        </td>
                        <td>
                          {m.entity_id ? (
                            <div className="graph-node-link">
                              <button
                                className="node-pill"
                                onClick={() => onNetworkWithEntity?.(m.entity_id!)}
                                title={`Node ID: ${m.entity_id}. Click to view in case network graph.`}
                              >
                                <Network size={11} />
                                <span>{m.normalized_value}</span>
                                <small className="node-id">{m.entity_id.slice(0, 10)}...</small>
                              </button>
                            </div>
                          ) : (
                            <span className="unmapped-node">Value Mention (Literal)</span>
                          )}
                        </td>
                        <td>
                          <button
                            className="evidence-btn"
                            onClick={() => onEvidence(m.evidence_id)}
                            title={`Open evidence record ${m.evidence_id} with exact span`}
                          >
                            <ExternalLink size={11} />
                            <span>{m.evidence_id}</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          <div className="card-footer table-footer">
            <span>
              <strong>Methodology Disclosure:</strong> Entity extractions from free text are tagged with exact character offsets.
              Outputs pass to Entity Resolution before final identity consolidation. No uncalibrated probability numbers are fabricated.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
