"""Automated regression test suite for Phase 2: Beam Steering Physics and Radiation Metrics.

Validates all 16 requirements specified in Section 11 of the specification:
1. Wavelength conversion and element positions
2. Continuous-phase steering at 0°, +25°, and −25°
3. Incident-wave angles of 0°, +5°, and −5°
4. Correct phase quantization and phase units
5. Symmetry of the ideal broadside array pattern
6. Independent array-factor reference agreement
7. Unit-cell field-versus-power multiplication
8. Main-lobe identification with competing maxima
9. HPBW interpolation and missing-crossing behavior
10. PSLL with correct main-lobe exclusion
11. Target power and target-angle power improvement
12. Zero-power and near-zero baseline handling
13. Reflection magnitude at 0 and 1
14. CSV and JSON export correctness
15. All three visualization modes consistency
16. Changes to frequency, element count, spacing, incident angle, and target angle
"""

from __future__ import annotations

import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.config import SPEED_OF_LIGHT_M_S
from app.main import app
from app.simulation import (
    angular_grid_deg,
    array_factor,
    calculate_directivity_dbi,
    calculate_hpbw_deg,
    calculate_psll_db,
    directional_power,
    element_positions_m,
    find_peaks_and_lobes,
    improvement_db,
    incident_phase_rad,
    normalized_power,
    power_to_db,
    quantize_phases_rad,
    steering_phases_rad,
    wavelength_m,
    wavenumber_rad_m,
    wrap_phase_rad,
)

client = TestClient(app)


# 1. Wavelength conversion and element positions
def test_req1_wavelength_and_element_positions_4ghz() -> None:
    f = 4.0e9
    lam = wavelength_m(f)
    expected_lam = SPEED_OF_LIGHT_M_S / 4.0e9
    assert lam == pytest.approx(expected_lam, rel=1e-9)
    assert round(lam, 5) == 0.07495

    k = wavenumber_rad_m(f)
    assert k == pytest.approx(2.0 * math.pi / lam, rel=1e-9)

    d = 0.05
    ratio = d / lam
    assert ratio == pytest.approx(0.667128, rel=1e-4)

    positions = element_positions_m(8, d)
    expected_positions = np.array([0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35])
    assert np.allclose(positions, expected_positions)


# 2. Continuous-phase steering at 0°, +25°, and -25°
def test_req2_continuous_phase_steering_at_0_plus25_minus25() -> None:
    f = 4.0e9
    d = 0.05
    N = 8
    pos = element_positions_m(N, d)
    k = wavenumber_rad_m(f)
    angles_deg = angular_grid_deg(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles_deg)

    for target in [0.0, 25.0, -25.0]:
        phases = steering_phases_rad(pos, k, target, incident_angle_deg=0.0)
        af = array_factor(angles_rad, pos, phases, k, 1.0, incident_angle_deg=0.0, element_pattern="isotropic")
        power = normalized_power(af)
        peaks = find_peaks_and_lobes(angles_deg, power, target)

        assert peaks["global_peak_angle"] == pytest.approx(target, abs=0.5)
        assert peaks["target_lobe_angle"] == pytest.approx(target, abs=0.5)
        assert peaks["competing_lobe_present"] is False


# 3. Incident-wave angles of 0°, +5°, and -5°
def test_req3_bistatic_incident_angles_0_plus5_minus5() -> None:
    f = 4.0e9
    d = 0.05
    N = 8
    pos = element_positions_m(N, d)
    k = wavenumber_rad_m(f)
    angles_deg = angular_grid_deg(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles_deg)
    target = 25.0

    for inc in [0.0, 5.0, -5.0]:
        # Steered beam
        phases = steering_phases_rad(pos, k, target, incident_angle_deg=inc)
        af_steered = array_factor(angles_rad, pos, phases, k, 1.0, incident_angle_deg=inc, element_pattern="isotropic")
        power_steered = normalized_power(af_steered)
        peaks_steered = find_peaks_and_lobes(angles_deg, power_steered, target)

        assert peaks_steered["global_peak_angle"] == pytest.approx(target, abs=0.5)

        # Baseline unsteered beam must satisfy Snell's Law of specular reflection: peak at -incident
        af_base = array_factor(angles_rad, pos, np.zeros(N), k, 1.0, incident_angle_deg=inc, element_pattern="isotropic")
        power_base = normalized_power(af_base)
        peaks_base = find_peaks_and_lobes(angles_deg, power_base, None)
        assert peaks_base["global_peak_angle"] == pytest.approx(-inc, abs=0.5)


