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


def incident_phase_rad(
    positions_m: Iterable[float] | np.ndarray,
    wavenumber: float,
    incident_angle_deg: float = 0.0,
) -> np.ndarray:
    """Return spatial phase of an incident plane wave arriving from incident_angle_deg.
    
    A plane wave arriving from angle theta_i (measured from broadside normal toward +x)
    advances along the array elements at x_n with spatial phase:
        psi_inc(x_n) = +k * x_n * sin(theta_i)
    """
    positions = _finite_array(positions_m, "positions_m")
    if not np.isfinite(wavenumber) or wavenumber <= 0:
        raise ValueError("wavenumber must be positive and finite.")
    if not np.isfinite(incident_angle_deg):
        raise ValueError("incident_angle_deg must be finite.")
    return wavenumber * positions * np.sin(np.deg2rad(incident_angle_deg))


def steering_phases_rad(
    positions_m: Iterable[float] | np.ndarray,
    wavenumber: float,
    target_angle_deg: float,
    incident_angle_deg: float = 0.0,
    bits: int | None = None,
) -> np.ndarray:
    """Return programmed RIS phase shift Phi_n to steer reflection to target_angle_deg.
    
    For a wave arriving from incident_angle_deg, each element at x_n has incident phase
    +k*x_n*sin(theta_i). To steer outgoing far-field reflection to target_angle_deg,
    the element must be programmed with:
        Phi_n = -k * x_n * (sin(theta_target) + sin(theta_incident))
    so that total phase in direction theta_target cancels to zero.
    """
    positions = _finite_array(positions_m, "positions_m")
    if not np.isfinite(wavenumber) or wavenumber <= 0:
        raise ValueError("wavenumber must be positive and finite.")
    if not np.isfinite(target_angle_deg):
        raise ValueError("target_angle_deg must be finite.")
    if not np.isfinite(incident_angle_deg):
        raise ValueError("incident_angle_deg must be finite.")
    raw_phases = -wavenumber * positions * (
        np.sin(np.deg2rad(target_angle_deg)) + np.sin(np.deg2rad(incident_angle_deg))
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
    """Compute far-field E(theta) with physical incident phase, element factor, and diode loss.
    
    Each element n at x_n has total field phase:
        phi_total,n = psi_inc(x_n) + phases_rad[n] = k * x_n * sin(theta_i) + phases_rad[n]
    where phases_rad is the programmed RIS phase (0 for unprogrammed baseline).
    
    The far-field observation phase in direction theta is +k * x_n * sin(theta).
    For unprogrammed baseline (phases_rad = 0), constructive summation occurs when
    sin(theta) + sin(theta_i) = 0, giving specular reflection at theta = -theta_i.
    """
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

    inc_phase = incident_phase_rad(positions, wavenumber, incident_angle_deg)
    total_element_phase = inc_phase + phases

    spatial_phase = wavenumber * positions[None, :] * np.sin(angles)[:, None]
    phase_terms = spatial_phase + total_element_phase[None, :]
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
    """Return a finite relative improvement, or None for a near-zero baseline or controlled power."""
    if baseline_power <= IMPROVEMENT_BASELINE_FLOOR or controlled_power <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    return float(10.0 * np.log10(controlled_power / baseline_power))


def find_peaks_and_lobes(
    angles_deg: np.ndarray, power: np.ndarray, target_angle_deg: float | None = None
) -> dict:
    """Identify local maxima, global peak, and target-directed lobe with competing lobe detection."""
    if power.size < 3 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return {
            "global_peak_angle": None,
            "global_peak_power": 0.0,
            "global_peak_idx": None,
            "target_lobe_angle": None,
            "target_lobe_power": 0.0,
            "target_lobe_idx": None,
            "competing_lobe_present": False,
        }

    local_peaks: list[tuple[int, float, float]] = []
    for i in range(1, power.size - 1):
        if power[i] > power[i - 1] and power[i] >= power[i + 1]:
            local_peaks.append((i, float(angles_deg[i]), float(power[i])))

    if power.size > 1:
        if power[0] > power[1]:
            local_peaks.append((0, float(angles_deg[0]), float(power[0])))
        if power[-1] > power[-2]:
            local_peaks.append((power.size - 1, float(angles_deg[-1]), float(power[-1])))

    if not local_peaks:
        g_idx = int(np.argmax(power))
        local_peaks = [(g_idx, float(angles_deg[g_idx]), float(power[g_idx]))]

    global_idx, global_angle, global_power = max(local_peaks, key=lambda x: x[2])

    if target_angle_deg is not None:
        target_lobe = min(local_peaks, key=lambda x: abs(x[1] - target_angle_deg))
        target_idx, target_angle, target_power = target_lobe
    else:
        target_idx, target_angle, target_power = global_idx, global_angle, global_power

    competing_present = bool((global_idx != target_idx) and (global_power > target_power * 1.01))

    return {
        "global_peak_angle": global_angle,
        "global_peak_power": global_power,
        "global_peak_idx": global_idx,
        "target_lobe_angle": target_angle,
        "target_lobe_power": target_power,
        "target_lobe_idx": target_idx,
        "competing_lobe_present": competing_present,
    }


def calculate_hpbw_deg(
    angles_deg: np.ndarray, power: np.ndarray, peak_idx: int | None = None
) -> float | None:
    """Calculate Half-Power Beamwidth (-3 dB width) in degrees around a chosen peak (default: global peak).
    
    Identifies the main lobe around peak_idx (or global peak), finds the left and right -3.0103 dB
    (half-power, P_peak / 2) crossings with linear interpolation, and computes
    HPBW = theta_right - theta_left. Returns None if either crossing is outside
    the visible grid (boundary clipped) or if power is near zero.
    """
    if power.size < 3 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    if peak_idx is None:
        peak_idx = int(np.argmax(power))
    if not (0 <= peak_idx < power.size):
        return None

    peak_power = float(power[peak_idx])
    if peak_power <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    half_power = peak_power * 0.5

    left_angle: float | None = None
    for i in range(peak_idx, 0, -1):
        if power[i - 1] <= half_power:
            p1, p2 = float(power[i - 1]), float(power[i])
            a1, a2 = float(angles_deg[i - 1]), float(angles_deg[i])
            left_angle = a1 if p2 == p1 else a1 + (half_power - p1) / (p2 - p1) * (a2 - a1)
            break

    right_angle: float | None = None
    for i in range(peak_idx, power.size - 1):
        if power[i + 1] <= half_power:
            p1, p2 = float(power[i]), float(power[i + 1])
            a1, a2 = float(angles_deg[i]), float(angles_deg[i + 1])
            right_angle = a1 if p2 == p1 else a1 + (half_power - p1) / (p2 - p1) * (a2 - a1)
            break

    if left_angle is None or right_angle is None:
        return None

    hpbw = float(right_angle - left_angle)
    return round(hpbw, 2) if hpbw > 0 else None


def calculate_psll_db(
    angles_deg: np.ndarray, power: np.ndarray, main_lobe_idx: int | None = None
) -> float | None:
    """Calculate Peak Sidelobe Level (PSLL) in dB relative to the main lobe at main_lobe_idx.
    
    Excludes the principal main lobe by locating the first pattern nulls on the
    left and right of the main beam maximum. The peak sidelobe power is identified
    strictly outside these null boundaries, and PSLL is evaluated as:
        PSLL = 10 * log10(max(P_sidelobe) / P_main_peak)
    Returns None if no sidelobes are present outside the nulls or if power is near zero.
    """
    if power.size < 5 or float(np.max(power)) <= IMPROVEMENT_BASELINE_FLOOR:
        return None
    if main_lobe_idx is None:
        peak_idx = int(np.argmax(power))
    else:
        peak_idx = int(main_lobe_idx)
    if not (0 <= peak_idx < power.size):
        return None

    peak_power = float(power[peak_idx])
    if peak_power <= IMPROVEMENT_BASELINE_FLOOR:
        return None

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
    """Estimate 1D array-factor directivity in dBi via visible-space pattern integration.
    
    Assumes an idealized linear array of isotropic elements with axial symmetry
    around the array axis, where the 3D solid-angle radiation integral simplifies to:
        D = 4*pi*U_max / integral(4*pi, U(theta, phi) dOmega)
          = 2 * P_max / integral_{-pi/2}^{+pi/2} P(theta) * cos(theta) dtheta
    
    Note: For an 8-element uniform linear array with half-wavelength spacing (d = lambda/2),
    spatial harmonic orthogonality over visible u in [-1, 1] yields D = N = 8, or ~9.03 dBi.
    This is an idealized 1D array-factor directivity cut; it does not account for a 2D planar
    aperture, true 3D solid angle integration, or antenna efficiency losses.
    """
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


