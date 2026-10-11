# SmartRIS — Master Project Prompt and Folder Structure


> Use this file as the master implementation brief for SmartRIS. It is a standalone project, not an interview deliverable. The user's frontend guardrail `agent.md` must be read before any frontend file is created or edited.


---

# Instructions to the coding agent

Act as a senior software engineer and scientific-computing developer. Build SmartRIS as a standalone, local-first scientific simulation platform. This is not an interview-specific repository. Do not include interview scripts, employer-specific language, or claims tailored to an institution.

## Mandatory frontend guardrail
Before creating or editing any frontend file, locate and read the user's frontend guardrail file named `agent.md`. Read it completely and obey it. Do not overwrite, weaken, rename, bypass, or silently ignore it. If it is missing or its location is ambiguous, stop frontend implementation and ask the user to provide or identify it. Backend-only work may continue. Do not claim that the file was read if it was unavailable. If it conflicts with a generic frontend recommendation in this document, preserve the user's guardrail and explain any material conflict.

## Initial workflow
1. Inspect the existing repository and current changes.
2. Read project instructions, README, dependency files, and existing code.
3. Locate and read `agent.md` before frontend work.
4. Preserve existing user work and adapt the structure where sensible.
5. Implement one coherent phase at a time.
6. Run tests relevant to each phase.
7. Do not report a test or build as passing unless it was actually run.
8. Do not fabricate results, measurements, hardware integrations, or scientific validation.
9. Do not add unnecessary services, databases, authentication, queues, or abstractions.
10. End each phase with a concise report of changes, tests, issues, and next steps.

## Definition of done
The project must have a documented mathematical model, tested numerical core, working backend API, frontend that renders real backend results, beam-steering comparison, clearly labeled exploratory optimization, validation and error handling, tests, accurate setup documentation, and explicit scientific limitations.


---

# Product definition and scope

SmartRIS — Programmable Reflecting Surface Simulation and Optimization Platform.

The app lets users configure an idealized linear reflecting array, calculate its angular array-factor pattern, set programmable element phases, compare baseline and controlled patterns, explore a constrained directional objective, and export reproducible results.

Primary users include students and developers exploring antenna-array fundamentals, scientific visualization, and phase-control optimization.

## Core user journeys
1. Configure element count, frequency, spacing, reflection magnitude, target angle, and angular sampling.
2. Run a baseline simulation.
3. Calculate ideal phase settings for a target angle.
4. Compare baseline and controlled patterns.
5. Inspect phase values and numerical metrics.
6. Optionally run a deterministic trade-off experiment with receiver and observation directions.
7. Save a configuration if experiment storage is implemented.
8. Export JSON or CSV results.

## Version-one scope
- Local development setup.
- Documented array-factor model.
- Frequency, element count, spacing, target angle, and reflection magnitude controls.
- Baseline and ideal-steering comparison.
- Interactive angular pattern visualization.
- Per-element phase display.
- Backend validation and structured errors.
- One explainable optimization experiment.
- Unit and API tests.
- README and scientific documentation.
- JSON/CSV export if time permits.

## Non-goals
Do not implement full-wave Maxwell-equation solving, real hardware control, a physical RCS claim, live laboratory measurements, complex 3D CAD, cloud collaboration, authentication, payment systems, a general workflow engine, or machine learning without a justified requirement. These can be future extensions, not version-one promises.


---

# Simple repository structure

Use a simple structure with separately maintained frontend and backend. Adapt existing repositories instead of moving files merely to match this example.

