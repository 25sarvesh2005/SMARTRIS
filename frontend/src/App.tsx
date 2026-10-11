import { useEffect, useState } from "react";
import { getHealth, runBeamSteering, runTradeoff } from "./api";
import { LineChart } from "./components/LineChart";
import { PolarChart } from "./components/PolarChart";
import { Metrics } from "./components/Metrics";
import { PhaseTable } from "./components/PhaseTable";
import type { BeamSteeringRequest, BeamSteeringResult, TradeoffRequest, TradeoffResult } from "./types";

type Page = "overview" | "beam" | "tradeoff" | "theory";

const defaultBeam: BeamSteeringRequest = {
  element_count: 8,
  frequency_hz: 3e9,
  spacing_m: 0.05,
  target_angle_deg: 25,
  reflection_magnitude: 1,
  angle_start_deg: -90,
  angle_stop_deg: 90,
  sample_count: 361,
  incident_angle_deg: 0,
  element_pattern: "isotropic",
  phase_quantization_bits: null,
  coupled_loss_model: false,
};

const { target_angle_deg: unusedTargetAngle, ...arrayDefaults } = defaultBeam;
void unusedTargetAngle;

const defaultTradeoff: TradeoffRequest = {
  ...arrayDefaults,
  receiver_angle_deg: 25,
  observation_angle_deg: -20,
  penalty: 0.5,
  max_evaluations: 1000,
};

const format = (value: number | null, digits = 3) =>
  value === null ? "Unavailable" : value.toFixed(digits);

function NumericField({
  label,
  value,
  onChange,
  min,
  max,
  step,
  unit,
  note,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number | "any";
  unit: string;
  note?: string;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <label className="numeric-field" htmlFor={id}>
      <span>
        {label}
        <small>{unit}</small>
      </span>
      <input
        id={id}
        type="number"
        value={value}
        min={min}
        max={max}
        step={step ?? "any"}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      {note && <em>{note}</em>}
    </label>
  );
}

