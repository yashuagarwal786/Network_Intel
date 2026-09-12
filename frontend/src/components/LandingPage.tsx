import {ArrowDown, ArrowRight, Check, Database, FileSearch, Fingerprint, GitBranch, Network, ScanLine, ShieldCheck} from 'lucide-react';
import '../landing.css';

const points = [
  {x:105,y:175,label:'Person A',type:'person'}, {x:260,y:105,label:'Phone record',type:'phone'},
  {x:280,y:300,label:'Account A17',type:'account'}, {x:460,y:225,label:'Account A31',type:'account'},
  {x:605,y:125,label:'Person B',type:'person'}, {x:620,y:330,label:'Location',type:'location'},
  {x:115,y:395,label:'Source report',type:'source'}, {x:460,y:430,label:'Call record',type:'phone'},
];
const edges = [[0,1],[0,2],[0,6],[1,3],[1,4],[2,3],[2,6],[2,7],[3,4],[3,5],[3,7],[4,5],[5,7]];

function EvidenceNetwork() {
  return <div className="lp-network" aria-label="Illustrative evidence network connecting people, phone records, and accounts">
    <div className="lp-network-top"><span><span className="lp-dot"/> CONNECTIONS IN CONTEXT</span><span>ILLUSTRATIVE VIEW</span></div>
    <svg viewBox="0 0 720 500" role="img" aria-label="An evidence path connects Person A through accounts A17 and A31 to Person B">
      <defs><pattern id="lp-grid" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#233445"/></pattern><radialGradient id="lp-glow"><stop stopColor="#0e7490" stopOpacity=".2"/><stop offset="1" stopColor="#0e7490" stopOpacity="0"/></radialGradient></defs>
      <rect width="720" height="500" fill="url(#lp-grid)"/><ellipse cx="360" cy="250" rx="340" ry="240" fill="url(#lp-glow)"/>
      {edges.map(([a,b]) => <line key={`${a}-${b}`} x1={points[a].x} y1={points[a].y} x2={points[b].x} y2={points[b].y} stroke="#294152" strokeWidth="1.2"/>)}
      <path className="lp-evidence-path" d="M105 175 L280 300 L460 225 L605 125" fill="none" stroke="#42d8e9" strokeWidth="2"/>
      {points.map((p,i) => <g key={p.label}>
        {[0,2,3,4].includes(i) && <circle cx={p.x} cy={p.y} r="32" fill="#1ac6df" opacity=".055"/>}
        <circle cx={p.x} cy={p.y} r="20" fill="#0b1a29" stroke={p.type==='person'?'#9ca4ff':p.type==='account'?'#46dcec':'#526b82'} strokeWidth="1.5"/>
        {p.type==='person' ? <g fill="none" stroke="#b3b8ff" strokeWidth="1.5"><circle cx={p.x} cy={p.y-4} r="4"/><path d={`M${p.x-7} ${p.y+7} Q${p.x} ${p.y-2} ${p.x+7} ${p.y+7}`}/></g> : <rect x={p.x-5} y={p.y-6} width="10" height="12" rx="2" fill="none" stroke={p.type==='account'?'#46dcec':'#829bad'} strokeWidth="1.5"/>}
        <text x={p.x} y={p.y+43} textAnchor="middle" fill="#a8b9c9" fontSize="13" fontFamily="inherit">{p.label}</text>
      </g>)}
      <g><rect x="303" y="243" width="136" height="28" rx="5" fill="#10323d" stroke="#245566"/><text x="371" y="262" textAnchor="middle" fill="#80e7f0" fontSize="12">Evidence-linked path</text></g>
    </svg>
    <div className="lp-network-bottom"><span><i/>Source-linked relationships</span><span>Human review required <ShieldCheck size={14}/></span></div>
  </div>;
}