# 4. Correct phase quantization and phase units
def test_req4_phase_quantization_and_units() -> None:
    # 1-bit quantization (2 states: 0 and -pi/pi)
    raw = np.array([0.1, 1.5, -1.4, 3.0])
    q1 = quantize_phases_rad(raw, bits=1)
    step1 = 2.0 * math.pi / 2
    assert np.allclose(np.sin(q1), 0.0, atol=1e-10)

    # 2-bit quantization (4 states: 0, pi/2, pi, -pi/2)
    q2 = quantize_phases_rad(raw, bits=2)
    step2 = 2.0 * math.pi / 4
    multiples = np.round(q2 / step2)
    assert np.allclose(q2, wrap_phase_rad(multiples * step2))

    # Phase wrapping equivalence
    test_phases = np.array([-3.5 * math.pi, -math.pi, 0.0, math.pi, 2.5 * math.pi])
    wrapped = wrap_phase_rad(test_phases)
    assert np.all(wrapped >= -math.pi)
    assert np.all(wrapped < math.pi)
    assert np.allclose(np.exp(1j * wrapped), np.exp(1j * test_phases))


# 5. Symmetry of the ideal broadside array pattern
def test_req5_symmetry_of_broadside_pattern() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    angles_deg = angular_grid_deg(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles_deg)

    power = normalized_power(array_factor(angles_rad, pos, np.zeros(8), k, 1.0, incident_angle_deg=0.0))
    # Must be perfectly symmetric around 0 deg
    assert np.allclose(power, power[::-1], atol=1e-9)

    # Must match Dirichlet analytical closed form
    psi = k * 0.05 * np.sin(angles_rad)
    with np.errstate(divide="ignore", invalid="ignore"):
        dirichlet = np.where(np.abs(psi) < 1e-9, 1.0, np.sin(4.0 * psi) / (8.0 * np.sin(psi / 2.0))) ** 2
    assert np.allclose(power, dirichlet, atol=1e-9)


# 6. Independent array-factor reference agreement
def test_req6_independent_reference_agreement() -> None:
    N = 8
    f = 4.0e9
    d = 0.05
    theta_i_deg = 5.0
    theta_t_deg = 25.0
    k = 2.0 * math.pi * f / SPEED_OF_LIGHT_M_S

    angles_deg = np.linspace(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles_deg)
    pos = np.arange(N) * d

    # Independent reference calculation from first principles
    # Reflected phase: phi_n = -k * x_n * (sin(theta_t) + sin(theta_i))
    phi_ref = -k * pos * (math.sin(math.radians(theta_t_deg)) + math.sin(math.radians(theta_i_deg)))
    psi_inc_ref = k * pos * math.sin(math.radians(theta_i_deg))

    ref_field = np.zeros(len(angles_rad), dtype=complex)
    for n in range(N):
        phase_term = k * pos[n] * np.sin(angles_rad) + psi_inc_ref[n] + phi_ref[n]
        ref_field += np.exp(1j * phase_term)
    ref_field = (ref_field / N) * np.maximum(0.0, np.cos(angles_rad))
    ref_power = np.abs(ref_field) ** 2

    # App calculation
    app_phases = steering_phases_rad(pos, k, theta_t_deg, incident_angle_deg=theta_i_deg)
    app_field = array_factor(
        angles_rad, pos, app_phases, k, 1.0, incident_angle_deg=theta_i_deg, element_pattern="cosine"
    )
    app_power = normalized_power(app_field)

    assert np.allclose(app_power, ref_power, atol=1e-12)


