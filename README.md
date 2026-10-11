# 📡 SmartRIS

> **An interactive, high-fidelity Reconfigurable Intelligent Surface (RIS) & 6G Holographic Beamforming Simulator.**  
> Explore anomalous reflection, phase-gradient beam steering, hardware quantization, and polar radiation patterns with physical electromagnetic rigor.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-smartris.vercel.app-000000?logo=vercel&logoColor=white)](https://smartris.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tests](https://img.shields.io/badge/Pytest-21%20Passed-brightgreen?logo=pytest&logoColor=white)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Why SmartRIS?

In 5G-Advanced and 6G wireless communication, millimeter-wave (mmWave) and sub-terahertz frequencies suffer from severe path attenuation and non-line-of-sight (NLOS) blockages. **Reconfigurable Intelligent Surfaces (RIS)**—also known as Intelligent Reflecting Surfaces (IRS) or Large Intelligent Surfaces (LIS)—turn the propagation environment itself into an active, programmable participant.

Instead of classical mirror-like specular reflection (where angle of reflection equals angle of incidence: $\theta_r = -\theta_i$), an engineered RIS modulates the phase profile across individual sub-wavelength metamaterial unit cells to create an **anomalous phase gradient**, shaping scattered wavefronts directly toward targeted user equipment ($Rx$).

**SmartRIS** gives researchers, radio engineers, and wireless enthusiasts an intuitive yet mathematically honest platform to model, visualize, and analyze RIS beam patterns in real time.

```
       Transmitter (Tx)
             \   θ_incident
              \
               \       Surface Normal (0°)
                v              |
       ========================+========================  <-- SmartRIS Array
       | Unit 0 | Unit 1 | Unit 2 | ... | Unit N-1 |          [x_n = n * d]
       ========================+========================
                                \
                                 \  θ_target
                                  \
                                   v
                             Receiver (Rx)
```

---

## 🚀 Key Features

* **⚡ True Bistatic Reflection Physics**:  
  Calculates continuous or discrete phase progressions taking into account arbitrary transmitter incident angles ($\theta_i$) and desired receiver angles ($\theta_t$):
  $$\phi_n = -k x_n (\sin\theta_{\text{target}} - \sin\theta_{\text{incident}})$$

* **🎯 Polar & Cartesian Spatial Radiation Diagrams**:
  * **Polar Radar Plot (0°–180°)**: Publication-grade polar radiation diagrams with concentric dB rings (0 dB down to -40 dB), angular radial spokes, and target vector pointers.
  * **Interactive Cartesian Line Plot**: Live cursor tracking, dynamic hover tooltips, main peak markers, target vertical indicators, and $-3\text{ dB}$ HPBW thresholds.
  * **Linear Power Scale**: Direct visualization of normalized $|AF(\theta)|^2$ power.

* **🔬 Realistic Hardware Imperfections**:
  * **Embedded Unit-Cell Element Pattern (EP)**: Simulates physical aperture roll-off with **Isotropic** ($1.0$), **Cosine** ($\cos\theta$), or **Microstrip Patch** ($\cos^2\theta$) models to eliminate unphysical grazing gain.
  * **Discrete Phase Quantization**: Test hardware constraints with **1-bit** ($\{0, \pi\}$), **2-bit** ($\{0, \pi/2, \pi, 3\pi/2\}$), and **3-bit** discrete PIN diode states.
  * **Diode Phase-Coupled Loss Model**: Incorporates the physical **Abeywickrama** practical phase-shift model, simulating dielectric absorption dips near resonance.

* **📊 Analytical RF Research Metrics**:
  * **HPBW**: Half-Power Beamwidth ($-3\text{ dB}$ width of main lobe).
  * **PSLL**: Peak Sidelobe Level in dB relative to the main beam.
  * **Array Directivity ($D$)**: Numerically integrated aperture directivity in dBi.
  * **Pointing Error**: Exact angular deviation between target and sampled peak.

* **🧪 Directional Trade-Off Lab**:  
  Bounded coordinate-search optimization that maximizes receiver gain while suppressing radiation toward sensitive observation or eavesdropper directions.

* **💾 1-Click Research Export**:  
  Export simulation arrays and phase tables directly to **CSV** or **JSON** for downstream analysis in MATLAB, Python (`matplotlib`/`pandas`), or LaTeX documents.

---

## 📐 Mathematical Formulation

### 1. Complex Array Factor & Coherent Field Summation

For a uniform linear array (ULA) of $N$ elements with spacing $d$ operating at frequency $f$, the free-space wavenumber is $k = \frac{2\pi f}{c}$. The normalized complex array factor across observation angles $\theta \in [-\frac{\pi}{2}, \frac{\pi}{2}]$ is:

$$AF(\theta) = \frac{1}{N} \sum_{n=0}^{N-1} \beta_n \exp\left(j \left[ k x_n (\sin\theta - \sin\theta_i) + \phi_n \right]\right)$$

The directional power is obtained from coherent superposition:

$$P(\theta) = \left| EP(\theta) \cdot AF(\theta) \right|^2$$

### 2. Practical Diode Reflection Model (Abeywickrama)

Real semiconductors (PIN diodes, varactors) exhibit phase-dependent amplitude variation:

$$\beta_n(\phi_n) = (1 - \beta_{\min}) \left( \frac{\sin(\phi_n - \phi_0) + 1}{2} \right)^\alpha + \beta_{\min}$$

Where $\beta_{\min} \approx 0.2$ models resonant absorption loss, $\phi_0 = 0$, and $\alpha = 1.6$.

### 3. Integrated Array Directivity

$$D = 10 \log_{10}\left( \frac{2 \max P(\theta)}{\int_{-\pi/2}^{\pi/2} P(\theta) \cos\theta \, d\theta} \right) \quad [\text{dBi}]$$

---

## 🛠️ Quickstart

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 1. Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

*Interactive Swagger API documentation is available at `http://127.0.0.1:8000/docs`.*

### 2. Frontend Setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

*Open `http://127.0.0.1:5173` to launch the simulator.*

---

## 🧪 Automated Testing

SmartRIS maintains a complete unit and integration test suite:

```powershell
# Run backend numerical and API verification
cd backend
python -m pytest -q
# Output: 21 passed

# Verify TypeScript compilation and production build
cd ..\frontend
npm run build
```

---

## 📂 Repository Architecture

```text
smartris/
├── api/                       # Vercel serverless entry point
│   └── index.py
├── backend/                   # Numerical core and FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI application factory
│   │   ├── routes.py          # REST endpoints
│   │   ├── simulation.py      # Array-factor, bistatic steering, and RF metrics
│   │   ├── optimization.py    # Deterministic coordinate search
│   │   ├── schemas.py         # Validated Pydantic request & response models
│   │   └── config.py          # Physical constants & limits
│   └── tests/                 # Numerical invariant & API tests
│       ├── test_simulation.py
│       ├── test_optimization.py
│       └── test_api.py
├── frontend/                  # React + TypeScript + Vite UI
│   ├── src/
│   │   ├── App.tsx            # Main application shell & workflows
│   │   ├── api.ts             # Centralized typed HTTP client
│   │   ├── types.ts           # Shared TypeScript interfaces
│   │   ├── styles.css         # Modern scientific-workbench design system
│   │   └── components/
│   │       ├── LineChart.tsx  # Interactive Cartesian plot with crosshair tooltips
│   │       ├── PolarChart.tsx # 180° Polar radar radiation pattern plot
│   │       ├── Metrics.tsx    # RF performance metrics grid
│   │       └── PhaseTable.tsx # Per-element phase progression table
│   └── package.json
├── docs/                      # Scientific documentation
│   ├── MATHEMATICAL_MODEL.md
│   ├── LIMITATIONS.md
│   ├── VALIDATION.md
│   ├── API.md
│   └── spec/                  # Internal architecture & design prompts
├── vercel.json                # Vercel full-stack deployment manifest
├── requirements.txt           # Root requirements for cloud deployment
├── LICENSE                    # MIT License
└── README.md
```

---

## 🌐 Live Platform

SmartRIS is deployed and publicly accessible on Vercel:

* **Production Web App:** [https://smartris.vercel.app](https://smartris.vercel.app)
* **REST API & Swagger Documentation:** [https://smartris.vercel.app/docs](https://smartris.vercel.app/docs)
* **Serverless Health Endpoint:** [https://smartris.vercel.app/api/health](https://smartris.vercel.app/api/health)

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