```text
smartris/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── frontend/
│   ├── agent.md                 # User guardrail if its actual location is here
│   ├── package.json
│   ├── package-lock.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api.ts
│       ├── types.ts
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── BeamSteering.tsx
│       │   ├── TradeoffLab.tsx
│       │   └── Theory.tsx
│       ├── components/
│       │   ├── Layout.tsx
│       │   ├── SimulationControls.tsx
│       │   ├── MetricCard.tsx
│       │   ├── RadiationPatternChart.tsx
│       │   ├── PhaseChart.tsx
│       │   ├── ComparisonPanel.tsx
│       │   └── ErrorNotice.tsx
│       └── styles/
│           └── global.css
├── backend/
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   ├── simulation.py
│   │   ├── optimization.py
│   │   └── experiments.py       # Optional
│   └── tests/
│       ├── test_simulation.py
│       ├── test_optimization.py
│       └── test_api.py
└── docs/
    ├── MATHEMATICAL_MODEL.md
    ├── API.md
    ├── VALIDATION.md
    └── LIMITATIONS.md
```

## Responsibilities
- `main.py`: create FastAPI app, register routes and middleware.
- `config.py`: local configuration, CORS origins, numerical limits.
- `schemas.py`: Pydantic request/response models and validation.
- `routes.py`: thin HTTP endpoints that call the numerical functions.
- `simulation.py`: constants, geometry, array factor, power, phase steering and pattern metrics.
- `optimization.py`: objective function and deterministic optimizer.
- `experiments.py`: optional experiment storage. Start in memory or use SQLite only if durable storage is actually required.
- `api.ts`: central frontend API client and error parsing.
- `types.ts`: TypeScript contracts matching Pydantic schemas.
- `pages/`: page-level state and composition.
- `components/`: reusable controls, charts, metrics, layout and errors.
- `docs/`: scientific equations, API contracts, validation and limitations.

Do not create empty placeholder files just to match the tree. Split modules only when there is a clear responsibility. Do not collapse the whole application into one file either.


---

# Technology and architecture

## Frontend
Use React, TypeScript, and Vite. Use the styling, component architecture, dependency choices, naming, accessibility and state-management patterns required by `agent.md`. A chart library with interactive polar/angular plots, such as Plotly, is suitable if permitted by the guardrail. Avoid unnecessary dependencies.

## Backend
Use Python 3.11 or a compatible supported version, FastAPI, Uvicorn, Pydantic, NumPy, Pytest, and HTTPX for API tests. Pin or constrain dependencies responsibly. Do not add packages that are not used.

## Local-first requirement
The core application must work locally without API keys, paid services, remote databases, cloud accounts, or hardware instruments.

## Architecture rules
- Python backend is the source of truth for numerical calculations.
- Frontend renders actual backend results; do not duplicate scientific formulas in React.
- Keep API schemas separate from the numerical engine.
- Centralize frontend HTTP calls.
- Use explicit units in field names or schema descriptions.
- Use safe local defaults.
- Configure CORS for the actual local frontend origin.
- Keep computational requests bounded.
- Do not expose stack traces or environment secrets to clients.
- Keep state management simple.
- Do not add a database server for local experiment history.


---

# Mathematical model

## Scientific honesty
The initial implementation is an idealized array-factor model. It is not a full-wave electromagnetic solver, physical surface model, hardware controller, or validated radar-cross-section simulator. Use accurate labels throughout the application.

## Constants and units
Use the speed of light in free space:
`c = 299792458.0 m/s`

For frequency `f_hz`:
`wavelength_m = c / f_hz`

For wavelength `wavelength_m`:
`k_rad_m = 2*pi / wavelength_m`

Use SI units inside the backend. The frontend may display GHz and centimetres, but must convert values correctly before sending requests. Use clear suffixes such as `_hz`, `_ghz`, `_m`, `_deg`, and `_rad`.

## Linear geometry
For N elements spaced by d metres:
`x_n = n*d`, for n = 0, ..., N-1.

In NumPy:
`positions_m = np.arange(N, dtype=float) * spacing_m`

The initial model is a uniform linear array, not a two-dimensional panel.

## Array factor
Use one consistent convention:
`AF(theta) = (1/N) * sum_n [a_n * beta_n * exp(j*(k*x_n*sin(theta) + phi_n))]`

