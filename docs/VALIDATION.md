# SmartRIS validation scope

The automated backend suite verifies software correctness and selected numerical invariants. It does not validate a physical surface, antenna, or radar-cross-section prediction.

Current tests cover:

- inverse wavelength scaling with frequency;
- uniform element positions beginning at zero;
- phase wrapping to `[-π, π)` without changing the complex phasor;
- zero phase progression at broadside;
- coherent field summation before normalized power;
- zero reflection magnitude and finite dB flooring;
- deterministic coordinate search, budget enforcement, and objective consistency;
- health, model-info, beam-steering, custom-phase validation, and trade-off API behavior.

Tests use deterministic configurations and floating-point `pytest.approx` comparisons where appropriate. The dB floor is `1e-12` normalized power. This verifies finite numerical output and stated equations—not electromagnetic accuracy, hardware agreement, material behavior, or experimental performance.

