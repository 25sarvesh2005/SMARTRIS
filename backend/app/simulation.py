"""Numerical functions for SmartRIS's idealized linear array-factor model."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from .config import DB_FLOOR_POWER, IMPROVEMENT_BASELINE_FLOOR, SPEED_OF_LIGHT_M_S


def _finite_array(values: Iterable[float] | np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain one or more finite values.")
    return array


def wavelength_m(frequency_hz: float) -> float:
    """Return free-space wavelength for a positive, finite frequency."""
    if not np.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive and finite.")
    return float(SPEED_OF_LIGHT_M_S / frequency_hz)


def wavenumber_rad_m(frequency_hz: float) -> float:
    """Return free-space wavenumber in radians per metre."""
    return float(2.0 * np.pi / wavelength_m(frequency_hz))


def element_positions_m(element_count: int, spacing_m: float) -> np.ndarray:
    """Return positions x_n = n * d for a uniform linear array."""
    if element_count < 1:
        raise ValueError("element_count must be at least one.")
    if not np.isfinite(spacing_m) or spacing_m <= 0:
        raise ValueError("spacing_m must be positive and finite.")
    return np.arange(element_count, dtype=float) * spacing_m


def degrees_to_radians(degrees: float | np.ndarray) -> np.ndarray:
    return np.deg2rad(_finite_array(degrees, "degrees"))


def radians_to_degrees(radians: float | np.ndarray) -> np.ndarray:
    return np.rad2deg(_finite_array(radians, "radians"))


def wrap_phase_rad(phases_rad: Iterable[float] | np.ndarray) -> np.ndarray:
    """Wrap finite phase angles into the documented [-pi, pi) interval."""
    phases = _finite_array(phases_rad, "phases_rad")
    return (phases + np.pi) % (2.0 * np.pi) - np.pi


def angular_grid_deg(start_deg: float, stop_deg: float, sample_count: int) -> np.ndarray:
    if not np.isfinite(start_deg) or not np.isfinite(stop_deg) or start_deg >= stop_deg:
        raise ValueError("angle_start_deg must be finite and less than angle_stop_deg.")
    if sample_count < 2:
        raise ValueError("sample_count must be at least two.")
    return np.linspace(start_deg, stop_deg, sample_count, dtype=float)


def quantize_phases_rad(phases_rad: Iterable[float] | np.ndarray, bits: int) -> np.ndarray:
    """Discretize continuous phase values to 2^bits uniform states in [-pi, pi)."""
    phases = _finite_array(phases_rad, "phases_rad")
    if bits < 1 or bits > 8:
        raise ValueError("bits must be between 1 and 8.")
    step = 2.0 * np.pi / (2**bits)
    quantized = np.round(phases / step) * step
    return wrap_phase_rad(quantized)


def element_pattern_gain(angles_rad: np.ndarray, pattern_type: str = "isotropic") -> np.ndarray:
    """Calculate field magnitude pattern for individual RIS unit cells."""
    if pattern_type == "isotropic":
        return np.ones_like(angles_rad, dtype=float)
    if pattern_type == "cosine":
        return np.maximum(0.0, np.cos(angles_rad))
    if pattern_type == "cosine_squared":
        return np.maximum(0.0, np.cos(angles_rad) ** 2)
    raise ValueError(f"Unknown element pattern type: {pattern_type}")


def diode_reflection_loss(
    phases_rad: np.ndarray, beta_min: float = 0.2, phi_0: float = 0.0, alpha: float = 1.6
) -> np.ndarray:
    """Coupled phase-amplitude model: reflection amplitude loss as function of phase."""
    return (1.0 - beta_min) * (((np.sin(phases_rad - phi_0) + 1.0) / 2.0) ** alpha) + beta_min


def steering_phases_rad(
    positions_m: Iterable[float] | np.ndarray,
    wavenumber: float,
    target_angle_deg: float,
    incident_angle_deg: float = 0.0,
    bits: int | None = None,
) -> np.ndarray:
    """Return wrapped phi_n = -k*x_n*(sin(theta_target) - sin(theta_incident))."""
    positions = _finite_array(positions_m, "positions_m")
    if not np.isfinite(wavenumber) or wavenumber <= 0:
        raise ValueError("wavenumber must be positive and finite.")
    if not np.isfinite(target_angle_deg):
        raise ValueError("target_angle_deg must be finite.")
    if not np.isfinite(incident_angle_deg):
        raise ValueError("incident_angle_deg must be finite.")
    raw_phases = -wavenumber * positions * (
        np.sin(np.deg2rad(target_angle_deg)) - np.sin(np.deg2rad(incident_angle_deg))
    )
    wrapped = wrap_phase_rad(raw_phases)
    if bits is not None:
        return quantize_phases_rad(wrapped, bits)
    return wrapped


def array_factor(
    angles_rad: Iterable[float] | np.ndarray,
    positions_m: Iterable[float] | np.ndarray,
    phases_rad: Iterable[float] | np.ndarray,
    wavenumber: float,
    reflection_magnitude: float,
    amplitudes: Iterable[float] | np.ndarray | None = None,
    incident_angle_deg: float = 0.0,
    element_pattern: str = "isotropic",
    coupled_loss_model: bool = False,
) -> np.ndarray:
    """Compute AF(theta) with optional bistatic incidence, element factor, and diode loss."""
    angles = _finite_array(angles_rad, "angles_rad").reshape(-1)
    positions = _finite_array(positions_m, "positions_m").reshape(-1)
    phases = _finite_array(phases_rad, "phases_rad").reshape(-1)
    if positions.size != phases.size:
        raise ValueError("positions_m and phases_rad must have the same length.")
    if not np.isfinite(wavenumber) or wavenumber <= 0:
        raise ValueError("wavenumber must be positive and finite.")
    if not np.isfinite(reflection_magnitude) or not 0.0 <= reflection_magnitude <= 1.0:
        raise ValueError("reflection_magnitude must be finite and within [0, 1].")
    if amplitudes is None:
        weights = np.ones(positions.size, dtype=float)
    else:
        weights = _finite_array(amplitudes, "amplitudes").reshape(-1)
        if weights.size != positions.size or np.any(weights < 0):
            raise ValueError("amplitudes must be nonnegative and match the element count.")

    elem_beta = weights * reflection_magnitude
    if coupled_loss_model:
        elem_beta = elem_beta * diode_reflection_loss(phases)

    spatial_phase = wavenumber * positions[None, :] * (
        np.sin(angles)[:, None] - np.sin(np.deg2rad(incident_angle_deg))
    )
    phase_terms = spatial_phase + phases[None, :]
    field = elem_beta[None, :] * np.exp(1j * phase_terms)
    af = np.sum(field, axis=1) / positions.size
    if element_pattern != "isotropic":
        ep = element_pattern_gain(angles, element_pattern)
        return af * ep
    return af


def normalized_power(array_factor_values: Iterable[complex] | np.ndarray) -> np.ndarray:
    values = np.asarray(array_factor_values, dtype=complex)
    if values.size == 0 or not np.all(np.isfinite(values.real)) or not np.all(np.isfinite(values.imag)):
        raise ValueError("array_factor_values must be finite and non-empty.")
    return np.abs(values) ** 2


def power_to_db(power: Iterable[float] | np.ndarray, floor: float = DB_FLOOR_POWER) -> np.ndarray:
    powers = _finite_array(power, "power")
    if np.any(powers < 0):
        raise ValueError("power cannot be negative.")
    if not np.isfinite(floor) or floor <= 0:
        raise ValueError("floor must be positive and finite.")
    return 10.0 * np.log10(np.maximum(powers, floor))


def directional_power(
    angle_deg: float,
    positions_m: Iterable[float] | np.ndarray,
    phases_rad: Iterable[float] | np.ndarray,
    wavenumber: float,
    reflection_magnitude: float,
    incident_angle_deg: float = 0.0,
    element_pattern: str = "isotropic",
    coupled_loss_model: bool = False,
) -> float:
    value = array_factor(
        np.asarray([np.deg2rad(angle_deg)]),
        positions_m,
        phases_rad,
        wavenumber,
        reflection_magnitude,
        incident_angle_deg=incident_angle_deg,
        element_pattern=element_pattern,
        coupled_loss_model=coupled_loss_model,
    )
    return float(normalized_power(value)[0])


def sampled_main_lobe_angle_deg(angles_deg: np.ndarray, power: np.ndarray) -> float | None:
    """Return the maximum sampled direction, unless no reflected field exists."""
    if power.size == 0 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    return float(angles_deg[int(np.argmax(power))])


def improvement_db(controlled_power: float, baseline_power: float) -> float | None:
    """Return a finite relative improvement, or None for a near-zero baseline."""
    if baseline_power <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    return float(10.0 * np.log10(controlled_power / baseline_power))


def calculate_hpbw_deg(angles_deg: np.ndarray, power: np.ndarray) -> float | None:
    """Calculate Half-Power Beamwidth (-3 dB width) of the main lobe in degrees."""
    if power.size < 3 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    peak_idx = int(np.argmax(power))
    peak_power = float(power[peak_idx])
    half_power = peak_power * 0.5

    left_angle = float(angles_deg[0])
    for i in range(peak_idx, 0, -1):
        if power[i - 1] <= half_power:
            p1, p2 = float(power[i - 1]), float(power[i])
            a1, a2 = float(angles_deg[i - 1]), float(angles_deg[i])
            if p2 != p1:
                left_angle = a1 + (half_power - p1) / (p2 - p1) * (a2 - a1)
            else:
                left_angle = a1
            break

    right_angle = float(angles_deg[-1])
    for i in range(peak_idx, power.size - 1):
        if power[i + 1] <= half_power:
            p1, p2 = float(power[i]), float(power[i + 1])
            a1, a2 = float(angles_deg[i]), float(angles_deg[i + 1])
            if p2 != p1:
                right_angle = a1 + (half_power - p1) / (p2 - p1) * (a2 - a1)
            else:
                right_angle = a1
            break

    hpbw = float(right_angle - left_angle)
    return round(hpbw, 2) if hpbw > 0 else None


def calculate_psll_db(angles_deg: np.ndarray, power: np.ndarray) -> float | None:
    """Calculate Peak Sidelobe Level (PSLL) in dB relative to the main lobe."""
    if power.size < 5 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    peak_idx = int(np.argmax(power))
    peak_power = float(power[peak_idx])

    left_null = 0
    for i in range(peak_idx - 1, 0, -1):
        if power[i] <= power[i - 1] and power[i] <= power[i + 1]:
            left_null = i
            break

    right_null = power.size - 1
    for i in range(peak_idx + 1, power.size - 1):
        if power[i] <= power[i - 1] and power[i] <= power[i + 1]:
            right_null = i
            break

    sidelobe_powers = []
    if left_null > 0:
        sidelobe_powers.append(float(np.max(power[:left_null])))
    if right_null < power.size - 1:
        sidelobe_powers.append(float(np.max(power[right_null + 1:])))

    if not sidelobe_powers:
        return None

    max_sidelobe = max(sidelobe_powers)
    if max_sidelobe <= IMPROVEMENT_BASELINE_FLOOR:
        return None

    psll = 10.0 * np.log10(max_sidelobe / peak_power)
    return round(float(psll), 2)


def calculate_directivity_dbi(angles_rad: np.ndarray, power: np.ndarray) -> float | None:
    """Estimate 1D array directivity in dBi via trapezoidal integration over visible angles."""
    if power.size < 5 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    integrand = power * np.cos(angles_rad)
    integral = float(np.trapezoid(integrand, angles_rad))
    if integral <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    directivity_linear = 2.0 * float(np.max(power)) / integral
    if directivity_linear < 1.0:
        directivity_linear = 1.0
    return round(float(10.0 * np.log10(directivity_linear)), 2)


