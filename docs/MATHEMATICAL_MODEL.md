# SmartRIS mathematical model

SmartRIS implements a one-dimensional phase-controlled array-factor model for Reconfigurable Intelligent Surface (RIS) simulation and directional exploration.

## 1. Physical and Spatial Geometry
For frequency `f_hz`, the free-space wavelength is `λ = c / f_hz`, where `c = 299792458.0 m/s`, and wavenumber is `k = 2π / λ` rad/m. Element positions for a Uniform Linear Array (ULA) of `N` elements with spacing `d_m` are `x_n = n d_m`.

## 2. Array Factor & Bistatic Scattering
When an incident plane wave arrives at angle `θ_incident` (measured from the surface normal toward +x) and scatters into far-field direction `θ`, the incident wave advances along the array surface with spatial phase `ψ_inc(x_n) = +k x_n sin(θ_incident)`. The far-field observation spatial phase from element `n` in direction `θ` is `+k x_n sin(θ)`.

The normalized complex far-field array factor is:

`AF(θ) = (1/N) Σ β_n exp(j [ k x_n sin(θ) + k x_n sin(θ_incident) + φ_n ])`

where:
- `β_n` is the per-element reflection magnitude in `[0, 1]`.
- `φ_n` is the programmed element reflection phase shift in radians.
- For an unprogrammed baseline array (`φ_n = 0`), constructive interference occurs when `sin(θ) + sin(θ_incident) = 0`, producing a specular reflection peak at `θ = -θ_incident`, in exact accordance with Snell's Law.

## 3. Element Radiation Pattern (EP)
Real unit cells exhibit angular roll-off (obliquity factor). The total radiation field is `E(θ) = EP(θ) · AF(θ)`, where:
- **Isotropic:** `EP(θ) = 1`
- **Cosine:** `EP(θ) = max(0, cos(θ))` (Lambertian aperture)
- **Cosine²:** `EP(θ) = max(0, cos²(θ))` (Microstrip patch antenna approximation)

Normalized directional power is evaluated after coherent summation: `P(θ) = |E(θ)|²`.

## 4. Phase Control & Quantization
Constructive steering to `θ_target` requires canceling both the incident wave phase ramp and the outgoing observation phase:
`φ_n = -k x_n (sin(θ_target) + sin(θ_incident))`

When hardware quantization (`B` bits) is enabled, phases are mapped to `2^B` discrete states:
`φ_quantized = round(φ / Δ) · Δ`, where `Δ = 2π / 2^B`.

## 5. Practical Diode Phase-Coupled Loss Model
Practical semiconductor phase shifters (PIN diodes, varactors) exhibit phase-dependent absorption (Abeywickrama model):
`β(φ) = (1 - β_min) · [ (sin(φ - φ_0) + 1) / 2 ]^α + β_min`
with `β_min = 0.2`, `φ_0 = 0`, and `α = 1.6`.

## 6. Research Metrics
- **HPBW (Half-Power Beamwidth):** Angular width between the `-3 dB` power points (`P ≥ 0.5 P_peak`) of the main lobe.
- **PSLL (Peak Sidelobe Level):** Relative amplitude in dB of the highest local maximum outside the main lobe nulls.
- **Directivity (dBi):** Numerically integrated array gain proxy `10 log10(2 P_peak / ∫ P(θ) cos(θ) dθ)`.
- **Pointing Error:** `|θ_sampled_peak - θ_target|`.


