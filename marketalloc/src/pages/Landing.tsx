import { ArrowRight, Compass, GitBranch, LineChart, Target, Wallet } from "lucide-react";
import { Link } from "react-router-dom";

const capabilities = [
  { icon: Target, title: "Marketing attribution", text: "Compare five attribution models and understand how channels share conversion credit." },
  { icon: LineChart, title: "Campaign analytics", text: "Review spend, reach, conversion efficiency and return across campaigns." },
  { icon: GitBranch, title: "Customer journeys", text: "Follow touchpoints from first interaction to conversion." },
  { icon: Wallet, title: "Budget planning", text: "Explore channel allocations with constraints and diminishing returns." },
];

export default function Landing() {
  return (
    <main className="landing">
      <section className="landing-hero">
        <div className="hero-copy">
          <span className="hero-kicker"><span className="status-dot" /> MARKETING DECISION SUPPORT</span>
          <h1>Make every marketing decision <em>count.</em></h1>
          <p>A marketing intelligence platform for understanding customer journeys, measuring channel contribution and making better budget allocation decisions.</p>
          <div className="hero-actions">
            <Link className="button button-accent button-large" to="/upload">Upload marketing data <ArrowRight size={16} /></Link>
            <Link className="button button-outline button-large" to="/methodology">Explore the methodology</Link>
          </div>
          <div className="hero-note"><Compass size={14} /> Your data is analyzed locally in your browser and is not stored.</div>
        </div>
        <div className="hero-visual" aria-label="Illustration of the marketing analytics workflow">
          <div className="visual-topline"><span>MARKETING PERFORMANCE WORKSPACE</span><span>YOUR DATA</span></div>
          <h2 className="visual-title">Connect the customer journey</h2>
          <div className="journey-diagram">
            <div className="diagram-lane"><span>CHANNELS</span><i>Search</i><i>Email</i><i>Social</i></div>
            <div className="diagram-connector"><span /><span /><span /></div>
            <div className="diagram-node"><GitBranch size={18} /><strong>Customer journey</strong><small>Ordered touchpoints</small></div>
            <div className="diagram-connector single"><span /></div>
            <div className="diagram-outcomes"><span><LineChart size={15} /> Attribution</span><span><Target size={15} /> Performance</span><span><Wallet size={15} /> Planning</span></div>
          </div>
          <p className="visual-caption">A joined-up view—from first interaction to the next budget decision.</p>
        </div>
      </section>
      <section className="capability-section">
        <div className="section-heading">
          <p className="eyebrow">A BETTER VIEW OF THE WHOLE PICTURE</p>
          <h2>From customer touchpoints to confident planning.</h2>
          <p>Bring your campaign, customer and conversion data together to see what is working and where to focus next.</p>
        </div>
        <div className="capability-grid">
          {capabilities.map(({ icon: Icon, title, text }) => (
            <article className="capability-card" key={title}><span className="capability-icon"><Icon size={18} /></span><h3>{title}</h3><p>{text}</p></article>
          ))}
        </div>
      </section>
      <section className="landing-cta">
        <div><p className="eyebrow">START WITH YOUR DATA</p><h2>Your marketing data. A clearer next move.</h2><p>Upload four CSV files to explore attribution, performance and budget planning.</p></div>
        <Link className="button button-accent button-large" to="/upload">Get started <ArrowRight size={16} /></Link>
      </section>
    </main>
  );
}
