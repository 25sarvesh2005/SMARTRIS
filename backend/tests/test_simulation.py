import numpy as np
import pytest

from app.config import SPEED_OF_LIGHT_M_S
from app.simulation import (
    array_factor,
    element_positions_m,
    normalized_power,
    power_to_db,
    sampled_main_lobe_angle_deg,
    steering_phases_rad,
    wavelength_m,
    wavenumber_rad_m,
    wrap_phase_rad,
)


def test_wavelength_scales_inverse_to_frequency() -> None:
    wavelength = wavelength_m(3.0e9)
    assert wavelength == pytest.approx(SPEED_OF_LIGHT_M_S / 3.0e9)
    assert wavelength_m(6.0e9) == pytest.approx(wavelength / 2.0)


def test_positions_start_at_zero_and_use_spacing() -> None:
    assert np.allclose(element_positions_m(4, 0.1), [0.0, 0.1, 0.2, 0.3])


def test_wrapped_phase_interval_and_phasor_equivalence() -> None:
    wrapped = wrap_phase_rad(np.array([-np.pi, np.pi, 3.0 * np.pi]))
    assert np.all(wrapped >= -np.pi)
    assert np.all(wrapped < np.pi)
    assert np.allclose(np.exp(1j * wrapped), np.exp(1j * np.array([-np.pi, np.pi, 3.0 * np.pi])))


def test_broadside_steering_has_zero_phase_progression() -> None:
    positions = element_positions_m(4, 0.05)
    phases = steering_phases_rad(positions, wavenumber_rad_m(3.0e9), 0.0)
    assert np.allclose(phases, 0.0)


def test_coherent_array_factor_is_summed_before_power() -> None:
    positions = element_positions_m(4, 0.05)
    array_factor_values = array_factor([0.0], positions, np.zeros(4), wavenumber_rad_m(3.0e9), 1.0)
    assert normalized_power(array_factor_values)[0] == pytest.approx(1.0)


def test_baseline_power_matches_independent_uniform_array_closed_form() -> None:
    element_count = 8
    spacing_m = 0.04
    reflection_magnitude = 0.7
    angle_deg = 20.0
    wavenumber = wavenumber_rad_m(3.0e9)
    positions = element_positions_m(element_count, spacing_m)
    calculated = normalized_power(
        array_factor([np.deg2rad(angle_deg)], positions, np.zeros(element_count), wavenumber, reflection_magnitude)
    )[0]
    psi = wavenumber * spacing_m * np.sin(np.deg2rad(angle_deg))
    expected = reflection_magnitude**2 * (np.sin(element_count * psi / 2.0) / (element_count * np.sin(psi / 2.0)))**2
    assert calculated == pytest.approx(expected)


def test_ideal_steering_reaches_the_expected_normalized_peak() -> None:
    reflection_magnitude = 0.65
    positions = element_positions_m(8, 0.04)
    wavenumber = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(positions, wavenumber, 31.0)
    power = normalized_power(array_factor([np.deg2rad(31.0)], positions, phases, wavenumber, reflection_magnitude))[0]
    assert power == pytest.approx(reflection_magnitude**2)


def test_zero_reflection_has_zero_power_and_finite_db_floor() -> None:
    positions = element_positions_m(2, 0.05)
    fields = array_factor([0.0], positions, np.zeros(2), wavenumber_rad_m(3.0e9), 0.0)
    power = normalized_power(fields)
    assert power[0] == 0.0
    assert np.isfinite(power_to_db(power)[0])
    assert sampled_main_lobe_angle_deg(np.array([-90.0, 0.0, 90.0]), power.repeat(3)) is None