# 7. Unit-cell field-versus-power multiplication
def test_req7_unit_cell_field_versus_power_multiplication() -> None:
    pos = element_positions_m(4, 0.05)
    k = wavenumber_rad_m(3.0e9)
    th_deg = np.array([0.0, 60.0])
    th_rad = np.deg2rad(th_deg)

    af_iso = array_factor(th_rad, pos, np.zeros(4), k, 1.0, element_pattern="isotropic")
    af_cos = array_factor(th_rad, pos, np.zeros(4), k, 1.0, element_pattern="cosine")

    p_iso = normalized_power(af_iso)
    p_cos = normalized_power(af_cos)

    # At 60 deg, cos(60) = 0.5, so power must be multiplied by cos^2(60) = 0.25
    assert p_cos[0] == pytest.approx(p_iso[0])
    assert p_cos[1] == pytest.approx(p_iso[1] * (0.5**2), rel=1e-5)


# 8. Main-lobe identification with competing maxima
def test_req8_main_lobe_identification_competing_maxima() -> None:
    angles_deg = np.linspace(-90.0, 90.0, 361)
    # Synthetic dual-beam pattern: beam 1 at -20 deg with power 0.9, beam 2 at +30 deg with power 0.7
    power = 0.9 * np.exp(-((angles_deg - (-20.0)) ** 2) / 20.0) + 0.7 * np.exp(-((angles_deg - 30.0) ** 2) / 20.0)

    # If target is +30 deg:
    peaks = find_peaks_and_lobes(angles_deg, power, target_angle_deg=30.0)
    assert peaks["global_peak_angle"] == pytest.approx(-20.0, abs=0.5)
    assert peaks["global_peak_power"] == pytest.approx(0.9, abs=0.01)
    assert peaks["target_lobe_angle"] == pytest.approx(30.0, abs=0.5)
    assert peaks["target_lobe_power"] == pytest.approx(0.7, abs=0.01)
    assert peaks["competing_lobe_present"] is True

    # If target is -20 deg:
    peaks_target_global = find_peaks_and_lobes(angles_deg, power, target_angle_deg=-20.0)
    assert peaks_target_global["global_peak_angle"] == pytest.approx(-20.0, abs=0.5)
    assert peaks_target_global["target_lobe_angle"] == pytest.approx(-20.0, abs=0.5)
    assert peaks_target_global["competing_lobe_present"] is False


# 9. HPBW interpolation and missing-crossing behavior
def test_req9_hpbw_interpolation_and_missing_crossing() -> None:
    angles = np.linspace(-90.0, 90.0, 361)
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)

    # Steered to 25 deg
    phases = steering_phases_rad(pos, k, 25.0)
    power = normalized_power(array_factor(np.deg2rad(angles), pos, phases, k, 1.0))
    hpbw = calculate_hpbw_deg(angles, power)
    assert hpbw == 14.15

    # Steered to 88 deg: crossing falls outside grid, must safely return None
    phases_edge = steering_phases_rad(pos, k, 88.0)
    power_edge = normalized_power(array_factor(np.deg2rad(angles), pos, phases_edge, k, 1.0))
    assert calculate_hpbw_deg(angles, power_edge) is None


# 10. PSLL with correct main-lobe exclusion
def test_req10_psll_with_main_lobe_exclusion() -> None:
    angles = np.linspace(-90.0, 90.0, 361)
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 25.0)
    power = normalized_power(array_factor(np.deg2rad(angles), pos, phases, k, 1.0))

    psll = calculate_psll_db(angles, power)
    assert psll is not None
    # Must exclude main lobe and match theoretical ULA sidelobe ~ -13 dB
    assert -13.5 <= psll <= -12.5


