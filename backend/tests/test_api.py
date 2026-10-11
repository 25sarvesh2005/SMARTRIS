import math

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_info() -> None:
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/info").json()["model_id"] == "idealized-linear-array-factor-v1"


def test_beam_steering_returns_comparable_patterns() -> None:
    response = client.post("/api/simulations/beam-steering", json={"target_angle_deg": 25.0})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["angles_deg"]) == 361
    assert len(payload["baseline_normalized_power"]) == len(payload["controlled_normalized_power"])
    assert payload["target_metrics"]["controlled_normalized_power"] > 0.99


def test_displayed_target_metrics_match_the_analytical_array_factor() -> None:
    frequency_hz = 3.0e9
    spacing_m = 0.05
    element_count = 8
    target_angle_deg = 25.0
    response = client.post(
        "/api/simulations/beam-steering",
        json={
            "frequency_hz": frequency_hz,
            "spacing_m": spacing_m,
            "element_count": element_count,
            "target_angle_deg": target_angle_deg,
        },
    )
    payload = response.json()
    wavelength = 299_792_458.0 / frequency_hz
    psi = (2.0 * math.pi / wavelength) * spacing_m * math.sin(math.radians(target_angle_deg))
    expected_baseline = (math.sin(element_count * psi / 2.0) / (element_count * math.sin(psi / 2.0))) ** 2
    expected_improvement_db = 10.0 * math.log10(1.0 / expected_baseline)
    metrics = payload["target_metrics"]
    assert response.status_code == 200
    assert metrics["baseline_normalized_power"] == pytest.approx(expected_baseline)
    assert metrics["controlled_normalized_power"] == pytest.approx(1.0)
    assert metrics["improvement_db"] == pytest.approx(expected_improvement_db)


def test_custom_phase_length_and_invalid_frequency_are_rejected() -> None:
    invalid_phases = client.post("/api/simulations/custom-phases", json={"phase_values": [0.0]})
    invalid_frequency = client.post("/api/simulations/beam-steering", json={"frequency_hz": 0.0})
    assert invalid_phases.status_code == 422
    assert invalid_frequency.status_code == 422


def test_tradeoff_is_bounded() -> None:
    response = client.post(
        "/api/simulations/tradeoff",
        json={"receiver_angle_deg": 25.0, "observation_angle_deg": -20.0, "max_evaluations": 40},
    )
    assert response.status_code == 200
    assert response.json()["evaluation_count"] <= 40


def test_zero_reflection_does_not_report_a_fake_peak() -> None:
    response = client.post(
        "/api/simulations/beam-steering",
        json={"target_angle_deg": 25.0, "reflection_magnitude": 0.0},
    )
    assert response.status_code == 200
    assert response.json()["sampled_main_lobe_angles_deg"]["controlled"] is None


def test_beam_steering_with_research_parameters() -> None:
    response = client.post(
        "/api/simulations/beam-steering",
        json={
            "target_angle_deg": 30.0,
            "incident_angle_deg": -15.0,
            "element_pattern": "cosine",
            "phase_quantization_bits": 2,
            "coupled_loss_model": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "research_metrics" in payload
    assert payload["research_metrics"]["hpbw_deg"] is not None
    assert payload["research_metrics"]["directivity_dbi"] is not None


