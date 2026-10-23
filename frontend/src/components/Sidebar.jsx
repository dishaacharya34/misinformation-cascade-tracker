import React from "react";
import {
  LayoutDashboard,
  FileSearch,
  History,
  Network,
  Settings,
  CircleHelp,
} from "lucide-react";

const navigation = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Analysis", icon: FileSearch },
  { label: "History", icon: History },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-section-label">WORKSPACE</div>

      <nav className="sidebar-nav">
        {navigation.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className={`nav-item ${activePage === label ? "active" : ""}`}
            onClick={() => onNavigate(label)}
          >
            <Icon size={19} />
            <span>{label}</span>
            {label === "Analysis" && <span className="nav-indicator" />}
          </button>
        ))}
      </nav>

      <div className="sidebar-divider" />

      <div className="sidebar-section-label">INTELLIGENCE</div>
      <div className="sidebar-static-item">
        <Network size={19} />
        <span>Cascade Network</span>
        <span className="coming-soon">SOON</span>
      </div>

      <div className="sidebar-spacer" />

      <div className="sidebar-bottom">
        <button className="nav-item" onClick={() => onNavigate("Settings")}>
          <Settings size={19} />
          <span>Settings</span>
        </button>
        <button className="nav-item" onClick={() => onNavigate("Help")}>
          <CircleHelp size={19} />
          <span>Help & Support</span>
        </button>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Project workspace</span>
          <span className="version">v1.0</span>
        </div>
      </div>
    </aside>
  );
}