def test_bistatic_steering_with_oblique_incidence() -> None:
    positions = element_positions_m(8, 0.05)
    wavenumber = wavenumber_rad_m(3.0e9)
    target_angle = 35.0
    incident_angle = -20.0
    phases = steering_phases_rad(positions, wavenumber, target_angle, incident_angle_deg=incident_angle)
    # Peak must occur at target_angle for incident_angle
    angles_deg = np.linspace(-90, 90, 361)
    power = normalized_power(
        array_factor(
            np.deg2rad(angles_deg), positions, phases, wavenumber, 1.0, incident_angle_deg=incident_angle
        )
    )
    peak = angles_deg[np.argmax(power)]
    assert peak == pytest.approx(target_angle, abs=0.6)
    target_power = normalized_power(
        array_factor(
            [np.deg2rad(target_angle)], positions, phases, wavenumber, 1.0, incident_angle_deg=incident_angle
        )
    )[0]
    assert target_power == pytest.approx(1.0)


def test_element_pattern_attenuates_grazing_angles() -> None:
    from app.simulation import element_pattern_gain
    angles = np.deg2rad(np.array([0.0, 60.0, 90.0]))
    iso = element_pattern_gain(angles, "isotropic")
    cos_p = element_pattern_gain(angles, "cosine")
    assert np.allclose(iso, [1.0, 1.0, 1.0])
    assert cos_p[0] == pytest.approx(1.0)
    assert cos_p[1] == pytest.approx(0.5)
    assert cos_p[2] == pytest.approx(0.0)


def test_phase_quantization() -> None:
    from app.simulation import quantize_phases_rad
    # 2-bit quantization has states at [-pi, -pi/2, 0, pi/2]
    raw = np.array([0.1, 1.5, -1.4, 3.0])
    quantized = quantize_phases_rad(raw, bits=2)
    # All quantized phases must be integer multiples of pi/2
    multiples = quantized / (np.pi / 2.0)
    assert np.allclose(multiples, np.round(multiples))


def test_research_metrics_hpbw_and_directivity() -> None:
    from app.simulation import calculate_directivity_dbi, calculate_hpbw_deg, calculate_psll_db
    angles = np.linspace(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles)
    positions = element_positions_m(8, 0.05)
    wavenumber = wavenumber_rad_m(3.0e9)
    # Broadside beam with d = lambda/2
    phases = np.zeros(8)
    power = normalized_power(array_factor(angles_rad, positions, phases, wavenumber, 1.0))
    hpbw = calculate_hpbw_deg(angles, power)
    assert hpbw is not None
    # For 8-element ULA, HPBW ~ 0.886 * (lambda/Nd) * (180/pi) ~ 12.7 deg
    assert 11.0 <= hpbw <= 15.0
    psll = calculate_psll_db(angles, power)
    assert psll is not None
    # Theoretical uniform array SLL is ~ -13.26 dB
    assert -14.5 <= psll <= -12.0
    directivity = calculate_directivity_dbi(angles_rad, power)
    assert directivity is not None
    # Broadside D ~ 10*log10(8) ~ 9.0 dBi
    assert 7.5 <= directivity <= 10.5


def test_audit_1_wavelength_and_single_frequency_conversion() -> None:
    f = 3.0e9
    lam = wavelength_m(f)
    assert lam == pytest.approx(299_792_458.0 / 3.0e9, rel=1e-9)
    assert round(lam, 4) == 0.0999
    k = wavenumber_rad_m(f)
    assert k == pytest.approx(2.0 * np.pi / lam, rel=1e-9)


def test_audit_2_half_wavelength_spacing() -> None:
    f = 3.0e9
    lam = wavelength_m(f)
    d = 0.05
    spacing_ratio = d / lam
    assert 0.49 <= spacing_ratio <= 0.51
    positions = element_positions_m(8, d)
    expected_positions = np.arange(8) * 0.05
    assert np.allclose(positions, expected_positions)


def test_audit_3_broadside_beam_at_zero_degrees() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 0.0)
    assert np.allclose(phases, 0.0)
    angles = np.linspace(-90.0, 90.0, 361)
    power = normalized_power(array_factor(np.deg2rad(angles), pos, phases, k, 1.0))
    peak_angle = sampled_main_lobe_angle_deg(angles, power)
    assert peak_angle == 0.0
    assert power[180] == pytest.approx(1.0)