function BeamPage() {
  const [form, setForm] = useState<BeamSteeringRequest>(defaultBeam);
  const [result, setResult] = useState<BeamSteeringResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [chartMode, setChartMode] = useState<"db" | "polar" | "linear">("db");

  const update = <K extends keyof BeamSteeringRequest>(key: K, value: BeamSteeringRequest[K]) =>
    setForm((current) => ({ ...current, [key]: value }));

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await runBeamSteering(form));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The simulation could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  const exportCsv = () => {
    if (!result) return;
    const header = "angle_deg,baseline_power_db,controlled_power_db,baseline_linear,controlled_linear\n";
    const rows = result.angles_deg
      .map(
        (ang, i) =>
          `${ang.toFixed(2)},${result.baseline_normalized_power_db[i].toFixed(4)},${result.controlled_normalized_power_db[i].toFixed(4)},${result.baseline_normalized_power[i].toFixed(6)},${result.controlled_normalized_power[i].toFixed(6)}`
      )
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `smartris_beam_${form.target_angle_deg}deg.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `smartris_beam_${form.target_angle_deg}deg.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="page beam-page">
      <header className="page-header">
        <p className="eyebrow">Primary workflow</p>
        <h1>Beam steering &amp; Radiation Analysis</h1>
        <p>
          Simulate an idealized or physically extended Reconfigurable Intelligent Surface (RIS) array.
          Compare baseline reflection against phase-controlled steering with polar radiation patterns and research metrics.
        </p>
      </header>
      <div className="workspace">
        <form className="controls" onSubmit={submit}>
          <h2>Array configuration</h2>
          <NumericField
            label="Element count"
            unit="elements"
            value={form.element_count}
            min={2}
            max={128}
            step={1}
            onChange={(value) => update("element_count", value)}
          />
          <NumericField
            label="Operating frequency"
            unit="GHz"
            value={form.frequency_hz / 1e9}
            min={0.001}
            max={100}
            step="any"
            onChange={(value) => update("frequency_hz", value * 1e9)}
            note="Decimal GHz values are converted to Hz automatically for the simulation."
          />
          <NumericField
            label="Element spacing"
            unit="m"
            value={form.spacing_m}
            min={0.0001}
            max={10}
            step="any"
            onChange={(value) => update("spacing_m", value)}
          />
          <NumericField
            label="Target angle"
            unit="degrees"
            value={form.target_angle_deg}
            min={-90}
            max={90}
            step="any"
            onChange={(value) => update("target_angle_deg", value)}
          />
          <NumericField
            label="Reflection magnitude (|Γ|)"
            unit="0–1"
            value={form.reflection_magnitude}
            min={0}
            max={1}
            step="any"
            onChange={(value) => update("reflection_magnitude", value)}
            note="Field reflection coefficient magnitude |Γ| where Pref/Pinc = |Γ|² (1.0 = total reflection)."
          />
          <NumericField
            label="Angular samples"
            unit="samples"
            value={form.sample_count}
            min={181}
            max={1441}
            step={10}
            onChange={(value) => update("sample_count", value)}
          />

          <details className="advanced-details">
            <summary>🔬 Research Parameters (Optional)</summary>
            <div className="advanced-panel">
              <NumericField
                label="Incident wave angle"
                unit="degrees"
                value={form.incident_angle_deg ?? 0}
                min={-90}
                max={90}
                step="any"
                onChange={(value) => update("incident_angle_deg", value)}
                note="Angle of transmitter arrival. Default 0° broadside."
              />
              <label className="select-field">
                <span>Unit-cell pattern</span>
                <select
                  value={form.element_pattern ?? "isotropic"}
                  onChange={(e) =>
                    update(
                      "element_pattern",
                      e.target.value as "isotropic" | "cosine" | "cosine_squared"
                    )
                  }
                >
                  <option value="isotropic">Isotropic (Ideal Point Source)</option>
                  <option value="cosine">Cosine (cos θ — Realistic roll-off)</option>
                  <option value="cosine_squared">Cosine² (cos² θ — Microstrip patch)</option>
                </select>
              </label>

              <label className="select-field">
                <span>Phase quantization</span>
                <select
                  value={form.phase_quantization_bits ?? "none"}
                  onChange={(e) =>
                    update(
                      "phase_quantization_bits",
                      e.target.value === "none" ? null : Number(e.target.value)
                    )
                  }
                >
                  <option value="none">Continuous (Ideal phase)</option>
                  <option value="1">1-bit (2 states: 0, π)</option>
                  <option value="2">2-bit (4 states: 0, π/2, π, 3π/2)</option>
                  <option value="3">3-bit (8 states: 45° step)</option>
                </select>
              </label>

              <label className="checkbox-field">
                <input
                  type="checkbox"
                  checked={form.coupled_loss_model ?? false}
                  onChange={(e) => update("coupled_loss_model", e.target.checked)}
                />
                <span>Diode phase-coupled loss model</span>
              </label>
            </div>
          </details>

          <button type="submit" disabled={loading}>
            {loading ? "Running simulation…" : "Run simulation"}
          </button>
        </form>

        <section className="result-area" aria-live="polite">
          {error && (
            <p className="notice error" role="alert">
              {error}
            </p>
          )}
          {!result && !loading && !error && (
            <p className="empty-state">Configure the array and run a simulation to view its angular pattern.</p>
          )}
          {loading && <p className="empty-state">Calculating the backend model…</p>}
          {result && (
            <>
              <div className="chart-view-tabs" role="tablist" aria-label="Pattern visualization modes">
                <button
                  type="button"
                  className={chartMode === "db" ? "active" : ""}
                  onClick={() => setChartMode("db")}
                >
                  Rectangular (dB)
                </button>
                <button
                  type="button"
                  className={chartMode === "polar" ? "active" : ""}
                  onClick={() => setChartMode("polar")}
                >
                  Polar Pattern
                </button>
                <button
                  type="button"
                  className={chartMode === "linear" ? "active" : ""}
                  onClick={() => setChartMode("linear")}
                >
                  Linear Power (|AF|²)
                </button>
              </div>

              {chartMode === "db" && (
                <LineChart
                  title="Angular pattern comparison (Logarithmic)"
                  yLabel="Normalized power (dB)"
                  angles={result.angles_deg}
                  series={[
                    {
                      label: "Baseline",
                      values: result.baseline_normalized_power_db,
                      color: "#526275",
                      dash: "6 4",
                    },
                    {
                      label: "Phase-controlled",
                      values: result.controlled_normalized_power_db,
                      color: "#006b7b",
                    },
                  ]}
                  targetAngle={form.target_angle_deg}
                  peakAngle={result.sampled_main_lobe_angles_deg.controlled}
                  onExportCsv={exportCsv}
                  onExportJson={exportJson}
                />
              )}

              {chartMode === "polar" && (
                <PolarChart
                  angles={result.angles_deg}
                  series={[
                    {
                      label: "Baseline",
                      values: result.baseline_normalized_power_db,
                      color: "#526275",
                      dash: "5 3",
                    },
                    {
                      label: "Phase-controlled",
                      values: result.controlled_normalized_power_db,
                      color: "#006b7b",
                    },
                  ]}
                  targetAngle={form.target_angle_deg}
                  title="Spatial Radiation Pattern (Polar)"
                />
              )}

              {chartMode === "linear" && (
                <LineChart
                  title="Angular power pattern (Linear)"
                  yLabel="Normalized power |AF|²"
                  angles={result.angles_deg}
                  series={[
                    {
                      label: "Baseline",
                      values: result.baseline_normalized_power,
                      color: "#526275",
                      dash: "6 4",
                    },
                    {
                      label: "Phase-controlled",
                      values: result.controlled_normalized_power,
                      color: "#006b7b",
                    },
                  ]}
                  targetAngle={form.target_angle_deg}
                  peakAngle={result.sampled_main_lobe_angles_deg.controlled}
                  onExportCsv={exportCsv}
                  onExportJson={exportJson}
                />
              )}

              <Metrics
                items={[
                  {
                    label: "Target power",
                    value: format(result.target_metrics.controlled_normalized_power),
                    detail: "normalized",
                  },
                  {
                    label: "Target power improvement",
                    value:
                      result.target_metrics.improvement_db === null
                        ? "Unavailable"
                        : `${format(result.target_metrics.improvement_db, 2)} dB`,
                    detail: "vs baseline at target angle",
                  },
                  {
                    label: "Estimated peak",
                    value:
                      result.sampled_main_lobe_angles_deg.controlled === null
                        ? "Unavailable"
                        : `${format(result.sampled_main_lobe_angles_deg.controlled, 1)}°`,
                    detail:
                      result.research_metrics?.competing_lobe_detected
                        ? `competing peak (target lobe: ${format(result.research_metrics.target_lobe_angle_deg ?? null, 1)}°)`
                        : result.research_metrics?.pointing_error_deg !== null &&
                          result.research_metrics?.pointing_error_deg !== undefined
                        ? `error: ${result.research_metrics.pointing_error_deg}°`
                        : "sampled grid",
                  },
                  {
                    label: "HPBW (-3 dB width)",
                    value:
                      result.research_metrics?.hpbw_deg !== null &&
                      result.research_metrics?.hpbw_deg !== undefined
                        ? `${result.research_metrics.hpbw_deg}°`
                        : "Unavailable",
                    detail: "beamwidth",
                  },
                  {
                    label: "Peak sidelobe (PSLL)",
                    value:
                      result.research_metrics?.psll_db !== null &&
                      result.research_metrics?.psll_db !== undefined
                        ? `${result.research_metrics.psll_db} dB`
                        : "None visible",
                    detail: "relative to peak",
                  },
                  {
                    label: "Estimated directivity",
                    value:
                      result.research_metrics?.directivity_dbi !== null &&
                      result.research_metrics?.directivity_dbi !== undefined
                        ? `${result.research_metrics.directivity_dbi} dBi`
                        : "Unavailable",
                    detail: "1D array factor cut",
                  },
                  {
                    label: "Wavelength",
                    value: `${format(result.wavelength_m, 4)} m`,
                  },
                ]}
              />

              <PhaseTable
                baseline={result.baseline_phases_deg}
                controlled={result.controlled_phases_deg}
              />

              <section className="notes">
                <h2>Model notes</h2>
                <p>
                  dB uses a numerical floor of {result.db_floor_power.toExponential()} to avoid
                  infinite display values.
                </p>
                {result.warnings.map((warning) => (
                  <p className="notice warning" key={warning}>
                    {warning}
                  </p>
                ))}
                <p>{result.limitations[0]}</p>
              </section>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

function Overview({ openBeam }: { openBeam: () => void }) {
  const [state, setState] = useState("Checking");
  const check = () => {
    setState("Checking");
    getHealth()
      .then(() => setState("Connected"))
      .catch(() => setState("Unavailable"));
  };
  useEffect(check, []);
  return (
    <main className="page">
      <header className="page-header">
        <p className="eyebrow">Simulation platform</p>
        <h1>SmartRIS</h1>
        <p>Explore an idealized or research-mode programmable reflecting array through transparent numerical electromagnetic models.</p>
      </header>
      <section className="overview-content">
        <div>
          <h2>Start a beam-steering simulation</h2>
          <p>Configure a linear array, calculate ideal or quantized steering phases, and compare spatial radiation patterns in Cartesian and Polar plots.</p>
          <button onClick={openBeam}>Open beam steering</button>
        </div>
        <div className="status">
          <h2>Backend status</h2>
          <p>
            <strong>{state}</strong>
            {state === "Unavailable" && " — start the FastAPI server, then retry."}
          </p>
          <button className="secondary" onClick={check}>
            Check connection
          </button>
        </div>
      </section>
      <p className="model-note">
        Research advisory: Outputs are array-factor calculations with optional element pattern, phase quantization, and diode loss models. They are suitable for theoretical exploratory research, but omit 3D near-field coupling and full-wave Maxwell interactions.
      </p>
    </main>
  );
}

function TradeoffPage() {
  const [form, setForm] = useState(defaultTradeoff);
  const [result, setResult] = useState<TradeoffResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const update = <K extends keyof TradeoffRequest>(key: K, value: TradeoffRequest[K]) =>
    setForm((current) => ({ ...current, [key]: value }));
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await runTradeoff(form));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The experiment could not be completed.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <main className="page">
      <header className="page-header">
        <p className="eyebrow">Exploratory workflow</p>
        <h1>Trade-off lab</h1>
        <p>Optimize a directional objective while making the receiver and observation trade-off visible.</p>
      </header>
      <div className="workspace">
        <form className="controls" onSubmit={submit}>
          <h2>Experiment</h2>
          <NumericField
            label="Receiver angle"
            unit="degrees"
            value={form.receiver_angle_deg}
            min={-90}
            max={90}
            step="any"
            onChange={(value) => update("receiver_angle_deg", value)}
          />
          <NumericField
            label="Observation angle"
            unit="degrees"
            value={form.observation_angle_deg}
            min={-90}
            max={90}
            step="any"
            onChange={(value) => update("observation_angle_deg", value)}
          />
          <NumericField
            label="Penalty coefficient"
            unit="nonnegative"
            value={form.penalty}
            min={0}
            max={100}
            step="any"
            onChange={(value) => update("penalty", value)}
          />
          <NumericField
            label="Evaluation budget"
            unit="evaluations"
            value={form.max_evaluations}
            min={1}
            max={10000}
            step={10}
            onChange={(value) => update("max_evaluations", value)}
          />
          <button disabled={loading}>{loading ? "Running experiment…" : "Run trade-off experiment"}</button>
        </form>
        <section className="result-area" aria-live="polite">
          {error && <p className="notice error" role="alert">{error}</p>}
          {!result && !loading && !error && (
            <p className="empty-state">Set two directions and run the bounded coordinate-search experiment.</p>
          )}
          {loading && <p className="empty-state">Running deterministic coordinate search…</p>}
          {result && (
            <>
              <LineChart
                title="Initial and optimized patterns"
                yLabel="Normalized power (dB)"
                angles={result.initial.angles_deg}
                series={[
                  { label: "Initial", values: result.initial.normalized_power_db, color: "#526275", dash: "6 4" },
                  { label: "Optimized", values: result.optimized.normalized_power_db, color: "#006b7b" },
                ]}
              />
              <Metrics
                items={[
                  {
                    label: "Receiver power",
                    value: `${format(result.initial_receiver_power)} → ${format(result.final_receiver_power)}`,
                    detail: "normalized",
                  },
                  {
                    label: "Observation power",
                    value: `${format(result.initial_observation_power)} → ${format(result.final_observation_power)}`,
                    detail: "normalized proxy",
                  },
                  { label: "Objective", value: `${format(result.initial_objective)} → ${format(result.final_objective)}` },
                  { label: "Constraint", value: result.constraint_status.replaceAll("_", " ") },
                  {
                    label: "Search",
                    value: `${result.evaluation_count} evaluations`,
                    detail: result.stop_reason.replaceAll("_", " "),
                  },
                ]}
              />
              <p className="model-note">{result.scientific_note}</p>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

function TheoryPage() {
  return (
    <main className="page theory">
      <header className="page-header">
        <p className="eyebrow">Model reference</p>
        <h1>Theory &amp; Research Limitations</h1>
        <p>Scientific breakdown of the array model, electromagnetic equations, and guidelines for actual research.</p>
      </header>
      <section>
        <h2>Array Factor Formulation</h2>
        <code>AF(θ) = (1/N) Σ βₙ exp(j [ k xₙ sin θ + k xₙ sin θᵢ + φₙ ])</code>
        <p>
          The simulator calculates complex phasor contributions coherently prior to computing normalized directional power:
          <code>P(θ) = | EP(θ) · AF(θ) |²</code>. For an unprogrammed baseline array (<code>φₙ = 0</code>), constructive summation yields specular reflection at <code>θ = −θᵢ</code> (Snell's Law).
        </p>

        <h2>Bistatic RIS Steering Condition</h2>
        <code>φₙ = −k xₙ (sin θtarget + sin θincident)</code>
        <p>
          In true Reconfigurable Intelligent Surface (RIS) operation, an incident plane wave arrives from direction <code>θᵢ</code> (from the transmitter) and is steered toward <code>θ_target</code> (receiver) by canceling both the incoming surface phase ramp and the outgoing observation phase.
        </p>

        <h2>Embedded Element Radiation Pattern (EP)</h2>
        <p>
          Real RIS metamaterial unit cells or patch antennas are not isotropic point sources. They have an element factor:
        </p>
        <ul>
          <li><strong>Isotropic:</strong> <code>EP(θ) = 1.0</code> (Theoretical baseline)</li>
          <li><strong>Cosine:</strong> <code>EP(θ) = max(0, cos θ)</code> (Lambertian / planar aperture roll-off)</li>
          <li><strong>Cosine²:</strong> <code>EP(θ) = max(0, cos² θ)</code> (Microstrip patch antenna approximation)</li>
        </ul>

        <h2>Diode Phase-Coupled Loss Model (Abeywickrama Model)</h2>
        <code>β(φ) = (1 − β_min) · [ (sin(φ − φ₀) + 1) / 2 ]^α + β_min</code>
        <p>
          Practical RIS hardware (PIN diodes, varactors) exhibits phase-dependent reflection magnitude loss due to internal dielectric and semiconductor resonance.
        </p>

        <h2>Hardware Phase Quantization</h2>
        <p>
          Real RIS chips use discrete pin states rather than continuous floating-point phases:
        </p>
        <ul>
          <li><strong>1-bit:</strong> 2 states <code>&#123;0, π&#125;</code> (causes quantization lobes, ~3.9 dB gain loss)</li>
          <li><strong>2-bit:</strong> 4 states <code>&#123;0, π/2, π, 3π/2&#125;</code> (~0.9 dB loss)</li>
          <li><strong>3-bit:</strong> 8 states (45° steps, near continuous performance)</li>
        </ul>

        <h2>Critical Guidelines for Actual Academic Research</h2>
        <p>
          When writing a research paper, note that this tool provides accurate <strong>far-field array-factor analysis</strong>. For full-wave physical validation:
        </p>
        <ul>
          <li>Full-wave solvers (CST Studio, Ansys HFSS) are required to account for mutual coupling between sub-wavelength elements.</li>
          <li>Near-field spherical wavefront curvature should be used if the communication distance <code>d &lt; 2 D² / λ</code>.</li>
          <li>Path loss follows the cascaded radar equation <code>(4π / λ)² · (d₁ · d₂)²</code> for diffuse RIS or geometric optics for large electrical sizes.</li>
        </ul>
      </section>
    </main>
  );
}

export default function App() {
  const [page, setPage] = useState<Page>("overview");
  const navigation: [Page, string][] = [
    ["overview", "Overview"],
    ["beam", "Beam steering"],
    ["tradeoff", "Trade-off lab"],
    ["theory", "Theory & model"],
  ];
  return (
    <div className="app-shell">
      <header className="app-header">
        <button className="wordmark" onClick={() => setPage("overview")}>
          SmartRIS
        </button>
        <nav aria-label="Main navigation">
          {navigation.map(([key, label]) => (
            <button
              key={key}
              className={page === key ? "active" : ""}
              onClick={() => setPage(key)}
            >
              {label}
            </button>
          ))}
        </nav>
        <div className="header-actions">
          <a
            href="https://github.com/25sarvesh2005/SMARTRIS/commits/main"
            target="_blank"
            rel="noreferrer"
            className="commit-badge-link"
            title="View commit history on GitHub"
          >
            <span className="commit-dot"></span>
            Commit: 15a1dd7
          </a>
        </div>
      </header>
      {page === "overview" && <Overview openBeam={() => setPage("beam")} />}
      {page === "beam" && <BeamPage />}
      {page === "tradeoff" && <TradeoffPage />}
      {page === "theory" && <TheoryPage />}
      <footer className="app-footer">
        <p>SmartRIS • 6G Reconfigurable Intelligent Surface &amp; Beamforming Simulator</p>
        <div className="footer-links">
          <a
            href="https://github.com/25sarvesh2005/SMARTRIS/commit/15a1dd7"
            target="_blank"
            rel="noreferrer"
          >
            Latest Verified: <code>15a1dd7</code>
          </a>
          <span>•</span>
          <a
            href="https://github.com/25sarvesh2005/SMARTRIS/commits/main"
            target="_blank"
            rel="noreferrer"
          >
            All Commits
          </a>
          <span>•</span>
          <a
            href="https://github.com/25sarvesh2005/SMARTRIS"
            target="_blank"
            rel="noreferrer"
          >
            GitHub Repo
          </a>
        </div>
      </footer>
    </div>
  );
}
