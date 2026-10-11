# SmartRIS limitations

SmartRIS is an idealized linear array-factor calculation. Its normalized directional power is not absolute received power, antenna gain, power density, scattering, radar cross section, or a measured quantity.

The model omits element radiation patterns, mutual coupling, substrate and material properties, edge effects, near-field coupling, polarization, losses beyond scalar reflection magnitude, hardware quantization, calibration, and environmental multipath. It has not been validated against laboratory measurements or a full-wave solver.

Spacing and frequency materially affect sampled patterns. Large spacing can lead to grating-lobe concerns depending on the geometry and scan direction. Main-lobe angles are limited by the angular sampling grid. The optimization is exploratory and deterministic, not a proof of global optimality.

