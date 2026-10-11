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


