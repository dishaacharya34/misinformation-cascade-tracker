import React from "react";
import { useState } from "react";
import Navbar from "./components/Navbar.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Analysis from "./pages/Analysis.jsx";
import History from "./pages/History.jsx";

export default function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  function renderPage() {
    switch (activePage) {
      case "Analysis":
        return <Analysis />;
      case "History":
        return <History />;
      case "Dashboard":
      default:
        return <Dashboard />;
    }
  }

  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-layout">
        <Sidebar
          activePage={activePage}
          onNavigate={setActivePage}
        />
        <main className="main-content">{renderPage()}</main>
      </div>
    </div>
  );
}
