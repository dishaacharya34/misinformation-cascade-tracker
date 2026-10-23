import React from "react";
import { FileSearch, Network, Clock3, Users } from "lucide-react";

export default function Analysis() {
  const sections = [
    {
      icon: FileSearch,
      title: "Content classification",
      description:
        "Review dataset-provided labels. Automated misinformation predictions require a suitable, validated classification model.",
    },
    {
      icon: Network,
      title: "Cascade propagation",
      description:
        "Examine parent-child post relationships, cascade sizes, and propagation depth when identifiers are available.",
    },
    {
      icon: Clock3,
      title: "Temporal trends",
      description:
        "Explore posting frequency using valid timestamps in the uploaded dataset.",
    },
    {
      icon: Users,
      title: "Influence analysis",
      description:
        "Explore observed cross-user propagation when author and parent-post information are available.",
    },
  ];

  return (
    <div className="dashboard-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">ANALYTICS WORKSPACE</div>
          <h1>Analysis<span className="heading-period">.</span></h1>
          <p>
            Understand the methods used to analyze misinformation propagation
            and identify which evidence your dataset supports.
          </p>
        </div>
      </div>

      <div className="analysis-method-grid">
        {sections.map(({ icon: Icon, title, description }) => (
          <section className="panel method-card" key={title}>
            <div className="method-icon">
              <Icon size={22} />
            </div>
            <h3>{title}</h3>
            <p>{description}</p>
          </section>
        ))}
      </div>

      <section className="panel methodology-panel">
        <h2>Analysis methodology</h2>
        <p>
          Each uploaded CSV is inspected for recognizable columns and checked
          for data-quality issues. The pipeline runs only the analyses
          supported by the available fields.
        </p>
        <ol>
          <li>CSV ingestion and validation</li>
          <li>Automatic column detection</li>
          <li>Available cascade, influence, and temporal analysis</li>
          <li>Evidence-based propagation-priority scoring</li>
          <li>Results with explicit limitations</li>
        </ol>
        <p className="disclaimer">
          A propagation-priority score does not establish whether a claim is
          true or false.
        </p>
      </section>
    </div>
  );
}
