# 🔬 Antenna Array Simulation Audit & Verification Report

**Repository:** `25sarvesh2005/SMARTRIS`  
**Latest Verified Commit:** `15a1dd7`  
**Operating Parameters Audited:**
- Number of elements: $N = 8$
- Operating frequency: $f = 3.0\text{ GHz}$
- Element spacing: $d = 0.05\text{ m}$
- Desired steering angle: $\theta_0 = 25.0^\circ$
- Reflection coefficient magnitude: $|\Gamma| = 1.0$
- Angular samples: $M = 361$ over $[-90^\circ, +90^\circ]$ ($\Delta\theta = 0.5^\circ$)

---

## 1. Mathematical Formulas & Conventions

### Free-Space Wavelength & Spacing
Using standard SI velocity $c = 299{,}792{,}458\text{ m/s}$:
$$\lambda = \frac{c}{f} = \frac{299{,}792{,}458}{3.0 \times 10^9} = 0.09993082\text{ m} \approx 0.0999\text{ m}$$
$$k = \frac{2\pi}{\lambda} \approx 62.87538\text{ rad/m}$$
Electrical spacing:
$$\frac{d}{\lambda} = \frac{0.05}{0.09993082} = 0.500346 \approx 0.5\lambda$$

### Array Factor & Progressive Phase Steering
For elements at $x_n = n \cdot d$ ($n=0, \dots, N-1$), incident angle $\theta_i = 0^\circ$, and observation angle $\theta$:
$$AF(\theta) = \frac{|\Gamma|}{N} \sum_{n=0}^{N-1} e^{j (k x_n \sin\theta + \phi_n)}$$
Steering phases:
$$\phi_n = -k x_n \sin\theta_0 = -n k d \sin(25^\circ)$$
At $\theta = 25^\circ$:
$$\phi_n + k x_n \sin(25^\circ) = 0 \implies AF(25^\circ) = |\Gamma| = 1.0$$
The principal main lobe peaks at $+25^\circ$ without mirroring or inverted sign.

---

## 2. Metric Verification Table

| Metric | Code Value | Independent Analytical Proof | Status |
| :--- | :---: | :--- | :---: |
| **Wavelength** | $0.0999\text{ m}$ | $\lambda = 299{,}792{,}458 / 3\times 10^9 = 0.0999308\text{ m}$ | ✅ Verified |
| **Element Spacing** | $0.05\text{ m}$ | $d / \lambda = 0.500346 \approx \lambda/2$ | ✅ Verified |
| **Peak Angle** | $25.0^\circ$ | Constructive phasor alignment at $\theta = \theta_0 = 25^\circ$ | ✅ Verified |
| **HPBW (-3 dB)** | $14.15^\circ$ | Continuous roots at $18.1318^\circ$ and $32.2783^\circ \implies 14.1464^\circ \approx 14.15^\circ$ | ✅ Verified |
| **Peak Sidelobe (PSLL)** | $-12.8\text{ dB}$ | First sidelobe power is $0.052513 \implies 10\log_{10}(0.052513) = -12.797\text{ dB}$ | ✅ Verified |
| **Target Improvement** | $15.54\text{ dB}$ | $P_{\text{steered}}(25^\circ)=1.0$, $P_{\text{baseline}}(25^\circ)=0.027923 \implies 10\log_{10}(35.812) = 15.54\text{ dB}$ | ✅ Verified (Relabeled) |
| **Estimated Directivity** | $9.03\text{ dBi}$ | $D = \frac{2}{\int_{-1}^1 \|AF(u)\|^2 du} = N = 8 \implies 10\log_{10}(8) = 9.0309\text{ dBi}$ | ✅ Verified (1D AF Cut) |
| **Reflection Magnitude** | $1.0$ | Field coefficient $|\Gamma| \in [0, 1]$, $P_{\text{reflected}}/P_{\text{incident}} = |\Gamma|^2$ | ✅ Verified |

---

## 3. Automated Test Suite

33 automated unit tests pass in `backend/tests/`:
- `test_audit_1_wavelength_and_single_frequency_conversion`
- `test_audit_2_half_wavelength_spacing`
- `test_audit_3_broadside_beam_at_zero_degrees`
- `test_audit_4_steering_plus_and_minus_25_degrees_symmetry`
- `test_audit_5_unsteered_uniform_array_symmetry_and_dirichlet`
- `test_audit_6_agreement_between_power_db_and_field_db`
- `test_audit_7_hpbw_reproducibility_and_boundary_handling`
- `test_audit_8_peak_sidelobe_detection_excluding_main_lobe`
- `test_audit_9_safe_handling_of_zero_power_and_near_zero_baseline`
- `test_audit_10_target_improvement_metric_distinction_and_directivity`
- `test_audit_11_parameter_variations_frequency_element_count_spacing`
- `test_audit_12_reflection_magnitude_power_scaling`
