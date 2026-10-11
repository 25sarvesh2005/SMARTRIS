import { useState } from "react";

type Series = { label: string; values: number[]; color: string; dash?: string };

export function PolarChart({
  angles,
  series,
  targetAngle,
  title = "Polar Radiation Pattern",
}: {
  angles: number[];
  series: Series[];
  targetAngle?: number;
  title?: string;
}) {
  const [hoveredAngle, setHoveredAngle] = useState<number | null>(null);

  if (!angles.length || !series.length) return null;

  const width = 540;
  const height = 380;
  const cx = width / 2;
  const cy = height - 40; // Semi-circular/hemispherical top plot centered at bottom
  const maxRadius = 280;
  const minDb = -40;
  const maxDb = 0;

  // Map dB to radius: 0 dB -> maxRadius, -40 dB -> 0
  const dbToRadius = (db: number) => {
    const clamped = Math.max(minDb, Math.min(maxDb, db));
    return ((clamped - minDb) / (maxDb - minDb)) * maxRadius;
  };

  // Convert (angle in deg, radius) to SVG (x, y) where 0 deg is UP (12 o'clock)
  const polarToCartesian = (angleDeg: number, radius: number) => {
    const rad = (angleDeg * Math.PI) / 180;
    return {
      x: cx + radius * Math.sin(rad),
      y: cy - radius * Math.cos(rad),
    };
  };

  const ringDbs = [-40, -30, -20, -10, 0];
  const spokeAngles = [-90, -60, -45, -30, 0, 30, 45, 60, 90];

  const seriesPaths = series.map((item) => {
    const points = item.values.map((val, idx) => {
      const ang = angles[idx];
      const r = dbToRadius(val);
      const pt = polarToCartesian(ang, r);
      return `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`;
    });
    return {
      label: item.label,
      color: item.color,
      dash: item.dash,
      d: `M ${points.join(" L ")}`,
      points,
    };
  });

  return (
    <section className="chart-panel polar-panel" aria-labelledby="polar-chart-heading">
      <div className="chart-heading">
        <h2 id="polar-chart-heading">{title}</h2>
        <span>Semi-circular 180° pattern (normalized dB)</span>
      </div>

      <svg
        className="polar-chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={`${title}. Polar beam pattern from -90° to +90°.`}
        onMouseLeave={() => setHoveredAngle(null)}
      >
        <defs>
          <radialGradient id="polar-fill" cx="50%" cy="100%" r="100%">
            <stop offset="0%" stopColor="#006b7b" stopOpacity="0.22" />
            <stop offset="100%" stopColor="#006b7b" stopOpacity="0.02" />
          </radialGradient>
        </defs>

        {/* Concentric dB arcs */}
        {ringDbs.map((db) => {
          const r = dbToRadius(db);
          if (r <= 0) return null;
          const left = polarToCartesian(-90, r);
          const right = polarToCartesian(90, r);
          return (
            <g key={db}>
              <path
                d={`M ${left.x} ${left.y} A ${r} ${r} 0 0 1 ${right.x} ${right.y}`}
                fill="none"
                stroke="#e2e8ea"
                strokeWidth="1"
              />
              <text
                x={cx + 6}
                y={cy - r + 11}
                className="polar-db-label"
                textAnchor="start"
                fontSize="10"
                fill="#7e8c95"
              >
                {db} dB
              </text>
            </g>
          );
        })}

        {/* Radial spokes */}
        {spokeAngles.map((ang) => {
          const pt = polarToCartesian(ang, maxRadius);
          const textPt = polarToCartesian(ang, maxRadius + 18);
          return (
            <g key={ang}>
              <line
                x1={cx}
                y1={cy}
                x2={pt.x}
                y2={pt.y}
                stroke={ang === 0 ? "#b0bec5" : "#e4eaec"}
                strokeWidth={ang === 0 ? "1.5" : "1"}
                strokeDasharray={ang === 0 ? undefined : "3 3"}
              />
              <text
                x={textPt.x}
                y={textPt.y + (ang === 0 ? -4 : 4)}
                textAnchor="middle"
                fontSize="11"
                fill={ang === 0 ? "#075c69" : "#687781"}
                fontWeight={ang === 0 ? "bold" : "normal"}
              >
                {ang === 0 ? "0°" : `${ang > 0 ? `+${ang}` : ang}°`}
              </text>
            </g>
          );
        })}

        {/* Target Angle Radial Line */}
        {targetAngle !== undefined && (
          (() => {
            const pt = polarToCartesian(targetAngle, maxRadius);
            return (
              <g>
                <line
                  x1={cx}
                  y1={cy}
                  x2={pt.x}
                  y2={pt.y}
                  stroke="#d9534f"
                  strokeWidth="2"
                  strokeDasharray="4 3"
                />
                <circle cx={pt.x} cy={pt.y} r="3" fill="#d9534f" />
              </g>
            );
          })()
        )}

        {/* Plotted Series */}
        {seriesPaths.map((item, idx) => (
          <g key={item.label}>
            {idx === 1 && (
              <path
                d={`${item.d} L ${cx} ${cy} Z`}
                fill="url(#polar-fill)"
                stroke="none"
              />
            )}
            <path
              d={item.d}
              fill="none"
              stroke={item.color}
              strokeWidth="2.4"
              strokeDasharray={item.dash}
              strokeLinejoin="round"
            />
          </g>
        ))}

        {/* Center origin dot */}
        <circle cx={cx} cy={cy} r="3.5" fill="#52606c" />
      </svg>

      <div className="legend">
        {series.map((item) => (
          <span key={item.label}>
            <i style={{ backgroundColor: item.color }} />
            {item.label}
          </span>
        ))}
        {targetAngle !== undefined && (
          <span>
            <i style={{ backgroundColor: "#d9534f" }} />
            Target vector ({targetAngle}°)
          </span>
        )}
      </div>
    </section>
  );
}