export default function LandingPage() {
  return <div className="lp" id="top">
    <a className="lp-skip" href="#main-content">Skip to content</a>
    <header className="lp-header"><a className="lp-brand" href="#top" aria-label="Network Intel home"><img src="/assets/network-intel-mark.png" alt=""/><span>Network<span className="lp-brand-light"> Intel</span></span></a><nav aria-label="Landing page navigation"><a href="#workflow">Workflow</a><a href="#evidence">Evidence</a><a href="#integrity">Built on trust</a></nav><a className="lp-button lp-button-small" href="#/app">Get started <ArrowRight size={16}/></a></header>
    <main id="main-content">
      <section className="lp-hero">
        <div className="lp-hero-copy"><div className="lp-eyebrow"><span className="lp-dot"/> EVIDENCE-LED NETWORK INTELLIGENCE</div><h1>See the connection.<br/><span>Find the bigger<br className="lp-desktop-break"/> picture.</span></h1><p>Turn scattered records into connected intelligence. Trace relationships, investigate signals, and follow every lead back to its evidence.</p><div className="lp-actions"><a className="lp-button" href="#/app">Get started <ArrowRight size={18}/></a><a className="lp-text-link" href="#workflow">Explore the workflow <ArrowDown size={16}/></a></div><div className="lp-entry-note"><Check size={14}/> No sign-in required <span>·</span> Explore the synthetic demo</div></div>
        <div className="lp-hero-visual"><div className="lp-visual-label"><Network size={15}/> THE SIGNAL IS IN THE CONNECTIONS</div><EvidenceNetwork/><div className="lp-signal"><span className="lp-signal-icon"><ScanLine size={21}/></span><div><span className="lp-meta">FROM CONNECTION TO CONTEXT</span><strong>A path worth investigating.</strong><span>Open the records. Examine the evidence.</span></div><ArrowRight size={19}/></div></div>
      </section>
      <div className="lp-capability-strip"><span>ONE CONNECTED WORKSPACE</span><span><Database size={17}/> Source records</span><span><Fingerprint size={17}/> Entity resolution</span><span><Network size={17}/> Network analysis</span><span><FileSearch size={17}/> Evidence review</span></div>
      <section className="lp-section" id="workflow"><div className="lp-section-heading"><div><div className="lp-eyebrow">01 / THE WORKFLOW</div><h2>From scattered records.<br/><span>To a clearer line of inquiry.</span></h2></div><p>Keep the source, the connection, and the reasoning together at every step.</p></div><div className="lp-steps">{[
        {icon:Database,title:'Bring the evidence together',body:'Work with source records in one case. Inspect extracted entities while keeping their original context within reach.'},
        {icon:GitBranch,title:'Connect what matters',body:'Review potential aliases, explore relationships, and trace paths between people, accounts, and events.'},
        {icon:FileSearch,title:'Follow the lead. Verify the why.',body:'Examine the signals behind each lead, open its supporting evidence, and record your review.'},
      ].map((step,i)=><article key={step.title}><div className="lp-step-top"><step.icon size={23}/><span>0{i+1}</span></div><h3>{step.title}</h3><p>{step.body}</p></article>)}</div></section>
      <section className="lp-section lp-evidence" id="evidence"><div><div className="lp-eyebrow">02 / EVIDENCE, ALWAYS IN REACH</div><h2>A connection is a start.<br/><span>Context makes it useful.</span></h2><p>A network tells you what connects. Network Intel helps you examine why it matters—with source records, temporal signals, and a review trail alongside the graph.</p><ul><li><Check/>Trace relationships back to source evidence</li><li><Check/>Explore the sequence behind a signal</li><li><Check/>Keep investigator decisions in the review trail</li></ul><a className="lp-text-link" href="#/app">Explore the investigation workspace <ArrowRight size={17}/></a></div><div className="lp-evidence-card"><div className="lp-card-heading"><span><FileSearch size={17}/> EVIDENCE CHAIN</span><span className="lp-demo-tag">Synthetic example</span></div><div className="lp-chain"><article><span>01</span><div><small>SOURCE RECORD</small><h3>Account transfer</h3><p>A recorded transaction connects two accounts.</p></div><Database size={18}/></article><article><span>02</span><div><small>ANALYTICAL SIGNAL</small><h3>Activity in context</h3><p>Review the timing and supporting events.</p></div><ScanLine size={18}/></article><article><span>03</span><div><small>HUMAN REVIEW</small><h3>Your judgment. Documented.</h3><p>Assess the lead and record your reasoning.</p></div><ShieldCheck size={18}/></article></div><div className="lp-card-foot"><span className="lp-dot"/> A lead is a starting point, not a conclusion.</div></div></section>
      <section className="lp-section lp-integrity" id="integrity"><div className="lp-integrity-icon"><ShieldCheck size={32}/></div><div><div className="lp-eyebrow">03 / BUILT ON TRUST</div><h2>Intelligence with accountability.</h2><p>Keep observed evidence, analytical inference, and human decisions distinct. Review proposed merges, reverse them when needed, and retain the source context.</p></div><div className="lp-trust-points"><span><Check/> Source-linked evidence</span><span><Check/> Reversible resolution decisions</span><span><Check/> Recorded review history</span></div></section>
      <section className="lp-final"><div className="lp-eyebrow">CONNECT THE RECORDS. KEEP THE CONTEXT.</div><h2>Your next insight starts<br/>with a connection.</h2><p>Step inside Network Intel and explore the evidence.</p><a className="lp-button" href="#/app">Get started <ArrowRight size={18}/></a><span className="lp-entry-note">No account needed. Synthetic demonstration data.</span></section>
    </main>
    <footer className="lp-footer"><a className="lp-brand" href="#top"><img src="/assets/network-intel-mark.png" alt=""/><span>Network Intel</span></a><span>Connected evidence. Considered decisions.</span><a href="#top">Back to top ↑</a></footer>
  </div>;
}
