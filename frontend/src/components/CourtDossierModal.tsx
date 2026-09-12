import { Printer, X, FileText, AlertCircle, HelpCircle } from 'lucide-react';
import type { CaseResponse, Entity, Relationship, Lead, Source, PathResult } from '../demoTypes';

interface Props {
  caseData: CaseResponse;
  nodes: Entity[];
  relationships: Relationship[];
  path: PathResult | null;
  leads: Lead[];
  sources: Source[];
  onClose: () => void;
}

export default function CourtDossierModal({
  caseData,
  nodes,
  relationships,
  path,
  leads,
  sources,
  onClose,
}: Props) {
  const c = caseData.case;
  const displayCaseId = c.id.replace(/^VEIL-/, 'NI-');
  const nowIst = new Date().toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    dateStyle: 'full',
    timeStyle: 'medium',
  }) + ' IST';

  const label = (id: string) => nodes.find(n => n.id === id)?.label || id;
  const verifiedEntities = nodes.filter(n => n.verification_status === 'VERIFIED');
  const verifiedRelationships = relationships.filter(r => r.verification_status === 'VERIFIED');
  const activeLead = leads[0] || null;

  // Aggregate supporting evidence IDs from path, active lead, and verified items
  const citedEvidenceIds = Array.from(new Set([
    ...(path?.evidence_ids || []),
    ...(activeLead?.evidence_ids || []),
    ...verifiedEntities.flatMap(n => n.evidence_ids),
    ...verifiedRelationships.flatMap(r => r.evidence_ids)
  ])).filter(Boolean);

  return (
    <div className="dossier-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(6px)',
      zIndex: 9999,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '24px',
      overflowY: 'auto'
    }}>
      <div className="dossier-window" style={{
        backgroundColor: '#0F131A',
        color: '#E5E7EB',
        width: '100%',
        maxWidth: '920px',
        maxHeight: '92vh',
        borderRadius: '8px',
        border: '1px solid #374151',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Modal Top Action Bar (hidden on print) */}
        <div className="no-print" style={{
          padding: '12px 20px',
          backgroundColor: '#161C26',
          borderBottom: '1px solid #283344',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="#38BDF8" />
            <strong style={{ fontSize: '14px', letterSpacing: '0.04em' }}>
              INVESTIGATION ANALYSIS DRAFT · WORKING INTELLIGENCE BRIEF
            </strong>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => window.print()}
              aria-label="Print or save draft as PDF"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '13px'
              }}
            >
              <Printer size={15} /> Print / Save as PDF
            </button>
            <button
              onClick={onClose}
              aria-label="Close investigation analysis draft modal"
              title="Close modal"
              style={{
                background: 'none',
                border: '1px solid #4B5563',
                color: '#9CA3AF',
                borderRadius: '4px',
                padding: '4px 8px',
                cursor: 'pointer'
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Printable Document Container */}
        <div className="dossier-printable" style={{
          padding: '40px',
          overflowY: 'auto',
          lineHeight: '1.6',
          fontSize: '13px'
        }}>
          {/* Header Banner */}
          <div style={{ textAlign: 'center', borderBottom: '2px solid #374151', paddingBottom: '18px', marginBottom: '24px' }}>
            <div style={{ fontSize: '11px', letterSpacing: '0.15em', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase' }}>
              Investigation Analysis &amp; Correlation System
            </div>
            <h1 style={{ fontSize: '20px', margin: '6px 0', color: '#F9FAFB', fontWeight: 800, letterSpacing: '0.05em' }}>
              Investigation Analysis Draft
            </h1>
            <div style={{ fontSize: '12px', color: '#94A3B8' }}>
              Internal investigative briefing generated from recorded source assertions and graph intelligence. Not a legal certification or judicial proof.
            </div>
          </div>

          {/* Case Metadata Table */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', padding: '12px', backgroundColor: '#161C26', borderRadius: '6px', marginBottom: '24px', border: '1px solid #283344' }}>
            <div>
              <small style={{ color: '#9CA3AF', display: 'block', fontSize: '10px' }}>CASE IDENTIFIER</small>
              <strong style={{ color: '#F3F4F6' }}>{displayCaseId}</strong>
            </div>
            <div>
              <small style={{ color: '#9CA3AF', display: 'block', fontSize: '10px' }}>INVESTIGATION TITLE</small>
              <strong style={{ color: '#F3F4F6' }}>{c.name}</strong>
            </div>
            <div>
              <small style={{ color: '#9CA3AF', display: 'block', fontSize: '10px' }}>REVIEW STATUS</small>
              <span style={{ color: '#F59E0B', fontWeight: 600 }}>{c.status}</span>
            </div>
            <div>
              <small style={{ color: '#9CA3AF', display: 'block', fontSize: '10px' }}>GENERATED TIMESTAMP</small>
              <span style={{ color: '#D1D5DB' }}>{nowIst}</span>
            </div>
          </div>

          {/* Section 1: Source Assertions */}
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '15px', color: '#38BDF8', borderBottom: '1px solid #374151', paddingBottom: '4px', marginBottom: '10px' }}>
              1. SOURCE ASSERTIONS
            </h2>
            <p style={{ margin: '0 0 8px 0', color: '#D1D5DB' }}>
              The following data sources have been ingested into this workspace. All entries represent unverified source assertions extracted from supplied files:
            </p>
            {sources.length > 0 ? (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left', marginBottom: '12px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#1E2430', color: '#9CA3AF', borderBottom: '1px solid #374151' }}>
                    <th style={{ padding: '6px' }}>Source File</th>
                    <th style={{ padding: '6px' }}>Category</th>
                    <th style={{ padding: '6px' }}>Captured Records</th>
                    <th style={{ padding: '6px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sources.map(s => (
                    <tr key={s.id} style={{ borderBottom: '1px solid #1F2937' }}>
                      <td style={{ padding: '6px', fontFamily: 'monospace', color: '#F3F4F6' }}>{s.filename}</td>
                      <td style={{ padding: '6px', color: '#9CA3AF' }}>{s.type}</td>
                      <td style={{ padding: '6px', color: '#9CA3AF' }}>{s.evidence_ids.length} records</td>
                      <td style={{ padding: '6px', color: '#94A3B8' }}>source record states assertions</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ color: '#9CA3AF', fontStyle: 'italic' }}>Not established from available records.</p>
            )}
          </section>

          {/* Section 2: Investigator-Verified Facts */}
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '15px', color: '#38BDF8', borderBottom: '1px solid #374151', paddingBottom: '4px', marginBottom: '10px' }}>
              2. INVESTIGATOR-VERIFIED FACTS
            </h2>
            {verifiedEntities.length > 0 || verifiedRelationships.length > 0 ? (
              <div>
                <p style={{ margin: '0 0 8px 0', color: '#D1D5DB' }}>
                  The following items have been explicitly confirmed and verified by human investigator review:
                </p>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#10B981' }}>
                  {verifiedEntities.map(e => (
                    <li key={e.id}>
                      Entity <strong>{e.label}</strong> ({e.type}) — Verified (Evidence: {e.evidence_ids.join(', ') || 'N/A'})
                    </li>
                  ))}
                  {verifiedRelationships.map(r => (
                    <li key={r.id}>
                      Relationship <strong>{label(r.source)} → {label(r.target)}</strong> ({r.type.replaceAll('_', ' ')}) — Verified (Evidence: {r.evidence_ids.join(', ') || 'N/A'})
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div style={{ padding: '10px 14px', backgroundColor: '#1E2430', borderRadius: '4px', borderLeft: '4px solid #9CA3AF' }}>
                <p style={{ margin: 0, color: '#9CA3AF' }}>
                  Not established from available records. No assertions have been marked as verified facts. All records currently remain unverified source assertions requiring human verification.
                </p>
              </div>
            )}
          </section>

          {/* Section 3: Algorithmic Findings */}
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '15px', color: '#38BDF8', borderBottom: '1px solid #374151', paddingBottom: '4px', marginBottom: '10px' }}>
              3. ALGORITHMIC FINDINGS
            </h2>
            {path ? (
              <>
                <p style={{ margin: '0 0 8px 0', color: '#D1D5DB' }}>
                  The graph traversal algorithm identified an association corridor connecting <strong>{label(path.node_ids[0])}</strong> to <strong>{label(path.node_ids[path.node_ids.length - 1])}</strong> across {path.path_length} steps:
                </p>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left', marginBottom: '10px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#1E2430', color: '#9CA3AF', borderBottom: '1px solid #374151' }}>
                      <th style={{ padding: '8px' }}>Step</th>
                      <th style={{ padding: '8px' }}>From</th>
                      <th style={{ padding: '8px' }}>Association Type</th>
                      <th style={{ padding: '8px' }}>To</th>
                      <th style={{ padding: '8px' }}>Evidence Reference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {path.steps.map((step, idx) => {
                      const rel = path.relationships.find(r => r.id === step.relationship_id);
                      return (
                        <tr key={idx} style={{ borderBottom: '1px solid #1F2937' }}>
                          <td style={{ padding: '8px', color: '#38BDF8', fontWeight: 700 }}>#{idx + 1}</td>
                          <td style={{ padding: '8px', color: '#F3F4F6' }}>{label(step.from_id)}</td>
                          <td style={{ padding: '8px', color: '#F59E0B' }}>
                            {rel?.type.replaceAll('_', ' ')} {step.traversal === 'reverse' ? '(reverse traversal)' : ''}
                          </td>
                          <td style={{ padding: '8px', color: '#F3F4F6' }}>{label(step.to_id)}</td>
                          <td style={{ padding: '8px', fontFamily: 'monospace', color: '#10B981' }}>
                            {step.evidence_ids.join(', ') || 'N/A'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <p style={{ fontSize: '11px', color: '#9CA3AF', margin: '4px 0 0 0', fontStyle: 'italic' }}>
                  Note: This is an algorithmically computed association. It highlights a potential structural corridor for examination and requires human verification.
                </p>
              </>
            ) : (
              <p style={{ color: '#9CA3AF' }}>Not established from available records. No active association corridor has been computed.</p>
            )}
          </section>

          {/* Section 4: Investigative Leads */}
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '15px', color: '#38BDF8', borderBottom: '1px solid #374151', paddingBottom: '4px', marginBottom: '10px' }}>
              4. INVESTIGATIVE LEADS
            </h2>
            {leads.length > 0 ? (
              leads.map(leadItem => (
                <div key={leadItem.lead_id} style={{ marginBottom: '16px', backgroundColor: '#161C26', padding: '14px', borderRadius: '6px', border: '1px solid #283344' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <strong style={{ fontSize: '13px', color: '#F3F4F6' }}>
                      Lead {leadItem.lead_id}: {leadItem.title}
                    </strong>
                    <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', backgroundColor: '#374151', color: '#F59E0B', fontWeight: 600 }}>
                      Priority: {leadItem.review_priority}
                    </span>
                  </div>
                  <p style={{ margin: '0 0 8px 0', color: '#D1D5DB' }}>{leadItem.summary}</p>
                  <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '8px' }}>
                    <strong>Signals Observed:</strong>
                    <ul style={{ margin: '4px 0 0 0', paddingLeft: '18px' }}>
                      {leadItem.signals.map(sig => (
                        <li key={sig.signal_id} style={{ marginBottom: '3px' }}>
                          <span style={{ color: '#E5E7EB' }}>{sig.title}</span> — {sig.calculation} (Evidence: {sig.supporting_evidence_ids.join(', ') || 'N/A'})
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div style={{ fontSize: '11px', color: '#94A3B8' }}>
                    Current review status: <strong>{leadItem.review_status}</strong> · investigative lead generated for examination order.
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: '#9CA3AF' }}>Not established from available records. No computed investigative leads in workspace.</p>
            )}
          </section>

          {/* Section 5: Supporting Evidence */}
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '15px', color: '#38BDF8', borderBottom: '1px solid #374151', paddingBottom: '4px', marginBottom: '10px' }}>
              5. SUPPORTING EVIDENCE CITATIONS
            </h2>
            <p style={{ margin: '0 0 8px 0', color: '#D1D5DB' }}>
              Evidence citations linked to the active findings and corridor ({citedEvidenceIds.length} references recorded):
            </p>
            {citedEvidenceIds.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', margin: '8px 0' }}>
                {citedEvidenceIds.map(eid => (
                  <span key={eid} style={{ fontFamily: 'monospace', fontSize: '11px', padding: '3px 8px', backgroundColor: '#1E2430', borderRadius: '4px', border: '1px solid #374151', color: '#38BDF8' }}>
                    {eid}
                  </span>
                ))}
              </div>
            ) : (
              <p style={{ color: '#9CA3AF' }}>Not established from available records.</p>
            )}
          </section>

          {/* Section 6: Limitations and Missing Context */}
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '15px', color: '#F59E0B', borderBottom: '1px solid #374151', paddingBottom: '4px', marginBottom: '10px' }}>
              6. LIMITATIONS AND MISSING CONTEXT
            </h2>
            <div style={{ backgroundColor: '#1A1813', border: '1px solid #78350F', borderRadius: '6px', padding: '12px', fontSize: '12px', color: '#FDE68A' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', fontWeight: 700 }}>
                <AlertCircle size={15} color="#F59E0B" /> Critical Investigative Caveats
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px', lineHeight: '1.5' }}>
                <li>Source records reflect raw observations and assertions; phone subscribers may differ from actual device operators.</li>
                <li>Temporal proximity or sequential transactions do not establish criminal intent, common control, or coordinated action.</li>
                <li>Incomplete coverage: analysis is bounded strictly by the ingested demonstration datasets; unobserved external channels may exist.</li>
                {activeLead?.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          </section>

          {/* Section 7: Investigator Decisions */}
          <section style={{
            marginTop: '28px',
            padding: '16px',
            backgroundColor: '#131822',
            border: '1px solid #283344',
            borderRadius: '6px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <HelpCircle size={18} color="#38BDF8" />
              <strong style={{ fontSize: '13px', color: '#93C5FD', letterSpacing: '0.04em' }}>
                7. INVESTIGATOR DECISION &amp; REVIEW REGISTER
              </strong>
            </div>
            <p style={{ fontSize: '11px', color: '#9CA3AF', margin: '0 0 16px 0', textAlign: 'justify' }}>
              This draft is prepared as an analytical aid to assist human decision-making. No algorithmic finding or candidate link constitutes verified evidence or a determination of responsibility without independent factual corroboration.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', paddingTop: '14px', borderTop: '1px dashed #374151', fontSize: '11px' }}>
              <div>
                <span style={{ color: '#6B7280', display: 'block' }}>REVIEWING ANALYST:</span>
                <span style={{ color: '#E5E7EB', display: 'block', marginTop: '20px', borderBottom: '1px solid #4B5563' }}></span>
              </div>
              <div>
                <span style={{ color: '#6B7280', display: 'block' }}>DATE OF EXAMINATION:</span>
                <span style={{ color: '#E5E7EB', display: 'block', marginTop: '20px', borderBottom: '1px solid #4B5563' }}></span>
              </div>
              <div>
                <span style={{ color: '#6B7280', display: 'block' }}>ACTION TAKEN:</span>
                <strong style={{ color: '#F59E0B', display: 'block', marginTop: '4px' }}>REQUIRES HUMAN VERIFICATION</strong>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