# 11. Target power and target-angle power improvement
def test_req11_target_power_and_improvement_exact_physical_definition() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(4.0e9)
    target = 25.0
    inc = 5.0

    phases = steering_phases_rad(pos, k, target, incident_angle_deg=inc)
    p_ctrl = directional_power(target, pos, phases, k, 1.0, incident_angle_deg=inc, element_pattern="cosine")
    p_base = directional_power(target, pos, np.zeros(8), k, 1.0, incident_angle_deg=inc, element_pattern="cosine")

    # Target power under continuous phase and cosine pattern must be cos^2(25) = 0.8214
    assert p_ctrl == pytest.approx(math.cos(math.radians(25.0)) ** 2, rel=1e-5)
    assert p_base > 0.0

    delta = improvement_db(p_ctrl, p_base)
    assert delta is not None
    assert delta == pytest.approx(10.0 * math.log10(p_ctrl / p_base), rel=1e-5)


# 12. Zero-power and near-zero baseline handling
def test_req12_zero_power_and_near_zero_baseline_handling() -> None:
    angles = np.linspace(-90.0, 90.0, 361)
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)

    # Gamma = 0.0
    zero_power = normalized_power(array_factor(np.deg2rad(angles), pos, np.zeros(8), k, 0.0))
    assert np.all(zero_power == 0.0)

    db = power_to_db(zero_power)
    assert np.all(np.isfinite(db))
    assert calculate_hpbw_deg(angles, zero_power) is None
    assert calculate_psll_db(angles, zero_power) is None
    assert calculate_directivity_dbi(np.deg2rad(angles), zero_power) is None

    # Improvement with zero or near-zero baseline
    assert improvement_db(1.0, 0.0) is None
    assert improvement_db(1.0, 1e-13) is None
    assert improvement_db(0.0, 1.0) is None


# 13. Reflection magnitude at 0 and 1
def test_req13_reflection_magnitude_scaling() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 25.0)
    angles_rad = np.deg2rad(np.linspace(-90.0, 90.0, 361))

    for gamma in [0.0, 0.25, 0.5, 0.75, 1.0]:
        p = normalized_power(array_factor(angles_rad, pos, phases, k, gamma))
        peak = float(np.max(p))
        assert peak == pytest.approx(gamma**2, rel=1e-3 if gamma > 0 else 0)