def test_audit_4_steering_plus_and_minus_25_degrees_symmetry() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    angles = np.linspace(-90.0, 90.0, 361)

    phases_pos = steering_phases_rad(pos, k, 25.0)
    power_pos = normalized_power(array_factor(np.deg2rad(angles), pos, phases_pos, k, 1.0))
    peak_pos = sampled_main_lobe_angle_deg(angles, power_pos)
    assert peak_pos == pytest.approx(25.0, abs=0.5)

    phases_neg = steering_phases_rad(pos, k, -25.0)
    power_neg = normalized_power(array_factor(np.deg2rad(angles), pos, phases_neg, k, 1.0))
    peak_neg = sampled_main_lobe_angle_deg(angles, power_neg)
    assert peak_neg == pytest.approx(-25.0, abs=0.5)

    assert np.allclose(power_pos, power_neg[::-1], atol=1e-6)


def test_audit_5_unsteered_uniform_array_symmetry_and_dirichlet() -> None:
    element_count = 8
    d = 0.05
    k = wavenumber_rad_m(3.0e9)
    pos = element_positions_m(element_count, d)
    angles = np.linspace(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles)
    power = normalized_power(array_factor(angles_rad, pos, np.zeros(element_count), k, 1.0))

    assert np.allclose(power, power[::-1], atol=1e-7)

    psi = k * d * np.sin(angles_rad)
    with np.errstate(divide="ignore", invalid="ignore"):
        dirichlet = (
            np.where(
                np.abs(psi) < 1e-9,
                1.0,
                np.sin(element_count * psi / 2.0) / (element_count * np.sin(psi / 2.0)),
            )
            ** 2
        )
    assert np.allclose(power, dirichlet, atol=1e-7)


def test_audit_6_agreement_between_power_db_and_field_db() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    angles = np.linspace(-90.0, 90.0, 361)
    phases = steering_phases_rad(pos, k, 25.0)
    fields = array_factor(np.deg2rad(angles), pos, phases, k, 1.0)
    power = normalized_power(fields)

    power_db = power_to_db(power)
    mag_db = 20.0 * np.log10(np.maximum(np.abs(fields), 1.0e-6))
    assert np.allclose(power_db, mag_db, atol=1e-5)


def test_audit_7_hpbw_reproducibility_and_boundary_handling() -> None:
    from scipy.optimize import brentq
    from app.simulation import calculate_hpbw_deg

    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 25.0)
    angles = np.linspace(-90.0, 90.0, 361)
    power = normalized_power(array_factor(np.deg2rad(angles), pos, phases, k, 1.0))

    hpbw = calculate_hpbw_deg(angles, power)
    assert hpbw == 14.15

    theta0 = np.deg2rad(25.0)
    kd = k * 0.05

    def af_diff(th: float) -> float:
        psi = kd * (np.sin(th) - np.sin(theta0))
        val = np.sin(4.0 * psi) / (8.0 * np.sin(psi / 2.0))
        return val**2 - 0.5

    th_l = np.rad2deg(brentq(af_diff, np.deg2rad(15.0), np.deg2rad(24.9)))
    th_r = np.rad2deg(brentq(af_diff, np.deg2rad(25.1), np.deg2rad(35.0)))
    exact_continuous_hpbw = th_r - th_l
    assert exact_continuous_hpbw == pytest.approx(14.1464, abs=0.01)
    assert round(exact_continuous_hpbw, 2) == 14.15

    # Safe handling of peaks close to grid boundaries
    phases_boundary = steering_phases_rad(pos, k, 88.0)
    power_boundary = normalized_power(array_factor(np.deg2rad(angles), pos, phases_boundary, k, 1.0))
    assert calculate_hpbw_deg(angles, power_boundary) is None


def test_audit_8_peak_sidelobe_detection_excluding_main_lobe() -> None:
    from app.simulation import calculate_psll_db

    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 25.0)
    angles = np.linspace(-90.0, 90.0, 361)
    power = normalized_power(array_factor(np.deg2rad(angles), pos, phases, k, 1.0))

    psll = calculate_psll_db(angles, power)
    assert psll == -12.8

    expected_psll_db = 10.0 * np.log10(0.052513)
    assert psll == pytest.approx(expected_psll_db, abs=0.05)
    assert psll < -12.0


