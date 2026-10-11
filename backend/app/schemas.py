"""Validated HTTP request models for the SmartRIS API."""

from __future__ import annotations

from typing import Literal

import math

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from . import config


class ArraySimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    element_count: int = Field(
        default=config.DEFAULT_BEAM_STEERING["element_count"],
        ge=config.MIN_ELEMENT_COUNT,
        le=config.MAX_ELEMENT_COUNT,
        description="Number of uniformly spaced array elements.",
    )
    frequency_hz: float = Field(
        default=config.DEFAULT_BEAM_STEERING["frequency_hz"],
        gt=config.MIN_FREQUENCY_HZ,
        le=config.MAX_FREQUENCY_HZ,
        description="Operating frequency in hertz.",
    )
    spacing_m: float = Field(
        default=config.DEFAULT_BEAM_STEERING["spacing_m"],
        gt=config.MIN_SPACING_M,
        le=config.MAX_SPACING_M,
        description="Uniform inter-element spacing in metres.",
    )
    reflection_magnitude: float = Field(
        default=config.DEFAULT_BEAM_STEERING["reflection_magnitude"], ge=0.0, le=1.0
    )
    angle_start_deg: float = Field(
        default=config.DEFAULT_BEAM_STEERING["angle_start_deg"],
        ge=config.MIN_ANGLE_DEG,
        le=config.MAX_ANGLE_DEG,
    )
    angle_stop_deg: float = Field(
        default=config.DEFAULT_BEAM_STEERING["angle_stop_deg"],
        ge=config.MIN_ANGLE_DEG,
        le=config.MAX_ANGLE_DEG,
    )
    sample_count: int = Field(
        default=config.DEFAULT_BEAM_STEERING["sample_count"],
        ge=config.MIN_SAMPLE_COUNT,
        le=config.MAX_SAMPLE_COUNT,
    )
    incident_angle_deg: float = Field(
        default=0.0,
        ge=config.MIN_ANGLE_DEG,
        le=config.MAX_ANGLE_DEG,
        description="Incident plane wave direction in degrees.",
    )
    element_pattern: Literal["isotropic", "cosine", "cosine_squared"] = Field(
        default="isotropic",
        description="Embedded unit-cell radiation pattern model.",
    )
    phase_quantization_bits: int | None = Field(
        default=None,
        ge=1,
        le=8,
        description="Hardware phase quantization bits (e.g. 1-bit, 2-bit, 3-bit). None for continuous.",
    )
    coupled_loss_model: bool = Field(
        default=False,
        description="Whether to apply realistic diode phase-dependent reflection loss.",
    )

    @model_validator(mode="after")
    def check_angular_bounds(self) -> "ArraySimulationRequest":
        if self.angle_start_deg >= self.angle_stop_deg:
            raise ValueError("angle_start_deg must be less than angle_stop_deg.")
        return self


class BeamSteeringRequest(ArraySimulationRequest):
    target_angle_deg: float = Field(
        default=config.DEFAULT_BEAM_STEERING["target_angle_deg"],
        ge=config.MIN_ANGLE_DEG,
        le=config.MAX_ANGLE_DEG,
        description="Desired phase-controlled direction in degrees.",
    )


class CustomPhasesRequest(ArraySimulationRequest):
    phase_values: list[float] = Field(description="One programmed phase per element.")
    phase_units: Literal["degrees", "radians"] = "radians"

    @field_validator("phase_values")
    @classmethod
    def validate_phase_values(cls, values: list[float]) -> list[float]:
        if not values:
            raise ValueError("phase_values must not be empty.")
        if not all(math.isfinite(value) for value in values):
            raise ValueError("phase_values must contain only finite values.")
        return values

    @model_validator(mode="after")
    def check_phase_count(self) -> "CustomPhasesRequest":
        if len(self.phase_values) != self.element_count:
            raise ValueError("phase_values must contain exactly one value per element.")
        return self


class TradeoffRequest(ArraySimulationRequest):
    receiver_angle_deg: float = Field(ge=config.MIN_ANGLE_DEG, le=config.MAX_ANGLE_DEG)
    observation_angle_deg: float = Field(ge=config.MIN_ANGLE_DEG, le=config.MAX_ANGLE_DEG)
    penalty: float = Field(default=1.0, ge=0.0, description="Nonnegative observation-power penalty.")
    max_evaluations: int = Field(
        default=1000,
        ge=config.MIN_OPTIMIZER_EVALUATIONS,
        le=config.MAX_OPTIMIZER_EVALUATIONS,
    )
    observation_power_threshold: float | None = Field(default=None, ge=0.0)

