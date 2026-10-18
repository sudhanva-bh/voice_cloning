# Performance Optimization Plan: 2x Speedup (Step Scaling & S23 Core Tuning)

**Document Version**: 1.0.0  
**Target Module**: `android/app` (Kotlin UI + Native C++ Engine)  
**Parent Architecture**: [litert_implementation_plan.md](../litert_implementation_plan.md)  
**Target Hardware**: Samsung Galaxy S23 (Snapdragon 8 Gen 2) & Lenovo Tab K10 (MediaTek Helio P22T)  
**Core Objective**: Accelerate on-device continuous flow matching (DiT) speech synthesis by **~2.2x to 2.5x** by:
1. Defaulting to 8 CFM steps and introducing a 6-step "Turbo" mode with calibrated sway scheduling.
2. Tuning native XNNPACK thread count to 5 threads to fully saturate all 5 high-performance/prime cores on the Snapdragon 8 Gen 2.

---

## 1. Technical Analysis & Bottlenecks

### 1.1 The Step-Count Multiplier
In the IndicF5 continuous flow matching architecture:
$$\text{Total Forward Passes} = N_{\text{steps}} \times 2 \quad (\text{Conditioned} + \text{Unconditioned CFG})$$

- At **16 steps**: $16 \times 2 = 32$ forward passes of the 343 MB DiT model. On S23 CPU, each forward pass takes $\approx 1.4\text{s}$, totaling $\approx 45\text{s}$ per chunk.
- At **8 steps**: $8 \times 2 = 16$ forward passes. Total time drops to $\approx 22\text{s}$ per chunk (**2.0x speedup**).
- At **6 steps (Turbo)**: $6 \times 2 = 12$ forward passes. Total time drops to $\approx 16\text{s}$ per chunk (**2.7x speedup**).

### 1.2 Sway Schedule Calibration for Low Step Counts
Euler integration error accumulates if time steps are spaced uniformly. In `EulerSampler::computeSwaySchedule`, the sway coefficient $\text{sway\_coef} = -1.0f$ curves the time trajectory:
$$t' = t + \text{sway\_coef} \times \left(\cos\left(\frac{\pi}{2} t\right) - 1 + t\right)$$
This curves sampling density so the ODE solver takes smaller steps in critical high-curvature velocity regions. For 6 and 8 steps, this ensures voice clarity and phoneme definition remain crisp without requiring 16 or 24 steps.

### 1.3 Snapdragon 8 Gen 2 CPU Topology Tuning
The Snapdragon 8 Gen 2 (`SM8550`) features an asymmetric tri-cluster CPU:
- $1\times$ Cortex-X3 Prime Core @ 3.36 GHz
- $2\times$ Cortex-A715 Performance Cores @ 2.80 GHz
- $2\times$ Cortex-A710 Performance Cores @ 2.80 GHz
- $3\times$ Cortex-A510 Efficiency Cores @ 2.00 GHz

The current default in `litert_indic_engine.cpp` is hardcoded to `num_threads = 4`. This leaves one high-performance core completely idle while computing heavy INT8 matrix multiplications.
Upgrading `num_threads = 5` allows XNNPACK to saturate all 5 prime and performance cores simultaneously, preventing thread migration onto slow A510 efficiency cores and delivering an estimated **15–20% hardware throughput gain**.

---

## 2. Implementation Work Breakdown

### Phase 1: Native C++ Engine Updates
1. **Thread Allocation**:
   - Update `LiteRTIndicEngine::initializeFromFiles` in [`litert_indic_engine.cpp`](file:///c:/voice_cloning/android/app/src/main/cpp/litert_indic_engine.cpp) from `num_threads = 4` to `num_threads = 5`.
2. **Sway Schedule & Step Support**:
   - Verify `computeSwaySchedule` in [`euler_sampler.cpp`](file:///c:/voice_cloning/android/app/src/main/cpp/euler_sampler.cpp) cleanly handles 6 steps ($N=6$).

### Phase 2: UI & Session Cache Integration
1. **RadioGroup Expansion in `activity_main.xml`**:
   - Add `rbStep6` ("6 Steps (Turbo)").
   - Set `rbStep8` as the `android:checked="true"` default (replacing 16).
2. **SessionCacheManager**:
   - Update `KEY_CFM_STEPS` default value from 16 to 8.
3. **MainActivity Listener**:
   - Wire `rbStep6` in `MainActivity.kt` to pass 6 steps to the engine.

### Phase 3: Verification & Benchmarking
1. Build and test on Samsung Galaxy S23.
2. Measure wall-clock time and RTF for 6 steps vs 8 steps vs 16 steps.
3. Verify that 6-step and 8-step speech audio quality is natural, fluent, and distortion-free.