Definitions:
- `AF(theta)`: normalized complex array factor.
- `N`: number of elements.
- `a_n`: nonnegative excitation amplitude.
- `beta_n`: reflection magnitude in [0, 1].
- `k`: wavenumber in radians per metre.
- `x_n`: element position in metres.
- `theta`: observation angle.
- `phi_n`: programmed phase in radians.
- `j`: square root of -1.

The normalization by N is part of the stated model. Do not change it in one module without updating the entire project.

## Normalized power
`P(theta) = abs(AF(theta))**2`

This is normalized directional power for the chosen model. It is not automatically absolute received power, antenna gain in dBi, power density, or radar cross section.

For display in dB:
`P_db = 10*log10(max(P, epsilon))`

Document epsilon as a numerical display floor, not a physical noise floor. Avoid NaN and infinity in JSON.

## Complex summation
Sum complex field contributions first, then compute squared magnitude. Do not add individual element powers and call that the coherent array factor.

## Steering phases
Under the array-factor convention above:
`phi_n = -k*x_n*sin(theta_target)`

This cancels the angle-dependent phase term at the target direction. The sign is tied to the exact equation above; do not mix conventions.

## Phase wrapping
Represent phases in `[-pi, pi)`. Convert to degrees for UI display:
`degrees = radians * 180/pi`
`radians = degrees * pi/180`

Keep backend calculations in radians unless a field is explicitly named as degrees.

## Reflection coefficient
A simplified element coefficient is:
`Gamma_n = beta_n * exp(j*phi_n)`, where `0 <= beta_n <= 1`.

Version one may use one scalar beta for all elements. Do not describe it as a complete material model.

## Angular sampling
Use an explicit validated grid, for example `np.linspace(start_deg, stop_deg, sample_count)`. Require start < stop, valid endpoints, and a bounded sample count. Compare patterns on the same grid. Do not claim greater peak-angle precision than the sampling supports.

## Main-lobe estimate
A basic estimate is the angle of the maximum sampled power. Label it as a sampled-grid estimate. If interpolation is added, document and test it.

## Spacing warning
Large spacing relative to wavelength can create grating-lobe concerns depending on scan angle and geometry. Provide a heuristic warning, not an unconditional claim that every spacing above half a wavelength always causes a grating lobe.

## Baseline and controlled patterns
Baseline: all programmed phases are zero.
Controlled: ideal steering phases for the target angle.
Return both phase vectors and patterns. Report target-direction power consistently. Prefer direct evaluation at the target angle for metrics, even if a sampled grid is used for visualization.

## Improvement metric
`improvement_db = 10*log10(P_controlled / P_baseline)`

Handle near-zero baseline values explicitly. Return a nullable metric or documented finite-floor result; do not return infinity or imply infinite physical improvement.

## Simplified directional trade-off
An exploratory objective may be:
`J(phi) = P(receiver_angle) - alpha*P(observation_angle)`, with alpha >= 0.

An optional constrained mode may maximize receiver-direction power subject to:
`P(observation_angle) <= threshold`.

This observation metric is a normalized array-factor proxy, not RCS. The UI must state that distinction near the controls and results.

## Optimization
Use a deterministic, explainable, bounded algorithm such as coordinate search. Return algorithm name, initial/final objective, initial/final receiver and observation powers, evaluation count, stop reason, final phase vector, and constraint status. Do not claim a global optimum without proof. If a constraint is infeasible within the search budget, report it honestly.

## Numerical stability
Reject non-finite inputs, invalid frequency, nonpositive spacing, empty or incorrectly sized phase vectors, excessive sample counts and unbounded optimizer budgets. Keep output finite. Do not silently clamp invalid values.


---

# Backend API

## Backend endpoints
Keep the API small and coherent.

### `GET /api/health`
Return `status` and `version`. It should be fast and must not run an optimization.

### `GET /api/info`
Return model identifier, units, defaults, supported ranges, normalization, assumptions and limitations.