def test_audit_9_safe_handling_of_zero_power_and_near_zero_baseline() -> None:
    from app.simulation import (
        calculate_directivity_dbi,
        calculate_hpbw_deg,
        calculate_psll_db,
        improvement_db,
    )

    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    angles = np.linspace(-90.0, 90.0, 361)

    power_zero = normalized_power(array_factor(np.deg2rad(angles), pos, np.zeros(8), k, 0.0))
    assert np.all(power_zero == 0.0)

    db = power_to_db(power_zero)
    assert np.all(np.isfinite(db))
    assert np.all(db == -120.0)

    assert sampled_main_lobe_angle_deg(angles, power_zero) is None
    assert calculate_hpbw_deg(angles, power_zero) is None
    assert calculate_psll_db(angles, power_zero) is None
    assert calculate_directivity_dbi(np.deg2rad(angles), power_zero) is None

    assert improvement_db(1.0, 0.0) is None
    assert improvement_db(1.0, 1.0e-13) is None
    assert improvement_db(1.0, 1.0) == pytest.approx(0.0)


def test_audit_10_target_improvement_metric_distinction_and_directivity() -> None:
    from app.simulation import calculate_directivity_dbi, directional_power, improvement_db

    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 25.0)

    p_steered_25 = directional_power(25.0, pos, phases, k, 1.0)
    p_baseline_25 = directional_power(25.0, pos, np.zeros(8), k, 1.0)

    assert p_steered_25 == pytest.approx(1.0)
    assert p_baseline_25 == pytest.approx(0.02792, abs=1e-4)
    delta_p = improvement_db(p_steered_25, p_baseline_25)
    assert delta_p is not None
    assert round(delta_p, 2) == 15.54

    angles = np.linspace(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles)
    power_steered = normalized_power(array_factor(angles_rad, pos, phases, k, 1.0))
    d_steered = calculate_directivity_dbi(angles_rad, power_steered)
    assert d_steered == 9.03

    power_broadside = normalized_power(array_factor(angles_rad, pos, np.zeros(8), k, 1.0))
    d_broadside = calculate_directivity_dbi(angles_rad, power_broadside)
    assert d_broadside == 9.03


def test_audit_11_parameter_variations_frequency_element_count_spacing() -> None:
    from app.simulation import calculate_directivity_dbi, calculate_hpbw_deg

    k3 = wavenumber_rad_m(3.0e9)
    angles = np.linspace(-90.0, 90.0, 361)
    angles_rad = np.deg2rad(angles)

    pos8 = element_positions_m(8, 0.05)
    pos16 = element_positions_m(16, 0.05)

    p8 = normalized_power(array_factor(angles_rad, pos8, np.zeros(8), k3, 1.0))
    p16 = normalized_power(array_factor(angles_rad, pos16, np.zeros(16), k3, 1.0))

    hpbw8 = calculate_hpbw_deg(angles, p8)
    hpbw16 = calculate_hpbw_deg(angles, p16)
    assert hpbw8 is not None and hpbw16 is not None
    assert hpbw16 == pytest.approx(hpbw8 / 2.0, abs=1.0)

    d8 = calculate_directivity_dbi(angles_rad, p8)
    d16 = calculate_directivity_dbi(angles_rad, p16)
    assert d8 == 9.03
    assert d16 == pytest.approx(10.0 * np.log10(16), abs=0.05)


def test_audit_12_reflection_magnitude_power_scaling() -> None:
    pos = element_positions_m(8, 0.05)
    k = wavenumber_rad_m(3.0e9)
    phases = steering_phases_rad(pos, k, 25.0)
    angles = np.linspace(-90.0, 90.0, 361)

    for gamma in [1.0, 0.7071, 0.5, 0.2]:
        p = normalized_power(array_factor(np.deg2rad(angles), pos, phases, k, gamma))
        peak_p = float(np.max(p))
        assert peak_p == pytest.approx(gamma**2, rel=1e-3)


