# SmartRIS API

The local API is served at `http://127.0.0.1:8000`. Interactive OpenAPI documentation is available at `/docs` when the backend is running.

## `GET /api/health`

Returns a lightweight status object: `{"status":"ok","version":"0.1.0"}`.

## `GET /api/info`

Returns the model identifier, units, defaults, supported ranges, normalization statement, and principal scientific limitations.

## `POST /api/simulations/beam-steering`

Calculates baseline zero-phase and ideal phase-controlled patterns on the same angular grid.

```json
{
  "element_count": 8,
  "frequency_hz": 3000000000,
  "spacing_m": 0.05,
  "target_angle_deg": 25,
  "reflection_magnitude": 1,
  "angle_start_deg": -90,
  "angle_stop_deg": 90,
  "sample_count": 361,
  "incident_angle_deg": 0.0,
  "element_pattern": "isotropic",
  "phase_quantization_bits": null,
  "coupled_loss_model": false
}
```

`element_count` is 2–128, `frequency_hz` is greater than 1 MHz through 100 GHz, `spacing_m` is greater than 0.0001 m through 10 m, angles are -90 through 90 degrees, reflection magnitude is 0–1, and sample count is 181–1441. Optional research parameters: `incident_angle_deg` (-90° to 90°), `element_pattern` (`"isotropic"`, `"cosine"`, `"cosine_squared"`), `phase_quantization_bits` (1 to 8), and `coupled_loss_model` (boolean). Successful responses include angular arrays, baseline and controlled power in linear and dB forms, phase vectors in radians and degrees, target metrics, sampled peak estimates, research metrics (`hpbw_deg`, `psll_db`, `directivity_dbi`, `pointing_error_deg`), warnings, limitations, and the dB display floor.

## `POST /api/simulations/custom-phases`

Accepts the common array fields plus `phase_values` and `phase_units` (`"radians"` or `"degrees"`). The phase array must contain exactly one finite value per element. The response contains a single calculated pattern and metadata.

## `POST /api/simulations/tradeoff`

Accepts the common array fields plus `receiver_angle_deg`, `observation_angle_deg`, nonnegative `penalty`, a bounded `max_evaluations` (1–10,000), and optional nonnegative `observation_power_threshold`. It returns initial and final patterns, phase vectors, objective and directional metrics, evaluation count, stop reason, and truthful constraint status. The optimizer is deterministic coordinate search; it does not guarantee a global optimum.

Validation failures return HTTP 422 with structured field errors. No endpoint intentionally exposes exception stack traces.