### `POST /api/simulations/beam-steering`
Request fields should include element count, frequency in Hz, spacing in metres, target angle in degrees, reflection magnitude, angular start/stop and sample count.

Response should include:
- Model identifier and input configuration.
- Wavelength and wavenumber.
- Element positions.
- Baseline and controlled phase vectors.
- Angular grid.
- Baseline and controlled normalized power arrays.
- Optional dB arrays.
- Target-direction metrics.
- Sampled main-lobe estimates.
- Warnings and limitations.

### `POST /api/simulations/custom-phases`
Accept array configuration, an explicit phase vector, phase units and sampling parameters. Reject vector-length mismatch and non-finite values.

### `POST /api/simulations/tradeoff`
Accept array configuration, receiver angle, observation angle, nonnegative penalty, bounded optimization budget and optional constraint threshold. Return initial/final patterns, phase vectors, objective values, directional metrics, constraint status, evaluation count and stop reason.

### Optional experiment endpoints
Only after the core works:
- `GET /api/experiments`
- `POST /api/experiments`
- `GET /api/experiments/{experiment_id}`
- `DELETE /api/experiments/{experiment_id}`
- JSON/CSV export endpoint or equivalent client-side export.

## Validation
Use Pydantic request schemas. Suggested initial limits:
- Element count: 2–128.
- Angles: -90 to +90 degrees.
- Reflection magnitude: 0 to 1.
- Sample count: 181–1441.
- Positive, bounded frequency and spacing.
- Nonnegative penalty coefficient.
- Bounded optimizer evaluation count.

Document the exact frequency and spacing ranges selected in code. Reject invalid inputs with useful 422 errors. Never silently clamp invalid values.

## Serialization
Convert NumPy arrays and scalar types to native JSON-compatible values. Do not serialize complex numbers as ambiguous strings. If complex values are exposed, represent real and imaginary parts or magnitude and phase with explicit units.

## Errors
Use appropriate statuses: 200 success, 404 missing experiment, 422 validation failure, and 500 unexpected failure. Do not expose stack traces in normal API responses. Keep diagnostic logs useful but free of secrets.

## API contract
Document method, path, fields, types, units, constraints, responses, examples and errors in `docs/API.md`. Keep TypeScript interfaces aligned with Pydantic models.


---

# Frontend behavior and UX

## Frontend guardrail
This section is subordinate to the user's `agent.md`. Read that file first and use its required patterns.

## Visual goal
Create a clear scientific tool, not a generic admin dashboard. Prioritize chart legibility, explicit units, accessible controls, responsive layout, and accurate scientific labels. Avoid fake telemetry, fake accuracy scores, decorative metrics, excessive animation, and misleading units.

## Pages
### Dashboard
Show project purpose, backend status, model identifier, main features and a clear statement that outputs are simulations.

### Beam Steering
Controls: element count, frequency, spacing, target angle, reflection magnitude and angular resolution.
Results: baseline and controlled pattern, phase distribution, wavelength, target-direction normalized power, improvement metric if valid, main-lobe estimate and warnings.

### Trade-off Lab
Controls: receiver angle, observation angle, penalty, optimizer budget and optional constraint threshold.
Results: initial/optimized patterns, initial/final directional powers, objective values, constraint status, evaluation count and stop reason. Label the observation value as a simplified array-factor proxy, not RCS.

### Theory
Explain frequency, wavelength, phase, interference, linear arrays, array factor, steering, reflection magnitude, normalized power and model limitations.

## Controls
Every control needs a label, units, valid range and sensible default. Provide reset controls where useful. Validate on the frontend for usability and on the backend for correctness. Do not silently change submitted values.

## Charts
Every chart needs a title, labeled axes, clear units/normalization, legend, useful tooltips, responsive sizing, and empty/error states. Distinguish baseline and controlled curves by legend and, where possible, line style as well as color. Explain the dB display floor.

