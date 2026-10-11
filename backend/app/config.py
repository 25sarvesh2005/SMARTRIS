"""Application constants and deliberately small, local-first limits."""

SPEED_OF_LIGHT_M_S = 299_792_458.0
MODEL_ID = "idealized-linear-array-factor-v1"
API_VERSION = "0.1.0"

MIN_ELEMENT_COUNT = 2
MAX_ELEMENT_COUNT = 128
MIN_FREQUENCY_HZ = 1.0e6
MAX_FREQUENCY_HZ = 100.0e9
MIN_SPACING_M = 1.0e-4
MAX_SPACING_M = 10.0
MIN_ANGLE_DEG = -90.0
MAX_ANGLE_DEG = 90.0
MIN_SAMPLE_COUNT = 181
MAX_SAMPLE_COUNT = 1441
MIN_OPTIMIZER_EVALUATIONS = 1
MAX_OPTIMIZER_EVALUATIONS = 10_000
DB_FLOOR_POWER = 1.0e-12
IMPROVEMENT_BASELINE_FLOOR = 1.0e-12

DEFAULT_BEAM_STEERING = {
    "element_count": 8,
    "frequency_hz": 3.0e9,
    "spacing_m": 0.05,
    "target_angle_deg": 25.0,
    "reflection_magnitude": 1.0,
    "angle_start_deg": -90.0,
    "angle_stop_deg": 90.0,
    "sample_count": 361,
}

