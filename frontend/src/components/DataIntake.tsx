import { useEffect, useState } from 'react';
import { api } from '../api';
import type { ProcessingSummary, SourceRecord, Mention, Claim, NerStatus, SourceFile } from '../intakeTypes';
import ReportIntelligenceView from './ReportIntelligenceView';
import BehavioralAnomalyView from './BehavioralAnomalyView';
import { Sparkles, Activity } from 'lucide-react';

export default function DataIntake({
  onEvidence,
  onRefresh,
  onNetwork,
  onResolution,
  onEntity,
}: {
  onEvidence: (id: string) => void;
  onRefresh: () => Promise<void>;
  onNetwork: () => void;
  onResolution: () => void;
  onEntity: (id:string) => void;
}) {
  const [summary, setSummary] = useState<ProcessingSummary | null>(null);
  const [records, setRecords] = useState<SourceRecord[]>([]);
  const [mentions, setMentions] = useState<Mention[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [sourceFiles, setSourceFiles] = useState<SourceFile[]>([]);
  const [nerStatus, setNerStatus] = useState<NerStatus | null>(null);

  const [tab, setTab] = useState<'NER & Reports' | 'Behavioral Anomaly' | 'Sources' | 'Records' | 'Mentions' | 'Claims'>('Sources');
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [record, setRecord] = useState<SourceRecord | null>(null);

  async function load() {
    const [s, r, c, sf, ns] = await Promise.all([
      api.processing(),
      api.records(),
      api.claims(),
      api.sourceFiles().catch(() => []),
      api.nerStatus().catch(() => ({
        available: false,
        model: 'en_core_web_sm',
        extractor_version: 'spacy-en_core_web_sm-unavailable',
        status_text: 'NER Model unavailable • Structured extraction only',
      })),
    ]);
    setSummary(s);
    setRecords(r.records);
    setMentions(c.mentions);
    setClaims(c.claims);
    setSourceFiles(sf);
    setNerStatus(ns);
  }

  useEffect(() => {
    load().catch(e => setError(e.message));
  }, []);

  async function work(action: () => Promise<unknown>) {
    setBusy(true);
    setError('');
    try {
      await action();
      setRecord(null);
      await load();
      await onRefresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function upload() {
    if (!files.length) return;
    for (const file of files) {
      if (file.size > 65536) throw new Error(`${file.name} exceeds the 64 KiB limit.`);
      const lower=file.name.toLowerCase();
      const kind=lower.endsWith('.txt')?'Report':lower.includes('cdr')?'CDR':lower.includes('transaction')?'Transaction':lower.includes('vehicle')?'Vehicle':'';
      if(!kind)throw new Error(`Could not infer source type for ${file.name}. Use report.txt or a CSV filename containing cdr, transaction, or vehicle.`);
      await api.upload(file.name, kind, new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer()));
    }
    setFiles([]);
  }

  async function openRecord(id: string) {
    try {
      setRecord(await api.record(id));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function handleLoadDemoReport() {
    await work(async () => {
      await api.loadDemoReport();
    });
  }

  const source = (id: string) => summary?.manifests.find(m => m.source_file_id === id)?.filename || id;
  const label = (id: string | null) => (id ? mentions.find(m => m.entity_id === id)?.normalized_value || id : 'No supported relation');

  return (
    <section className="records-panel intake-panel">
      <div className="section-top">
        <div>
          <h2>Data Sources</h2>
          <p className="muted">Four controlled source types · exact rows and report spans</p>
        </div>
      </div>

      <details className="intake-setup">
        <summary>Upload source documents or reload demo batches</summary>
        <div className="intake-controls">
          <button disabled={busy} onClick={() => work(() => api.resetIntake(true))}>
            Load fallback evidence pack
          </button>
          <button
            disabled={busy || !summary?.manifests.length}
            className="primary"
            onClick={() => work(() => api.process())}
          >
            {busy ? 'Processing…' : 'Process sources'}
          </button>
        </div>
        <p className="micro">
          Replaces this case's source files with a clearly labelled synthetic fallback pack. Uploaded files remain the recommended judge flow.
        </p>
        <div className="intake-upload">
          <input
            aria-label="Synthetic source files"
            type="file"
            accept=".txt,.csv"
            multiple
            onChange={e => setFiles(Array.from(e.target.files||[]))}
          />
          <button disabled={busy || !files.length} onClick={() => work(upload)}>
            {files.length?`Validate ${files.length} file${files.length>1?'s':''}`:'Select source files'}
          </button>
        </div>
      </details>

      {error && (
        <p className="caution" role="alert">
          {error}
        </p>
      )}

      {!summary && !error && <p role="status">Loading processed sources…</p>}

      {summary && (
        <>
          <div className="intake-stats" role="status">
            <span>
              <strong>{summary.records_processed}</strong>records
            </span>
            <span>
              <strong>{summary.entity_mentions}</strong>mentions
            </span>
            <span>
              <strong>{summary.relationship_candidates}</strong>candidates
            </span>
            <span>
              <strong>{summary.rejected_records}</strong>invalid
            </span>
            <span>
              <strong>{summary.withheld_claims}</strong>withheld
            </span>
          </div>

          {summary.needs_reprocess && (
            <div className="caution-banner" role="alert" style={{ margin: '12px 0', padding: '12px 16px', background: 'rgba(234, 179, 8, 0.12)', border: '1px solid rgba(234, 179, 8, 0.4)', borderRadius: '6px' }}>
              <p style={{ margin: 0, fontWeight: 600, color: '#facc15' }}>Reprocess Required</p>
              <p className="micro" style={{ margin: '4px 0 10px 0', color: '#cbd5e1' }}>
                {summary.reprocess_reason || 'Source records or character spans require updating to current parser specifications.'}
              </p>
              <button disabled={busy} className="primary" onClick={() => work(() => api.process())}>
                {busy ? 'Reprocessing…' : 'Reprocess sources now'}
              </button>
            </div>
          )}

          <div className="processing-flow">Uploaded <span>→</span> Validated <span>→</span> Parsed <span>→</span> Extracted <span>→</span> Added for Review <small>{summary.processed?'Completed · invalid rows excluded':'Awaiting processing'}</small></div><div className="intake-tabs">
            {(['Sources', 'Records', 'Mentions', 'Claims', 'NER & Reports', 'Behavioral Anomaly'] as const).map(t => (
              <button
                aria-pressed={tab === t}
                key={t}
                onClick={() => {
                  setTab(t);
                  setRecord(null);
                }}
                className={t === 'NER & Reports' ? 'tab-ner-highlight' : t === 'Behavioral Anomaly' ? 'tab-anomaly-highlight' : ''}
              >
                {t === 'NER & Reports' ? (
                  <>
                    <Sparkles size={13} /> Report extraction
                  </>
                ) : t === 'Behavioral Anomaly' ? (
                  <>
                    <Activity size={13} /> Behavioral profiles
                  </>
                ) : (
                  t
                )}
              </button>
            ))}
          </div>

          <div className={'intake-results' + (tab === 'Sources' && !record ? ' source-grid' : '')}>
            {record ? (
              <article>
                <button onClick={() => setRecord(null)}>Back to results</button>
                <h3>
                  {record.filename} · {record.row ? `Row ${record.row}` : record.span_start != null ? `Characters ${record.span_start}–${record.span_end}` : 'Span unavailable'}
                </h3>
                <p className="micro">
                  {record.record_id} · {record.parser_version} · {record.verification_status}
                </p>
                <pre>{record.raw_excerpt}</pre>
                <h4>Normalized fields</h4>
                <pre>{JSON.stringify(record.normalized_fields, null, 2)}</pre>
                {record.validation_errors.map(e => (
                  <p className="caution" key={e}>
                    {e}
                  </p>
                ))}
                <button onClick={() => onEvidence('E-' + record.record_id)}>Open record evidence</button>
              </article>
            ) : tab === 'NER & Reports' ? (
              <ReportIntelligenceView
                files={sourceFiles}
                manifests={summary.manifests}
                records={records}
                mentions={mentions}
                claims={claims}
                nerStatus={nerStatus}
                onEvidence={onEvidence}
                onNetworkWithEntity={id=>id?onEntity(id):onNetwork()}
                onNavigateResolution={onResolution}
                onLoadDemoReport={handleLoadDemoReport}
                busy={busy}
              />
            ) : tab === 'Behavioral Anomaly' ? (
              <BehavioralAnomalyView
                onEvidence={onEvidence}
                onInspectEntity={onEntity}
              />
            ) : tab === 'Sources' ? (
              summary.manifests.length ? (
                summary.manifests.map(m => (
                  <article key={m.source_file_id}>
                    <div className="source-kind">
                      {{
                        Report: 'Investigation Report',
                        CDR: 'CDR Records',
                        Transaction: 'Bank Transactions',
                        Vehicle: 'Vehicle Records',
                      }[m.source_type] || m.source_type}
                    </div>
                    <strong>{m.filename}</strong>
                    <span
                      className={
                        'tag' +
                        (m.processing_status.includes('ERROR') || m.processing_status === 'INVALID' ? ' amber' : '')
                      }
                    >
                      {m.processing_status.replaceAll('_', ' ')}
                    </span>
                    <p className="micro">
                      {m.source_type} · {m.record_count} records · {m.parser_version}
                    </p>
                    <p className="micro">
                      {new Set(mentions.filter(n => n.source_file_id === m.source_file_id).map(n => n.entity_id).filter(Boolean)).size} extracted entity IDs ·{' '}
                      {claims.filter(c => c.source_file_id === m.source_file_id && c.disposition === 'GRAPH_CANDIDATE').length} candidates
                    </p>
                    {m.source_type === 'Report' && (
                      <button
                        className="inspect-ner-btn"
                        onClick={() => setTab('NER & Reports')}
                        style={{ marginTop: '6px', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                      >
                        <Sparkles size={12} /> Inspect NER Extraction &amp; Spans
                      </button>
                    )}
                    <details style={{ marginTop: '8px' }}>
                      <summary>Source manifest / SHA-256</summary>
                      <p className="micro intake-hash">
                        {m.source_file_id}
                        <br />
                        {m.checksum}
                        <br />
                        Uploaded {m.uploaded_at}
                      </p>
                    </details>
                    {m.validation_errors.length > 0 && (
                      <details className="validation-details">
                        <summary>{m.validation_errors.length} rejected row · inspect validation</summary>
                        {m.validation_errors.map(e => (
                          <p className="caution" key={e}>
                            {e}
                          </p>
                        ))}
                      </details>
                    )}
                  </article>
                ))
              ) : (
                <p>No sources loaded. Upload this case's CSV/TXT evidence files to begin.</p>
              )
            ) : tab === 'Records' ? (
              records.map(r => (
                <article key={r.record_id}>
                  <button onClick={() => openRecord(r.record_id)}>
                    {r.filename} · {r.row ? `Row ${r.row}` : r.span_start != null ? `Characters ${r.span_start}–${r.span_end}` : 'Span unavailable'}
                  </button>
                  <span className="tag">{r.status}</span>
                  <p>{r.raw_excerpt}</p>
                  {r.validation_errors.map(e => (
                    <p className="caution" key={e}>
                      {e}
                    </p>
                  ))}
                </article>
              ))
            ) : tab === 'Mentions' ? (
              mentions.map(m => (
                  <article key={m.mention_id}>
                    <strong>{m.raw_value}</strong>
                    <span className="tag">{m.kind} · UNVERIFIED</span>
                    <span className={m.extraction_method.includes('spacy') ? 'tag amber' : 'tag'} style={{ marginLeft: '6px' }}>
                      {m.extraction_method === 'spacy-ner' ? 'spaCy Statistical NER' :
                       m.extraction_method === 'spacy-entity-ruler' ? 'spaCy EntityRuler' :
                       m.extraction_method === 'deterministic-csv-field' ? 'Deterministic CSV Field' :
                       m.extraction_method === 'deterministic-regex' ? 'Deterministic Regex' :
                       m.extraction_method}
                    </span>
                    <p className="micro">
                      Normalized: {m.normalized_value} · {source(m.source_file_id)} · {m.field || (m.span_start != null ? `characters ${m.span_start}–${m.span_end}` : 'Span unavailable')} · {m.extraction_method}
                    </p>
                    {m.entity_id && (
                      <p className="micro" style={{ color: '#7ee0d6' }}>
                        Graph Node: {m.entity_id}
                      </p>
                    )}
                    <button onClick={() => openRecord(m.record_id)}>Source record</button>
                    <button onClick={() => onEvidence(m.evidence_id)}>Evidence</button>
                  </article>
                ))
            ) : (
              claims.map(c => (
                <article key={c.claim_id}>
                  <strong>{c.relationship_type}</strong>
                  <span className="tag">{c.disposition}</span>
                  <p>
                    {label(c.subject_id)} → {label(c.object_id)}
                  </p>
                  <p className="micro">
                    {c.polarity} · {c.uncertainty} · UNVERIFIED · {source(c.source_file_id)} · {c.extraction_method} · {c.span_start != null ? `characters ${c.span_start}–${c.span_end}` : 'Span unavailable'}
                  </p>
                  <p>{c.explanation}</p>
                  <button onClick={() => openRecord(c.record_id)}>Source record</button>
                  <button onClick={() => onEvidence(c.evidence_ids[0])}>Evidence</button>
                </article>
              ))
            )}
          </div>

          <div className="intake-controls">
            <button disabled={busy || !summary.processed} onClick={onNetwork}>
              View in graph
            </button>
            <button disabled={busy} onClick={onResolution}>
              Continue to resolution review
            </button>
          </div>
        </>
      )}
    </section>
  );
}