## Metrics
Only show values calculated from the current backend result. Each metric needs a name, value, unit or normalization, and explanatory help where ambiguous. Do not invent accuracy or success metrics.

## Loading and errors
Show a real loading state while requests are running. Do not fake progress percentages. Prevent accidental duplicate submission if necessary. If a request fails, show an actionable message and do not display an old result as if it were current. Preserve inputs after validation errors.

## State
Keep state simple and follow the guardrail. Centralize HTTP requests. Do not duplicate scientific formulas in the frontend. Keep inputs, current result, request status and errors distinct. Make stale data clear.

## Accessibility
Use labels, visible focus states, adequate contrast, keyboard navigation, accessible error messages and textual explanations for charts. Test responsive behavior.


---

# Testing, validation and scientific claims

## Test philosophy
Test mathematical behavior and invariants, not only implementation details. Use deterministic small configurations and tolerances appropriate to floating-point calculations.

## Numerical tests
Test:
- Wavelength and wavenumber.
- Element positions.
- Degree/radian conversion.
- Phase wrapping.
- Steering phase vector.
- Complex summation.
- Normalized power.
- dB conversion and floor.
- Angular grid.
- Target-angle evaluation.
- Baseline/controlled comparison.
- Trade-off objective.
- Constraint status.
- Deterministic optimization.
- Evaluation budget and stop reason.

## Useful invariants
- Valid positive frequency produces positive finite wavelength.
- Doubling frequency halves wavelength within tolerance.
- Positions are finite and start at zero.
- Phase vector length matches element count.
- Wrapped phases lie in the documented interval.
- Power is nonnegative and finite.
- Pattern array length matches the angular grid.
- Zero reflection magnitude yields zero reflected contribution in this model.
- A phase-aligned ideal configuration reaches the expected normalized coherent response.
- Repeated identical optimization runs are deterministic under the documented implementation.
- Evaluation count never exceeds the configured budget.

## API tests
Test health, model information, valid beam steering, custom phases, trade-off mode, invalid element count, invalid frequency, invalid spacing, invalid angle, wrong phase-vector length, excessive sample count, non-finite inputs, and missing experiment IDs if applicable.

## Frontend checks
Run TypeScript checks and production build. Verify loading states, API errors, unit conversions, real response data in charts, and no stale result being presented as current.

## Integration checks
Start backend, call the API, start frontend, run a simulation through the UI, change a parameter, confirm a new backend result is rendered, test invalid input, and test export if implemented.

## Scientific quality
Distinguish:
- Software correctness: code follows stated equations.
- Numerical validation: output follows analytical expectations and invariants.
- Model validation: model adequately represents a defined physical use.
- Experimental validation: predictions are compared against measurements or a trusted reference.

Version one may demonstrate software correctness and selected numerical validation. It must not claim physical or experimental validation without evidence.

## Limitations to document
- Idealized linear geometry.
- Simplified element behavior.
- No full-wave solution.
- No explicit mutual coupling.
- No detailed substrate/material model.
- No near-field coupling model.
- No physical RCS measurement.
- No hardware validation.
- No guarantee of global optimization.
- Sampling limits in peak-angle estimation.
- Frequency and spacing sensitivity.

## Scientific language
Use terms such as “simplified array-factor model,” “normalized directional power,” “idealized phase-controlled array,” and “exploratory optimization.”
Avoid unsupported claims such as “proven stealth,” “invisible to radar,” “experimentally validated,” or “complete electromagnetic simulation.”


---

# Documentation, commands and Git hygiene

## README requirements
Include project purpose, features, stack, folder structure, prerequisites, installation, backend/frontend run commands, tests, API docs, mathematical-model overview, visualization notes, exports, limitations, and license. Do not include interview-specific language.

## Documentation files
`docs/MATHEMATICAL_MODEL.md`: equations, units, variable definitions, sign convention and assumptions.
`docs/API.md`: endpoint contracts and examples.
`docs/VALIDATION.md`: tests, analytical cases, tolerances, and what has or has not been validated.
`docs/LIMITATIONS.md`: difference between array factor, antenna pattern, normalized directional power, received power, scattering and RCS.

