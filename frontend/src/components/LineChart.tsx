import { useState, useRef } from "react";

type Series = { label: string; values: number[]; color: string; dash?: string };

export function LineChart({
  angles,
  series,
  title,
  yLabel,
  targetAngle,
  peakAngle,
  onExportCsv,
  onExportJson,
}: {
  angles: number[];
  series: Series[];
  title: string;
  yLabel: string;
  targetAngle?: number;
  peakAngle?: number | null;
  onExportCsv?: () => void;
  onExportJson?: () => void;
}) {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  if (!angles.length || !series.length) return null;

  const width = 840;
  const height = 340;
  const padding = { top: 30, right: 30, bottom: 48, left: 65 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const values = series.flatMap((item) => item.values);
  const xMin = Math.min(...angles);
  const xMax = Math.max(...angles);
  let yMin = Math.min(...values);
  let yMax = Math.max(...values);

  // For dB plots, clamp yMin to at least -45 dB to maintain clean scientific range
  if (yLabel.includes("dB") && yMin < -45) {
    yMin = -45;
  }
  if (yMax <= yMin) yMax = yMin + 1;

  const x = (val: number) =>
    padding.left + ((val - xMin) / (xMax - xMin)) * plotWidth;
  const y = (val: number) => {
    const clamped = Math.max(yMin, Math.min(yMax, val));
    return height - padding.bottom - ((clamped - yMin) / (yMax - yMin)) * plotHeight;
  };

  const points = (vals: number[]) =>
    vals.map((v, i) => `${x(angles[i]).toFixed(1)},${y(v).toFixed(1)}`).join(" ");

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const svgX = (mouseX / rect.width) * width;
    if (svgX < padding.left || svgX > width - padding.right) {
      setHoverIndex(null);
      return;
    }
    const ratio = (svgX - padding.left) / plotWidth;
    const angleVal = xMin + ratio * (xMax - xMin);
    // Find closest index in angles
    let bestIdx = 0;
    let minDiff = Math.abs(angles[0] - angleVal);
    for (let i = 1; i < angles.length; i++) {
      const diff = Math.abs(angles[i] - angleVal);
      if (diff < minDiff) {
        minDiff = diff;
        bestIdx = i;
      }
    }
    setHoverIndex(bestIdx);
  };

  const hoverAngle = hoverIndex !== null ? angles[hoverIndex] : null;
  const hoverX = hoverAngle !== null ? x(hoverAngle) : null;

  // Grid tick ratios
  const yTicks = [0, 0.25, 0.5, 0.75, 1.0].map((ratio) => {
    const yPos = padding.top + ratio * plotHeight;
    const val = yMax - ratio * (yMax - yMin);
    return { yPos, val };
  });

  const xTicks = [-90, -60, -30, 0, 30, 60, 90].filter(
    (t) => t >= xMin && t <= xMax
  );

  return (
    <section className="chart-panel" aria-labelledby="pattern-chart-heading">
      <div className="chart-heading">
        <div>
          <h2 id="pattern-chart-heading">{title}</h2>
          <span>{yLabel} vs observation angle (deg)</span>
        </div>
        <div className="chart-actions">
          {onExportCsv && (
            <button
              type="button"
              className="export-btn"
              onClick={onExportCsv}
              title="Download CSV of simulation data"
            >
              Export CSV
            </button>
          )}
          {onExportJson && (
            <button
              type="button"
              className="export-btn"
              onClick={onExportJson}
              title="Download full JSON response"
            >
              Export JSON
            </button>
          )}
        </div>
      </div>

      <div className="chart-svg-container">
        <svg
          ref={svgRef}
          className="line-chart"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={`${title}. ${yLabel} plotted by angle.`}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoverIndex(null)}
        >
          {/* Horizontal gridlines */}
          {yTicks.map(({ yPos, val }) => (
            <g key={yPos}>
              <line
                x1={padding.left}
                x2={width - padding.right}
                y1={yPos}
                y2={yPos}
                className="grid"
              />
              <text
                x={padding.left - 9}
                y={yPos + 4}
                textAnchor="end"
                className="axis-label"
              >
                {val.toFixed(val > -10 && val < 10 ? 1 : 0)}
              </text>
            </g>
          ))}

          {/* Axes */}
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={height - padding.bottom}
            y2={height - padding.bottom}
            className="axis"
          />
          <line
            x1={padding.left}
            x2={padding.left}
            y1={padding.top}
            y2={height - padding.bottom}
            className="axis"
          />

          {/* Vertical gridlines and X ticks */}
          {xTicks.map((val) => {
            const xPos = x(val);
            return (
              <g key={val}>
                <line
                  x1={xPos}
                  x2={xPos}
                  y1={padding.top}
                  y2={height - padding.bottom}
                  className="grid"
                  strokeDasharray={val === 0 ? undefined : "2 2"}
                />
                <text
                  x={xPos}
                  y={height - 24}
                  textAnchor="middle"
                  className="axis-label"
                >
                  {val}°
                </text>
              </g>
            );
          })}

          {/* Target Angle Marker */}
          {targetAngle !== undefined && targetAngle >= xMin && targetAngle <= xMax && (
            <g>
              <line
                x1={x(targetAngle)}
                x2={x(targetAngle)}
                y1={padding.top}
                y2={height - padding.bottom}
                stroke="#d9534f"
                strokeWidth="1.5"
                strokeDasharray="4 3"
              />
              <text
                x={x(targetAngle)}
                y={padding.top - 8}
                textAnchor="middle"
                fontSize="11"
                fill="#d9534f"
                fontWeight="600"
              >
                Target ({targetAngle}°)
              </text>
            </g>
          )}

          {/* -3 dB Line if applicable */}
          {yLabel.includes("dB") && yMin <= -3 && (
            <g>
              <line
                x1={padding.left}
                x2={width - padding.right}
                y1={y(-3)}
                y2={y(-3)}
                stroke="#f0ad4e"
                strokeWidth="1"
                strokeDasharray="2 3"
              />
              <text
                x={width - padding.right - 4}
                y={y(-3) - 5}
                textAnchor="end"
                fontSize="10"
                fill="#b87309"
              >
                -3 dB (HPBW threshold)
              </text>
            </g>
          )}

          {/* Curves */}
          {series.map((item) => (
            <polyline
              key={item.label}
              points={points(item.values)}
              fill="none"
              stroke={item.color}
              strokeWidth="2.5"
              strokeDasharray={item.dash}
              vectorEffect="non-scaling-stroke"
            >
              <title>{item.label}</title>
            </polyline>
          ))}

          {/* Peak Marker Dot */}
          {peakAngle !== null &&
            peakAngle !== undefined &&
            series[1] &&
            (() => {
              const peakIdx = angles.findIndex((a) => Math.abs(a - peakAngle) < 0.26);
              if (peakIdx >= 0) {
                const px = x(angles[peakIdx]);
                const py = y(series[1].values[peakIdx]);
                return (
                  <circle
                    cx={px}
                    cy={py}
                    r="4.5"
                    fill="#006b7b"
                    stroke="#fff"
                    strokeWidth="1.5"
                  />
                );
              }
              return null;
            })()}

          {/* Interactive Hover Crosshair */}
          {hoverX !== null && hoverIndex !== null && (
            <g>
              <line
                x1={hoverX}
                x2={hoverX}
                y1={padding.top}
                y2={height - padding.bottom}
                stroke="#064b58"
                strokeWidth="1"
                strokeDasharray="3 2"
              />
              {series.map((item) => {
                const py = y(item.values[hoverIndex]);
                return (
                  <circle
                    key={item.label}
                    cx={hoverX}
                    cy={py}
                    r="4"
                    fill={item.color}
                    stroke="#fff"
                    strokeWidth="1"
                  />
                );
              })}
            </g>
          )}
        </svg>

        {/* Hover Tooltip Box */}
        {hoverIndex !== null && hoverAngle !== null && (
          <div className="chart-tooltip">
            <strong>Angle: {hoverAngle.toFixed(1)}°</strong>
            {series.map((item) => (
              <span key={item.label} style={{ color: item.color }}>
                {item.label}: {item.values[hoverIndex].toFixed(2)} dB
              </span>
            ))}
          </div>
        )}
      </div>

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
            Target Angle ({targetAngle}°)
          </span>
        )}
      </div>
    </section>
  );
}
