import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export default function ChartPanel({
  title,
  subtitle,
  data = [],
  dataKey = "count",
  xKey = "date",
}) {
  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <span className="chart-legend">
          <span className="legend-dot" />
          Observed posts
        </span>
      </div>

      {data.length === 0 ? (
        <div className="chart-empty">
          <p>No trend data available yet.</p>
          <span>Upload a CSV with valid timestamps to populate this chart.</span>
        </div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#253047" strokeDasharray="3 3" />
              <XAxis
                dataKey={xKey}
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: "#111b2e",
                  border: "1px solid #334155",
                  borderRadius: 10,
                  color: "#e2e8f0",
                }}
              />
              <Area
                type="monotone"
                dataKey={dataKey}
                stroke="#38bdf8"
                strokeWidth={2}
                fill="url(#trendFill)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