## Backend setup
Windows PowerShell:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
macOS/Linux:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs normally appear at `http://127.0.0.1:8000/docs`.

## Frontend setup
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Use only scripts that actually exist in `package.json`. Configure the API base URL through an environment variable and document the default.

## Tests
Backend:
```bash
cd backend
pytest -q
```
Frontend build:
```bash
cd frontend
npm run build
```
Run these commands before claiming success.

## Git hygiene
Ignore virtual environments, bytecode, test caches, node_modules, build output, local environment files, temporary exports and local database files where appropriate. Do not commit secrets. Keep source, tests, lockfiles and `.env.example` tracked. Prefer focused commits and honest commit messages.


---

# Implementation phases and acceptance

## Phase 0 — Inspect and plan
Inspect existing files, read instructions, locate and read `agent.md`, preserve existing work, and write a short plan. If `agent.md` is missing, stop frontend work while backend work may proceed.

## Phase 1 — Numerical core
Implement constants, conversions, geometry, phase wrapping, array factor, normalized power, dB conversion and steering phases. Add unit tests and mathematical documentation.

Exit criteria: equations are consistent, tests pass, outputs are finite for valid inputs, and units/sign convention are documented.

## Phase 2 — Backend
Create FastAPI app, schemas, health/info endpoints, beam-steering endpoint, custom-phase endpoint and tests.

Exit criteria: server starts, OpenAPI docs load, valid requests work, invalid inputs return useful errors.

## Phase 3 — Frontend foundation
Only after reading `agent.md`, create/adapt the frontend, types, API client, layout, health indicator, loading state and error handling.

Exit criteria: frontend starts, API call works, guardrail is followed, and no scientific formula is duplicated in UI.

## Phase 4 — Beam-steering UI
Add controls, pattern chart, phase chart, metrics, warnings and model limitations.

Exit criteria: an end-to-end simulation works and charts display backend data.

## Phase 5 — Optimization
Implement deterministic bounded optimization, objective/constraint reporting, tests and Trade-off Lab.

Exit criteria: initial/final metrics, evaluation count, stop reason and constraint status are correct.

## Phase 6 — Experiments and exports
Add experiment history only if core features are stable. Choose in-memory storage first or SQLite if persistence is required. Add JSON/CSV export and tests.

## Phase 7 — Polish and docs
Check accessibility, responsive behavior, README accuracy, model labels, API docs and limitations. Remove dead code and unused dependencies.

## Phase 8 — Release check
Run backend tests, frontend build and a manual end-to-end simulation. Review Git diff and ensure no secrets or false claims.

## Acceptance criteria
- Numerical model is documented.
- Complex fields are summed before power is calculated.
- Steering phases match the selected sign convention.
- Backend validates input.
- API response fields are documented.
- Frontend renders real backend results.
- Baseline and controlled patterns can be compared.
- Optimizer reports actual objective and constraint status.
- Tests cover numerical behavior and API validation.
- Setup instructions match the repository.
- Frontend guardrail is respected.
- No fake outputs or unsupported scientific claims remain.

## Final work report
Report files created/modified, features actually implemented, exact tests run and observed outcomes, frontend build status, startup commands, known issues, future features, scientific limitations, and whether `agent.md` was found and followed.


---

# Detailed checklist — Numerical function checks


| Area | Input or trigger | Expected behavior |
|---|---|---|

| Wavelength | Positive finite frequency | Positive finite metres; doubling frequency halves wavelength |

| Element positions | Element count and positive spacing | Finite one-dimensional positions beginning at zero |

| Phase wrapping | Finite phase vector | Equivalent phasors and documented interval |

| Steering phases | Positions, wavenumber and target angle | Vector length matches element count; phases finite |