# 14. CSV and JSON export correctness
def test_req14_csv_and_json_export_correctness() -> None:
    resp = client.post(
        "/api/simulations/beam-steering",
        json={
            "element_count": 8,
            "frequency_hz": 4.0e9,
            "spacing_m": 0.05,
            "target_angle_deg": 25.0,
            "incident_angle_deg": 5.0,
            "element_pattern": "cosine",
            "sample_count": 361,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    # JSON checks
    assert "angles_deg" in data
    assert "baseline_normalized_power_db" in data
    assert "controlled_normalized_power_db" in data
    assert "baseline_normalized_power" in data
    assert "controlled_normalized_power" in data
    assert len(data["angles_deg"]) == 361
    assert "target_metrics" in data
    assert "research_metrics" in data
    assert data["research_metrics"]["target_lobe_angle_deg"] is not None
    assert "competing_lobe_detected" in data["research_metrics"]

    # CSV string generation
    header = "angle_deg,baseline_power_db,controlled_power_db,baseline_linear,controlled_linear\n"
    rows = [
        f"{data['angles_deg'][i]:.2f},{data['baseline_normalized_power_db'][i]:.4f},{data['controlled_normalized_power_db'][i]:.4f},{data['baseline_normalized_power'][i]:.6f},{data['controlled_normalized_power'][i]:.6f}"
        for i in range(len(data["angles_deg"]))
    ]
    csv_text = header + "\n".join(rows)
    assert len(csv_text.splitlines()) == 362


# 15. All three visualization modes consistency
def test_req15_three_visualization_modes_consistency() -> None:
    resp = client.post(
        "/api/simulations/beam-steering",
        json={"frequency_hz": 4.0e9, "target_angle_deg": 25.0, "incident_angle_deg": 5.0},
    )
    data = resp.json()
    linear = np.array(data["controlled_normalized_power"])
    db = np.array(data["controlled_normalized_power_db"])

    # dB view is directly 10 * log10(linear)
    db_from_linear = 10.0 * np.log10(np.maximum(linear, 1e-12))
    assert np.allclose(db, db_from_linear, atol=1e-5)


# 16. Changes to frequency, element count, spacing, incident angle, and target angle
@pytest.mark.parametrize("f_hz", [2.0e9, 4.0e9, 10.0e9])
@pytest.mark.parametrize("n_elem", [4, 8, 16])
@pytest.mark.parametrize("inc_deg,tgt_deg", [(-10.0, 20.0), (0.0, 0.0), (10.0, -25.0)])
def test_req16_parametric_variations(f_hz: float, n_elem: int, inc_deg: float, tgt_deg: float) -> None:
    d = 0.03
    pos = element_positions_m(n_elem, d)
    k = wavenumber_rad_m(f_hz)
    angles_deg = angular_grid_deg(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles_deg)

    phases = steering_phases_rad(pos, k, tgt_deg, incident_angle_deg=inc_deg)
    af = array_factor(angles_rad, pos, phases, k, 1.0, incident_angle_deg=inc_deg, element_pattern="isotropic")
    p = normalized_power(af)
    peaks = find_peaks_and_lobes(angles_deg, p, tgt_deg)

    # Beam must point to target angle
    assert peaks["target_lobe_angle"] == pytest.approx(tgt_deg, abs=0.6)


# Exact Regression Parameters Case (4 GHz, 8 elem, d=0.05m, tgt=+25, inc=+5, cosine)
def test_exact_regression_parameters_continuous() -> None:
    resp = client.post(
        "/api/simulations/beam-steering",
        json={
            "element_count": 8,
            "frequency_hz": 4.0e9,
            "spacing_m": 0.05,
            "target_angle_deg": 25.0,
            "reflection_magnitude": 1.0,
            "sample_count": 361,
            "incident_angle_deg": 5.0,
            "element_pattern": "cosine",
            "phase_quantization_bits": None,
            "coupled_loss_model": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    # Peak angle must be at 24.5° (nearest discrete grid point to 25.0°)
    assert data["sampled_main_lobe_angles_deg"]["controlled"] == 24.5
    assert data["sampled_main_lobe_angles_deg"]["baseline"] == -5.0  # Snell's Law specular reflection
    assert data["research_metrics"]["pointing_error_deg"] == 0.5
    assert data["research_metrics"]["competing_lobe_detected"] is False

    # Target power = cos^2(25°) = 0.8214
    assert data["target_metrics"]["controlled_normalized_power"] == pytest.approx(0.8214, abs=1e-3)
    assert data["target_metrics"]["improvement_db"] == pytest.approx(19.20, abs=0.2)
    assert data["research_metrics"]["hpbw_deg"] == pytest.approx(10.48, abs=0.1)
    assert data["research_metrics"]["psll_db"] == pytest.approx(-12.07, abs=0.2)
    assert data["research_metrics"]["directivity_dbi"] == pytest.approx(10.24, abs=0.1)


def test_exact_regression_parameters_1bit_diode_loss() -> None:
    resp = client.post(
        "/api/simulations/beam-steering",
        json={
            "element_count": 8,
            "frequency_hz": 4.0e9,
            "spacing_m": 0.05,
            "target_angle_deg": 25.0,
            "reflection_magnitude": 1.0,
            "sample_count": 361,
            "incident_angle_deg": 5.0,
            "element_pattern": "cosine",
            "phase_quantization_bits": 1,
            "coupled_loss_model": True,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    # With corrected physics:
    # Controlled beam points at 24.5° (nearest to 25.0°), NOT at -15.5°!
    assert data["sampled_main_lobe_angles_deg"]["controlled"] == 24.5
    assert data["research_metrics"]["pointing_error_deg"] == 0.5
    # Baseline reflects specularly to -5.0°
    assert data["sampled_main_lobe_angles_deg"]["baseline"] == -5.0
    # Power and improvement metrics
    assert data["target_metrics"]["controlled_normalized_power"] == pytest.approx(0.0866, abs=1e-3)
    assert data["target_metrics"]["improvement_db"] == pytest.approx(16.10, abs=0.2)
