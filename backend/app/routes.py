"""Thin HTTP routes that adapt validated schemas to numerical functions."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter

from . import config
from .optimization import coordinate_search
from .schemas import ArraySimulationRequest, BeamSteeringRequest, CustomPhasesRequest, TradeoffRequest
from .simulation import (
    angular_grid_deg,
    array_factor,
    calculate_directivity_dbi,
    calculate_hpbw_deg,
    calculate_psll_db,
    degrees_to_radians,
    directional_power,
    element_positions_m,
    improvement_db,
    normalized_power,
    power_to_db,
    radians_to_degrees,
    sampled_main_lobe_angle_deg,
    steering_phases_rad,
    wavelength_m,
    wavenumber_rad_m,
    wrap_phase_rad,
)

router = APIRouter(prefix="/api")


def _has_visible_steering_grating_lobe(
    spacing_m: float, wavelength: float, target_angle_deg: float
) -> bool:
    """Check whether a nonzero spatial-order replica is visible for this scan."""
    target_sine = float(np.sin(np.deg2rad(target_angle_deg)))
    wavelength_over_spacing = wavelength / spacing_m
    min_order = int(np.ceil((-1.0 - target_sine) / wavelength_over_spacing))
    max_order = int(np.floor((1.0 - target_sine) / wavelength_over_spacing))
    return any(order != 0 for order in range(min_order, max_order + 1))


def _warnings(
    request: ArraySimulationRequest, wavelength: float, steering_target_angle_deg: float | None = None
) -> list[str]:
    warnings: list[str] = []
    if steering_target_angle_deg is not None and _has_visible_steering_grating_lobe(
        request.spacing_m, wavelength, steering_target_angle_deg
    ):
        warnings.append(
            "This spacing and target angle produce a visible grating-lobe replica in the idealized model."
        )
    elif steering_target_angle_deg is None and request.spacing_m > wavelength / 2.0:
        warnings.append(
            "Element spacing exceeds half a wavelength; grating lobes may occur for some phase configurations."
        )
    if steering_target_angle_deg is not None and not (
        request.angle_start_deg <= steering_target_angle_deg <= request.angle_stop_deg
    ):
        warnings.append(
            "The target angle is outside the displayed angular grid; target metrics are evaluated directly."
        )
    if request.sample_count < 361:
        warnings.append(
            "Main-lobe angles are sampled-grid estimates; increase sample_count for a finer angular grid."
        )
    return warnings


def _base_result(
    request: ArraySimulationRequest, phases_rad: np.ndarray, steering_target_angle_deg: float | None = None
) -> dict:
    wavelength = wavelength_m(request.frequency_hz)
    wavenumber = wavenumber_rad_m(request.frequency_hz)
    positions = element_positions_m(request.element_count, request.spacing_m)
    angles_deg = angular_grid_deg(request.angle_start_deg, request.angle_stop_deg, request.sample_count)
    angles_rad = degrees_to_radians(angles_deg)
    pattern = normalized_power(
        array_factor(
            angles_rad,
            positions,
            phases_rad,
            wavenumber,
            request.reflection_magnitude,
            incident_angle_deg=request.incident_angle_deg,
            element_pattern=request.element_pattern,
            coupled_loss_model=request.coupled_loss_model,
        )
    )
    peak_angle = sampled_main_lobe_angle_deg(angles_deg, pattern)
    hpbw = calculate_hpbw_deg(angles_deg, pattern)
    psll = calculate_psll_db(angles_deg, pattern)
    directivity = calculate_directivity_dbi(angles_rad, pattern)
    pointing_error = None
    if steering_target_angle_deg is not None and peak_angle is not None:
        pointing_error = round(abs(peak_angle - steering_target_angle_deg), 2)

    return {
        "model_id": config.MODEL_ID,
        "configuration": request.model_dump(),
        "wavelength_m": wavelength,
        "wavenumber_rad_m": wavenumber,
        "element_positions_m": positions.tolist(),
        "phases_rad": phases_rad.tolist(),
        "phases_deg": radians_to_degrees(phases_rad).tolist(),
        "angles_deg": angles_deg.tolist(),
        "normalized_power": pattern.tolist(),
        "normalized_power_db": power_to_db(pattern).tolist(),
        "sampled_main_lobe_angle_deg": peak_angle,
        "hpbw_deg": hpbw,
        "psll_db": psll,
        "directivity_dbi": directivity,
        "pointing_error_deg": pointing_error,
        "warnings": _warnings(request, wavelength, steering_target_angle_deg),
        "limitations": [
            "Idealized linear array-factor model; this is not a full-wave electromagnetic simulation.",
            "Normalized directional power is not absolute received power, gain, scattering, or RCS.",
            "The model omits element patterns, mutual coupling, materials, and hardware effects.",
        ],
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": config.API_VERSION}


@router.get("/info")
def info() -> dict:
    return {
        "model_id": config.MODEL_ID,
        "api_version": config.API_VERSION,
        "normalization": "AF is normalized by element count; normalized directional power is |AF|^2.",
        "units": {"frequency": "Hz", "spacing": "m", "angles": "degrees", "phases": "radians/degrees"},
        "defaults": config.DEFAULT_BEAM_STEERING,
        "limits": {
            "element_count": [config.MIN_ELEMENT_COUNT, config.MAX_ELEMENT_COUNT],
            "frequency_hz": [config.MIN_FREQUENCY_HZ, config.MAX_FREQUENCY_HZ],
            "spacing_m": [config.MIN_SPACING_M, config.MAX_SPACING_M],
            "angles_deg": [config.MIN_ANGLE_DEG, config.MAX_ANGLE_DEG],
            "sample_count": [config.MIN_SAMPLE_COUNT, config.MAX_SAMPLE_COUNT],
            "max_evaluations": [config.MIN_OPTIMIZER_EVALUATIONS, config.MAX_OPTIMIZER_EVALUATIONS],
        },
        "limitations": [
            "This is an idealized array-factor model, not a validated RCS or full-wave solver.",
            "Optimization is deterministic exploratory coordinate search and does not guarantee a global optimum.",
        ],
    }


@router.post("/simulations/beam-steering")
def beam_steering(request: BeamSteeringRequest) -> dict:
    positions = element_positions_m(request.element_count, request.spacing_m)
    phases = steering_phases_rad(
        positions,
        wavenumber_rad_m(request.frequency_hz),
        request.target_angle_deg,
        incident_angle_deg=request.incident_angle_deg,
        bits=request.phase_quantization_bits,
    )
    baseline = _base_result(request, np.zeros(request.element_count, dtype=float))
    controlled = _base_result(request, phases, request.target_angle_deg)
    baseline_target_power = directional_power(
        request.target_angle_deg,
        positions,
        np.zeros(request.element_count, dtype=float),
        wavenumber_rad_m(request.frequency_hz),
        request.reflection_magnitude,
        incident_angle_deg=request.incident_angle_deg,
        element_pattern=request.element_pattern,
        coupled_loss_model=request.coupled_loss_model,
    )
    controlled_target_power = directional_power(
        request.target_angle_deg,
        positions,
        phases,
        wavenumber_rad_m(request.frequency_hz),
        request.reflection_magnitude,
        incident_angle_deg=request.incident_angle_deg,
        element_pattern=request.element_pattern,
        coupled_loss_model=request.coupled_loss_model,
    )
    return {
        "model_id": config.MODEL_ID,
        "configuration": request.model_dump(),
        "wavelength_m": controlled["wavelength_m"],
        "wavenumber_rad_m": controlled["wavenumber_rad_m"],
        "element_positions_m": controlled["element_positions_m"],
        "angles_deg": controlled["angles_deg"],
        "baseline_phases_rad": baseline["phases_rad"],
        "baseline_phases_deg": baseline["phases_deg"],
        "controlled_phases_rad": controlled["phases_rad"],
        "controlled_phases_deg": controlled["phases_deg"],
        "baseline_normalized_power": baseline["normalized_power"],
        "controlled_normalized_power": controlled["normalized_power"],
        "baseline_normalized_power_db": baseline["normalized_power_db"],
        "controlled_normalized_power_db": controlled["normalized_power_db"],
        "target_metrics": {
            "baseline_normalized_power": baseline_target_power,
            "controlled_normalized_power": controlled_target_power,
            "improvement_db": improvement_db(controlled_target_power, baseline_target_power),
        },
        "sampled_main_lobe_angles_deg": {
            "baseline": baseline["sampled_main_lobe_angle_deg"],
            "controlled": controlled["sampled_main_lobe_angle_deg"],
        },
        "research_metrics": {
            "hpbw_deg": controlled["hpbw_deg"],
            "psll_db": controlled["psll_db"],
            "directivity_dbi": controlled["directivity_dbi"],
            "pointing_error_deg": controlled["pointing_error_deg"],
        },
        "warnings": controlled["warnings"],
        "limitations": controlled["limitations"],
        "db_floor_power": config.DB_FLOOR_POWER,
    }


@router.post("/simulations/custom-phases")
def custom_phases(request: CustomPhasesRequest) -> dict:
    raw_phases = np.asarray(request.phase_values, dtype=float)
    phases = wrap_phase_rad(np.deg2rad(raw_phases) if request.phase_units == "degrees" else raw_phases)
    return _base_result(request, phases)


@router.post("/simulations/tradeoff")
def tradeoff(request: TradeoffRequest) -> dict:
    positions = element_positions_m(request.element_count, request.spacing_m)
    wavenumber = wavenumber_rad_m(request.frequency_hz)
    initial_phases = np.zeros(request.element_count, dtype=float)
    optimized = coordinate_search(
        initial_phases_rad=initial_phases,
        positions_m=positions,
        wavenumber=wavenumber,
        reflection_magnitude=request.reflection_magnitude,
        receiver_angle_deg=request.receiver_angle_deg,
        observation_angle_deg=request.observation_angle_deg,
        penalty=request.penalty,
        max_evaluations=request.max_evaluations,
        observation_power_threshold=request.observation_power_threshold,
    )
    initial = _base_result(request, initial_phases)
    final = _base_result(request, optimized.phases_rad)
    return {
        "model_id": config.MODEL_ID,
        "configuration": request.model_dump(),
        "initial": initial,
        "optimized": final,
        "algorithm": "deterministic coordinate search",
        "initial_objective": optimized.initial_objective,
        "final_objective": optimized.final_objective,
        "initial_receiver_power": optimized.initial_receiver_power,
        "final_receiver_power": optimized.final_receiver_power,
        "initial_observation_power": optimized.initial_observation_power,
        "final_observation_power": optimized.final_observation_power,
        "evaluation_count": optimized.evaluation_count,
        "stop_reason": optimized.stop_reason,
        "constraint_status": optimized.constraint_status,
        "scientific_note": "Observation power is a normalized directional array-factor proxy, not RCS.",
    }