| Array factor | Angles, positions, phases, amplitudes, beta and k | Complex output with expected shape and finite values |

| Normalized power | Complex array factor | Nonnegative finite values |

| dB conversion | Normalized power and epsilon | Finite output with documented floor |

| Trade-off objective | Phases, receiver/observation angles and alpha | Objective equals reward minus penalty |

| Optimizer | Initial phases, objective and budget | Bounded deterministic result and explicit stop reason |



Additional rules:

- [ ] Verify **Wavelength** using the stated input and expected behavior.

- [ ] Verify **Element positions** using the stated input and expected behavior.

- [ ] Verify **Phase wrapping** using the stated input and expected behavior.

- [ ] Verify **Steering phases** using the stated input and expected behavior.

- [ ] Verify **Array factor** using the stated input and expected behavior.

- [ ] Verify **Normalized power** using the stated input and expected behavior.

- [ ] Verify **dB conversion** using the stated input and expected behavior.

- [ ] Verify **Trade-off objective** using the stated input and expected behavior.

- [ ] Verify **Optimizer** using the stated input and expected behavior.


---

# Detailed checklist — API endpoint checks


| Area | Input or trigger | Expected behavior |
|---|---|---|

| GET /api/health | No body required | Status and version; no expensive simulation |

| GET /api/info | No body required | Model, units, limits and caveats |

| POST /api/simulations/beam-steering | Valid array configuration | Baseline/controlled patterns, phases, metrics and warnings |

| POST /api/simulations/custom-phases | Configuration plus phase vector | Pattern or explicit validation error |

| POST /api/simulations/tradeoff | Configuration, directions and bounded objective | Initial/final results and truthful constraint status |

| Experiment create | Configuration and result metadata | Identifier and documented storage behavior |

| Experiment retrieve | Known identifier | Stored record or 404 |

| JSON export | Valid result/experiment | Parseable JSON with units and model metadata |

| CSV export | Valid angular pattern | Header row and one row per angle |



Additional rules:

- [ ] Verify **GET /api/health** using the stated input and expected behavior.

- [ ] Verify **GET /api/info** using the stated input and expected behavior.

- [ ] Verify **POST /api/simulations/beam-steering** using the stated input and expected behavior.

- [ ] Verify **POST /api/simulations/custom-phases** using the stated input and expected behavior.

- [ ] Verify **POST /api/simulations/tradeoff** using the stated input and expected behavior.

- [ ] Verify **Experiment create** using the stated input and expected behavior.

- [ ] Verify **Experiment retrieve** using the stated input and expected behavior.

- [ ] Verify **JSON export** using the stated input and expected behavior.

- [ ] Verify **CSV export** using the stated input and expected behavior.


---

# Detailed checklist — Frontend interaction checks


| Area | Input or trigger | Expected behavior |
|---|---|---|

| Health indicator | Backend available/unavailable | Accurate status without false success |

| Simulation controls | Valid values and units | Correct request payload |

| Submit | Valid form | Loading state, API call and result |

| Invalid form | Out-of-range value | Readable error and preserved input |

| Pattern chart | Backend response arrays | Labeled axes, legend and correct data |

| Phase chart | Returned phase vector | Correct units and element indexing |

| Trade-off run | Valid objective configuration | Initial/final results and constraint status |

| Export | Existing calculated result | Download matches calculated values |

| Responsive layout | Narrow viewport | Controls and charts remain usable |

| Accessibility | Keyboard-only navigation | Labels, focus and actionable errors |



Additional rules:

- [ ] Verify **Health indicator** using the stated input and expected behavior.

- [ ] Verify **Simulation controls** using the stated input and expected behavior.

- [ ] Verify **Submit** using the stated input and expected behavior.

- [ ] Verify **Invalid form** using the stated input and expected behavior.

- [ ] Verify **Pattern chart** using the stated input and expected behavior.

- [ ] Verify **Phase chart** using the stated input and expected behavior.

