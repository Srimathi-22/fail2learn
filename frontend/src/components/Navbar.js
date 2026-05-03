import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand" style={{ textDecoration: "none" }}>
        <div className="navbar-logo">F2L</div>
        <div>
          <div className="navbar-title">Fail2Learn</div>
          <div className="navbar-subtitle">Catalyst Discovery Platform</div>
        </div>
      </NavLink>

      <div className="navbar-links">
        {[
          { to: "/",           label: "Search"    },
          { to: "/candidates", label: "Candidates" },
          { to: "/feedback",   label: "Feedback"  },
          { to: "/history",    label: "History"   },
        ].map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
