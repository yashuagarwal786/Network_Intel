import LeadReview from './LeadReview';
import {useEffect,useRef,useState} from 'react';
import type {ComputedLead,EvidenceExplanation} from '../leadTypes';
import type {Entity,PathResult,Selection} from '../demoTypes';
import EvidenceRefs from './EvidenceRefs';
import {api} from '../api';

const time = (s: string) =>
  new Date(s).toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    dateStyle: 'medium',
    timeStyle: 'short',
  }) + ' IST';

const values = (data: Record<string, unknown>) => (
  <dl className="computed-values">
    {Object.entries(data).map(([key, value]) => (
      <div key={key}>
        <dt>{key.replaceAll('_', ' ')}</dt>
        <dd>{typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}</dd>
      </div>
    ))}
  </dl>
);

export default function LeadDetail({
  lead,
  nodes,
  onEvidence,
  onSelect,
  onPath,
  onReviewed,
}: {
  lead: ComputedLead;
  nodes: Entity[];
  onEvidence: (id: string, trail?: string) => void;
  onSelect: (s: Selection) => void;
  onPath: (p: PathResult) => void;
  onReviewed: () => Promise<void>;
}) {
  const review = useRef<HTMLDetailsElement>(null);
  const [explanation, setExplanation] = useState<EvidenceExplanation | null>(null);
  const [explanationError, setExplanationError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    setExplanation(null);
    setExplanationError('');
    api
      .explainLead(lead.lead_id, controller.signal)
      .then(setExplanation)
      .catch(e => {
        if (e.name !== 'AbortError') setExplanationError(e.message);
      });
    return () => controller.abort();
  }, [lead.lead_id]);

  return (
    <>
      <div className="lead-flags">
        <span className="tag amber">{lead.review_priority} · examination order</span>
        <span className="fixture-label">COMPUTED</span>
        <button
          className="review-jump"
          onClick={() => {
            if (review.current) {
              review.current.open = true;
              review.current.scrollIntoView({ block: 'nearest' });
            }
          }}
        >
          Review Lead
        </button>
      </div>
      <h2>{lead.title}</h2>
      <p className="priority-disclaimer">
        Review priority indicates examination order. It is not a probability of criminal activity.
      </p>
      <p className="micro">
        {lead.engine_version} · {lead.review_status}
        <br />
        Generated (replay clock): {time(lead.generated_at)}
      </p>

      {/* 1. STRUCTURED FACTS FIRST: Why flagged */}
      <h3>Why Flagged / Summary</h3>
      <p>{lead.summary}</p>
      <p className="micro">
        Window: {time(lead.time_window.start)} → {time(lead.time_window.end)}
      </p>
      <details className="priority-policy">
        <summary>{lead.signal_categories.length} signal categories · review-priority policy</summary>
        <p className="caution">{lead.priority_explanation}</p>
      </details>

      {/* 2. SUPPORTING EVIDENCE */}
      <h3>Supporting Evidence &amp; Signals ({lead.signals.length})</h3>
      {lead.signals.map(s => (
        <details key={s.signal_id} className="computed-signal">
          <summary>
            {s.title}
            <small>{s.category.replaceAll('_', ' ')} · expand calculation</small>
          </summary>
          <p>{s.calculation}</p>
          <h4>Supporting evidence</h4>
          <EvidenceRefs
            ids={s.supporting_evidence_ids}
            onOpen={id =>
              onEvidence(
                id,
                'Lead ' +
                  lead.lead_id +
                  ' → ' +
                  s.signal_type.replaceAll('_', ' ') +
                  ' → Event → Evidence'
              )
            }
          />
          {s.path && <button onClick={() => onPath(s.path!)}>Show computed signal path</button>}
          <details className="method-details">
            <summary>Method, thresholds and limitations</summary>
            <p className="micro">
              {s.algorithm_version} · {s.signal_id}
            </p>
            <p className="micro">
              Window: {time(s.time_window.start)} → {time(s.time_window.end)}
            </p>
            <h4>Baseline definition</h4>
            <p>{s.baseline_definition}</p>
            <details className="computed-values">
              <summary>Observed values / source counts</summary>
              {values(s.observed_value)}
            </details>
            <h4>Expected values</h4>
            {Object.keys(s.expected_value).length ? (
              values(s.expected_value)
            ) : (
              <p>No historical amount or path expectation assumed.</p>
            )}
            <h4>Policy threshold</h4>
            {values(s.threshold)}
            <h4>Limitations</h4>
            {s.limitations.map(text => (
              <p key={text} className="micro">
                {text}
              </p>
            ))}
          </details>
        </details>
      ))}

      {/* 3. WHO / WHAT WAS INVOLVED */}
      <h3>Who / What Was Involved?</h3>
      <div className="related-entities">
        {lead.involved_entity_ids.map(id => (
          <button key={id} onClick={() => onSelect({ kind: 'entity', id })}>
            {nodes.find(n => n.id === id)?.label || id}
          </button>
        ))}
      </div>

      {/* 4. WHAT REMAINS UNCERTAIN */}
      <h3>What Remains Uncertain?</h3>
      {lead.limitations.map(text => (
        <p className="micro" key={text}>
          {text}
        </p>
      ))}

      {/* 5. NEXT INVESTIGATOR ACTION */}
      <h3>Next Investigator Action</h3>
      <details ref={review} className="review-disclosure">
        <summary>Record investigator review &amp; decision</summary>
        <LeadReview lead={lead} onSaved={onReviewed} />
      </details>

      {/* 6. OPTIONAL GROUNDED AI EXPLANATION */}
      <section className="ai-evidence-explanation" style={{ marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '16px' }}>
        <div className="eyebrow">GROUNDED EVIDENCE EXPLANATION (OPTIONAL AI ASSISTANCE)</div>
        {explanation ? (
          <>
            <div className="explanation-mode">
              <span>
                {explanation.generation_mode === 'GROQ_GROUNDED'
                  ? 'Groq · Grounded & Validated'
                  : 'Deterministic Grounded Fallback (Rules)'}
              </span>
              <small>{explanation.model || explanation.provider}</small>
            </div>
            <h3>Explanation</h3>
            <p>{explanation.explanation}</p>
            <h3>Why flagged?</h3>
            <p>{explanation.why_flagged}</p>
            <h3>Suggested investigator action</h3>
            <p>{explanation.review_suggestion}</p>
            <h3>Supporting evidence citations</h3>
            <EvidenceRefs
              ids={explanation.supporting_evidence_ids}
              onOpen={id => onEvidence(id, 'Grounded explanation → Evidence')}
            />
            <p className="caution">{explanation.caution}</p>
          </>
        ) : explanationError ? (
          <p className="caution">{explanationError}</p>
        ) : (
          <p role="status" className="micro">
            Building explanation from structured facts…
          </p>
        )}
      </section>
    </>
  );
}