- [ ] Verify **Trade-off run** using the stated input and expected behavior.

- [ ] Verify **Export** using the stated input and expected behavior.

- [ ] Verify **Responsive layout** using the stated input and expected behavior.

- [ ] Verify **Accessibility** using the stated input and expected behavior.


---

# Test-case bank — Frequency and units


- [ ] Valid 3 GHz input is converted to 3,000,000,000 Hz before the backend call.

- [ ] Doubling frequency halves free-space wavelength within a suitable numerical tolerance.

- [ ] Zero frequency is rejected.

- [ ] Negative frequency is rejected.

- [ ] NaN and infinity are rejected.

- [ ] Displayed wavelength uses metres or centimetres consistently.

- [ ] Frequency labels distinguish GHz from Hz.


---

# Test-case bank — Geometry and spacing


- [ ] Minimum supported element count is accepted.

- [ ] Maximum supported element count is accepted.

- [ ] Element count below minimum is rejected.

- [ ] Element count above maximum is rejected.

- [ ] Positive spacing produces finite positions.

- [ ] Zero spacing is rejected unless explicitly supported for a test-only mathematical case.

- [ ] Negative spacing is rejected.

- [ ] Positions begin at zero and increase by the configured spacing.

- [ ] Spacing units are converted correctly from UI to API.


---

# Test-case bank — Angles and phases


- [ ] Broadside target produces the expected zero phase progression under the chosen convention.

- [ ] Positive target angle produces finite steering phases.

- [ ] Negative target angle produces finite steering phases.

- [ ] Target angle outside the supported interval is rejected.

- [ ] Phase values are wrapped into the documented interval.

- [ ] Degrees are converted to radians exactly once.

- [ ] Phase-vector length mismatch is rejected.

- [ ] Non-finite phase entries are rejected.


---

# Test-case bank — Array-factor calculations


- [ ] Output pattern length equals angular sample count.

- [ ] Power is computed from squared magnitude of the complex field sum.

- [ ] Power is nonnegative.

- [ ] All returned values are finite for valid inputs.

- [ ] Reflection magnitude zero produces zero modeled reflected contribution.

- [ ] Unit reflection magnitude allows the expected ideal coherent normalized peak.

- [ ] Baseline and controlled patterns share the same angular grid.

- [ ] Decibel floor is finite and documented.

- [ ] Near-zero baseline improvement is handled without infinity.


---

# Test-case bank — Optimization behavior


- [ ] Repeated runs with identical inputs return the same result under the deterministic algorithm.

- [ ] Evaluation count does not exceed the requested maximum.

- [ ] Objective values match direct objective-function evaluation.

- [ ] Final phase-vector length equals element count.

- [ ] Stop reason distinguishes convergence from evaluation-budget exhaustion.

- [ ] Constraint status is computed from final directional power.

- [ ] An infeasible constraint is not marked as satisfied.

- [ ] Negative penalty coefficient is rejected.

- [ ] Invalid optimization budget is rejected.


---

# Test-case bank — API and frontend integration


- [ ] Health endpoint returns a successful response when the server is running.

- [ ] Invalid requests return a documented validation response.

- [ ] API failures appear as readable UI errors.

- [ ] Submitting a valid form calls the real backend.

- [ ] Chart values come from the response and not a static sample array.

- [ ] Changing a parameter causes a new request and recalculated result.

- [ ] An old result is not labeled as current after a failed request.

- [ ] TypeScript build catches request/response type mismatches.

- [ ] Exported JSON parses successfully.

- [ ] CSV headers and row counts match the angular samples.



---

# Final instruction to the coding agent

Start by inspecting the repository and finding the user's `agent.md` frontend guardrail. Do not create or edit frontend files until you have read it. Then build the numerical core first, test it, expose it through FastAPI, and connect the frontend to real API results. Keep the structure simple, the model assumptions explicit, and the project independent of any interview or job application. Finish with an honest report of completed work, tests actually run, and known limitations.
