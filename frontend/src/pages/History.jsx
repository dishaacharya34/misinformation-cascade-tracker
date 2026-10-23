
import React, { useEffect, useState } from "react";
import { History as HistoryIcon, Database, Clock3, RefreshCw, AlertTriangle, FileText } from "lucide-react";
import { getAnalysisHistory } from "../services/api.js";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const data = await getAnalysisHistory();
      setHistory(data.history || []);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Could not load analysis history."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  function formatDate(value) {
    if (!value) return "Date unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? "Date unavailable"
      : date.toLocaleString();
  }

  return (
    <div className="dashboard-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">PREVIOUS ANALYSES</div>
          <h1>Analysis history<span className="heading-period">.</span></h1>
          <p>Review saved analysis runs and dataset summaries.</p>
        </div>

        <button className="secondary-button" onClick={loadHistory} disabled={loading}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {loading && (
        <section className="panel history-empty">
          <p>Loading saved analyses…</p>
        </section>
      )}

      {error && (
        <section className="panel error-banner" role="alert">
          <AlertTriangle size={20} />
          <div>
            <strong>Could not load history</strong>
            <p>{error}</p>
          </div>
        </section>
      )}

      {!loading && !error && history.length === 0 && (
        <section className="panel history-empty">
          <div className="empty-state-icon">
            <HistoryIcon size={30} />
          </div>
          <h2>No saved analyses yet</h2>
          <p>Upload a CSV and complete an analysis to create a history record.</p>
          <div className="history-requirements">
            <div><Database size={18} /><span>Firestore persistence</span></div>
            <div><Clock3 size={18} /><span>Analysis timestamps</span></div>
          </div>
        </section>
      )}

      {!loading && !error && history.length > 0 && (
        <div className="history-list">
          {history.map((item) => {
            const results = item.results || {};
            const validation = results.validation || {};
            const cascades = results.cascades || {};
            const risk = results.risk || {};

            return (
              <section className="panel history-record" key={item.id}>
                <div className="panel-header">
                  <div>
                    <h3><FileText size={17} /> {item.filename || "Unnamed dataset"}</h3>
                    <p><Clock3 size={14} /> {formatDate(item.created_at)}</p>
                  </div>
                  <span className="result-badge">Saved</span>
                </div>

                <div className="history-metrics">
                  <div>
                    <span>Posts analyzed</span>
                    <strong>{validation.row_count ?? "—"}</strong>
                  </div>
                  <div>
                    <span>Detected cascades</span>
                    <strong>{cascades.available ? cascades.cascade_count : "N/A"}</strong>
                  </div>
                  <div>
                    <span>Priority score</span>
                    <strong>{risk.available ? `${risk.score}/100` : "N/A"}</strong>
                  </div>
                </div>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}
