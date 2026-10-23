import React from "react";
import { useState } from "react";
import {
  Activity,
  FileText,
  Network,
  GitBranch,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";

import MetricCard from "../components/MetricCard.jsx";
import FileUploader from "../components/FileUploader.jsx";
import ChartPanel from "../components/ChartPanel.jsx";
import { analyzeCsv } from "../services/api.js";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);
  const [datasetName, setDatasetName] = useState("");

  async function handleAnalyze(file) {
    setLoading(true);
    setError("");
    setResults(null);
    setDatasetName(file.name);

    try {
      const data = await analyzeCsv(file);

      if (data.success === false) {
        throw new Error(data.error || "Analysis could not be completed.");
      }

      setResults(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Could not connect to the analysis API. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  const validation = results?.validation;
  const cascades = results?.cascades;
  const trends = results?.trends;
  const risk = results?.risk;

  const metricCards = [
    {
      title: "Posts analyzed",
      value: validation?.row_count ?? "—",
      description: "Rows in uploaded dataset",
      icon: FileText,
      accent: "blue",
    },
    {
      title: "Detected cascades",
      value: cascades?.available ? cascades.cascade_count : "N/A",
      description: cascades?.available
        ? "Observed connected components"
        : "Post and parent IDs required",
      icon: Network,
      accent: "teal",
    },
    {
      title: "Largest cascade",
      value: cascades?.available
        ? cascades.cascades?.[0]?.size ?? 0
        : "N/A",
      description: "Posts in largest observed cascade",
      icon: GitBranch,
      accent: "violet",
    },
    {
      title: "Priority score",
      value: risk?.available ? `${risk.score}/100` : "N/A",
      description: risk?.level
        ? `${risk.level} propagation priority`
        : "Awaiting analysis",
      icon: Activity,
      accent: "orange",
    },
  ];

  return (
    <div className="dashboard-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            <span className="status-dot" />
            MISINFORMATION INTELLIGENCE
          </div>
          <h1>Overview<span className="heading-period">.</span></h1>
          <p>
            Explore propagation patterns, content labels, and emerging trends
            from social media and news datasets.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => window.location.reload()}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <FileUploader onAnalyze={handleAnalyze} loading={loading} />

      {error && (
        <div className="error-banner" role="alert">
          <AlertTriangle size={20} />
          <div>
            <strong>Analysis failed</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      <div className="section-heading">
        <div>
          <h2>Dataset overview</h2>
          <p>
            {results
              ? `Results for ${datasetName}`
              : "Upload a dataset to populate these metrics."}
          </p>
        </div>
        {results && <span className="result-badge">Analysis complete</span>}
      </div>

      <div className="metrics-grid">
        {metricCards.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      <div className="dashboard-grid">
        <ChartPanel
          title="Posting activity"
          subtitle="Observed posts over time"
          data={trends?.available ? trends.daily_posts : []}
          xKey="date"
          dataKey="count"
        />

        <section className="panel risk-panel">
          <div className="panel-header">
            <div>
              <h3>Propagation priority</h3>
              <p>Preliminary evidence-based signals</p>
            </div>
            <Activity size={20} />
          </div>

          {risk?.available ? (
            <>
              <div className="risk-score">
                <strong>{risk.score}</strong>
                <span>/ 100</span>
              </div>
              <span className={`risk-level ${risk.level}`}>
                {risk.level} priority
              </span>
              <ul className="signal-list">
                {risk.signals.map((signal, index) => (
                  <li key={`${signal}-${index}`}>{signal}</li>
                ))}
              </ul>
              <p className="disclaimer">{risk.interpretation}</p>
            </>
          ) : (
            <div className="chart-empty">
              <p>No risk assessment yet.</p>
              <span>Upload a CSV to calculate available propagation signals.</span>
            </div>
          )}
        </section>
      </div>

      {results && (
        <section className="panel details-panel">
          <div className="panel-header">
            <div>
              <h3>Analysis details</h3>
              <p>Detected fields and data quality information</p>
            </div>
          </div>

          <div className="detail-row">
            <span>Detected columns</span>
            <strong>{Object.keys(results.columns || {}).length}</strong>
          </div>

          <div className="column-tags">
            {Object.entries(results.columns || {}).map(([field, column]) => (
              <span className="column-tag" key={field}>
                {field}: {column}
              </span>
            ))}
          </div>

          {(results.missing_fields || []).length > 0 && (
            <p className="muted-note">
              Unavailable fields: {results.missing_fields.join(", ")}
            </p>
          )}

          {(validation?.warnings || []).map((warning, index) => (
            <p className="warning-note" key={index}>
              {warning}
            </p>
          ))}

          {results.classification && (
            <div className="classification-note">
              <strong>Content labels</strong>
              <p>
                {results.classification.available
                  ? results.classification.note
                  : results.classification.reason}
              </p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
