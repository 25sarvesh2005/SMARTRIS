import numpy as np

from app.optimization import coordinate_search, tradeoff_objective
from app.simulation import element_positions_m, wavenumber_rad_m


def test_coordinate_search_is_deterministic_and_bounded() -> None:
    kwargs = dict(
        initial_phases_rad=np.zeros(4),
        positions_m=element_positions_m(4, 0.05),
        wavenumber=wavenumber_rad_m(3.0e9),
        reflection_magnitude=1.0,
        receiver_angle_deg=25.0,
        observation_angle_deg=-20.0,
        penalty=0.5,
        max_evaluations=100,
    )
    first = coordinate_search(**kwargs)
    second = coordinate_search(**kwargs)
    assert first.evaluation_count <= 100
    assert np.allclose(first.phases_rad, second.phases_rad)
    assert first.final_objective == second.final_objective


def test_reported_objective_matches_direct_calculation() -> None:
    positions = element_positions_m(4, 0.05)
    result = coordinate_search(
        initial_phases_rad=np.zeros(4), positions_m=positions, wavenumber=wavenumber_rad_m(3.0e9),
        reflection_magnitude=1.0, receiver_angle_deg=20.0, observation_angle_deg=-30.0,
        penalty=0.25, max_evaluations=50,
    )
    objective, _, _ = tradeoff_objective(
        result.phases_rad, positions, wavenumber_rad_m(3.0e9), 1.0, 20.0, -30.0, 0.25
    )
    assert result.final_objective == objective

