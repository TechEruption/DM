import { NavLink, Link, useLocation } from "react-router-dom";
import { BarChart3, Upload, X } from "lucide-react";
import { useState, type ReactNode } from "react";
import { useDataset } from "../../context/DatasetContext";

const links = [
  { to: "/dashboard", label: "Overview" },
  { to: "/attribution", label: "Attribution" },
  { to: "/journeys", label: "Journeys" },
  { to: "/campaigns", label: "Campaigns" },
  { to: "/channels", label: "Channels" },
  { to: "/funnel", label: "Funnel" },
  { to: "/budget", label: "Budget" },
  { to: "/scenarios", label: "Scenarios" },
  { to: "/insights", label: "Insights" },
  { to: "/methodology", label: "Methodology" },
];

export default function AppLayout({ children }: { children: ReactNode }) {
  const { dataset } = useDataset();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const isLanding = location.pathname === "/";
  return (
    <div className="app-frame">
      <header className="site-header">
        <div className="site-header-inner">
          <Link className="brand" to="/" aria-label="MARKETALLOC home">
            <span className="brand-mark"><BarChart3 size={18} strokeWidth={2.4} /></span>
            <span className="brand-copy"><strong>MARKETALLOC</strong><small>Marketing intelligence</small></span>
          </Link>
          {!isLanding && (
            <button className="mobile-menu-toggle" aria-label={menuOpen ? "Close navigation" : "Open navigation"} onClick={() => setMenuOpen((open) => !open)}>
              {menuOpen ? <X size={19} /> : <span className="menu-lines">☰</span>}
            </button>
          )}
          <nav className={`site-nav ${menuOpen ? "is-open" : ""}`} aria-label="Main navigation">
            {!isLanding && links.map((item) => (
              <NavLink key={item.to} to={item.to} onClick={() => setMenuOpen(false)} className={({ isActive }) => isActive ? "site-nav-link active" : "site-nav-link"}>
                {item.label}
              </NavLink>
            ))}
            {isLanding && <Link className="site-nav-link" to="/methodology">Methodology</Link>}
            <Link className={dataset ? "button button-outline nav-upload" : "button button-accent nav-upload"} to="/upload" onClick={() => setMenuOpen(false)}>
              <Upload size={14} /> {dataset ? "Change data" : "Upload data"}
            </Link>
          </nav>
        </div>
      </header>
      <div className={isLanding ? "page-content landing-content" : "page-content"}>{children}</div>
      <footer className="site-footer">
        <span>MARKETALLOC · Marketing attribution, made clear.</span>
        <span>Developed by Soumabha Mahapatra</span>
      </footer>
    </div>
  );
}
