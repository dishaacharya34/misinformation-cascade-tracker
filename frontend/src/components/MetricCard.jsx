import React from "react";
import { ArrowUpRight } from "lucide-react";

export default function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  accent = "blue",
}) {
  return (
    <article className={`metric-card accent-${accent}`}>
      <div className="metric-card-top">
        <span className="metric-title">{title}</span>
        <div className="metric-icon">
          {Icon && <Icon size={19} />}
        </div>
      </div>

      <div className="metric-value">{value}</div>

      <div className="metric-description">
        <ArrowUpRight size={14} />
        <span>{description}</span>
      </div>
    </article>
  );
}
