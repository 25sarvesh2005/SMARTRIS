"""A deterministic, bounded coordinate-search exploration for SmartRIS."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .simulation import directional_power, wrap_phase_rad


@dataclass(frozen=True)
class OptimizationResult:
    phases_rad: np.ndarray
    initial_objective: float
    final_objective: float
    initial_receiver_power: float
    final_receiver_power: float
    initial_observation_power: float
    final_observation_power: float
    evaluation_count: int
    stop_reason: str
    constraint_status: str


def tradeoff_objective(
    phases_rad: np.ndarray,
    positions_m: np.ndarray,
    wavenumber: float,
    reflection_magnitude: float,
    receiver_angle_deg: float,
    observation_angle_deg: float,
    penalty: float,
) -> tuple[float, float, float]:
    receiver_power = directional_power(
        receiver_angle_deg, positions_m, phases_rad, wavenumber, reflection_magnitude
    )
    observation_power = directional_power(
        observation_angle_deg, positions_m, phases_rad, wavenumber, reflection_magnitude
    )
    return receiver_power - penalty * observation_power, receiver_power, observation_power


def coordinate_search(
    *,
    initial_phases_rad: np.ndarray,
    positions_m: np.ndarray,
    wavenumber: float,
    reflection_magnitude: float,
    receiver_angle_deg: float,
    observation_angle_deg: float,
    penalty: float,
    max_evaluations: int,
    observation_power_threshold: float | None = None,
) -> OptimizationResult:
    """Run explainable coordinate search; no claim of a global optimum is made."""
    if penalty < 0 or not np.isfinite(penalty):
        raise ValueError("penalty must be finite and nonnegative.")
    if max_evaluations < 1:
        raise ValueError("max_evaluations must be at least one.")
    if observation_power_threshold is not None and (
        not np.isfinite(observation_power_threshold) or observation_power_threshold < 0
    ):
        raise ValueError("observation_power_threshold must be finite and nonnegative.")

    current = wrap_phase_rad(initial_phases_rad)
    initial_objective, initial_receiver, initial_observation = tradeoff_objective(
        current, positions_m, wavenumber, reflection_magnitude, receiver_angle_deg, observation_angle_deg, penalty
    )
    evaluations = 1
    best_any = (current.copy(), initial_objective, initial_receiver, initial_observation)
    feasible = observation_power_threshold is None or initial_observation <= observation_power_threshold
    best_feasible = best_any if feasible else None
    step = np.pi / 2.0
    minimum_step = np.deg2rad(0.5)
    stop_reason = "evaluation_budget_exhausted"

    while evaluations < max_evaluations and step >= minimum_step:
        improved = False
        for index in range(current.size):
            for direction in (1.0, -1.0):
                if evaluations >= max_evaluations:
                    break
                candidate = current.copy()
                candidate[index] = wrap_phase_rad(np.asarray([candidate[index] + direction * step]))[0]
                objective, receiver, observation = tradeoff_objective(
                    candidate, positions_m, wavenumber, reflection_magnitude,
                    receiver_angle_deg, observation_angle_deg, penalty,
                )
                evaluations += 1
                if objective > best_any[1]:
                    best_any = (candidate.copy(), objective, receiver, observation)
                candidate_feasible = (
                    observation_power_threshold is None or observation <= observation_power_threshold
                )
                if candidate_feasible and (best_feasible is None or objective > best_feasible[1]):
                    best_feasible = (candidate.copy(), objective, receiver, observation)
                    current = candidate
                    improved = True
            if evaluations >= max_evaluations:
                break
        if not improved:
            step /= 2.0

    if evaluations < max_evaluations:
        stop_reason = "coordinate_step_converged"
    final = best_feasible if best_feasible is not None else best_any
    if observation_power_threshold is None:
        constraint_status = "not_applicable"
    elif best_feasible is None:
        constraint_status = "no_feasible_candidate_found_within_budget"
    elif final[3] <= observation_power_threshold:
        constraint_status = "satisfied"
    else:
        constraint_status = "not_satisfied"

    return OptimizationResult(
        phases_rad=final[0], initial_objective=float(initial_objective), final_objective=float(final[1]),
        initial_receiver_power=float(initial_receiver), final_receiver_power=float(final[2]),
        initial_observation_power=float(initial_observation), final_observation_power=float(final[3]),
        evaluation_count=evaluations, stop_reason=stop_reason, constraint_status=constraint_status,
    )

