import React from "react";
import { ShieldCheck, Bell, Search } from "lucide-react";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={23} />
        </div>
        <div>
          <span className="brand-name">Cascade<span className="brand-accent">Watch</span></span>
          <span className="brand-caption">MISINFORMATION INTELLIGENCE</span>
        </div>
      </div>

      <div className="navbar-right">
        <div className="system-status">
          <span className="status-dot" />
          Analysis system
        </div>
        <button className="icon-button" aria-label="Search">
          <Search size={18} />
        </button>
        <button className="icon-button" aria-label="Notifications">
          <Bell size={18} />
        </button>
        <div className="avatar" title="Project workspace">MW</div>
      </div>
    </header>
  );
}
