export function PhaseTable({ baseline, controlled }: { baseline: number[]; controlled: number[] }) {
  return <section className="phase-section" aria-labelledby="phase-heading"><h2 id="phase-heading">Phase settings</h2><p>Programmed phase in degrees; element order matches the backend array.</p><div className="phase-scroll"><table><thead><tr><th>Element</th><th>Baseline</th><th>Phase-controlled</th></tr></thead><tbody>{controlled.map((phase, index) => <tr key={index}><td>{index}</td><td>{baseline[index].toFixed(2)}°</td><td>{phase.toFixed(2)}°</td></tr>)}</tbody></table></div></section>;
}

