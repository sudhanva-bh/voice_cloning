# Literature Review Writing Plan

**Subject:** IndicF5-based multilingual zero-shot speech synthesis on native Android with Google LiteRT

## Suggested argument

Explain what zero-shot speech synthesis requires; introduce continuous flow matching and F5-TTS; connect these to IndicF5 and its adaptations; explain vocoding; then show why quantization and physical edge execution are nontrivial. Compare existing edge DiT-TTS optimization with Android/TFLite deployment evidence and close on the specific integration evaluated in the project.

## Suggested sections and approximate length

| Section | Approx. words | Core papers |
|---|---:|---|
| 1. Zero-shot and multilingual synthesis | 450–600 | 08, 11–13, 17–18 |
| 2. Continuous flow matching and F5-TTS | 550–700 | 02, 06, 09, 16 |
| 3. IndicF5-specific optimization | 400–550 | 03, 04; original IndicF5 model release |
| 4. Vocoder and signal reconstruction | 200–300 | 07 |
| 5. Edge and quantization | 500–700 | 01, 05, 14–15 |
| 6. LiteRT/Android execution | 350–500 | 19–21 |
| 7. Synthesis of gap and project positioning | 200–300 | 01–05, 19–21 |

**Total:** Approximately 2,650–3,650 words, adaptable to your supervisor’s requirements.

## Study questions to extract from the papers

1. **Architecture:** What constitutes the conditioning input, text representation, DiT denoiser, ODE solver, and vocoder?
2. **Quality:** How are speaker similarity, intelligibility, naturalness, timbre and phonetic stability assessed?
3. **Efficiency:** Which optimizations are structural (pruning/distillation) versus runtime (quantization/delegates/FFT/caching)?
4. **Deployment:** What hardware, memory, threading, precision and benchmarking procedures are reported?
5. **Fairness:** Which experimental settings differ enough to prohibit direct cross-paper speed claims?
6. **Research gap:** Which combination of capabilities and constraints is not demonstrated by the selected related work?

## Critical distinctions

- **Pivot-FSOF:** edge GPU/CUDA/Jetson; not Android/XNNPACK.
- **RIS beamforming:** LiteRT for Microcontrollers; not Android LiteRT and not TTS.
- **EinsteinNet/health classification:** Android TFLite examples, but different workloads and model scales.
- **IndicF5 depth-pruning and spectral papers:** directly relevant but preprint/manuscript status, not confirmed peer-reviewed journals.
- **Vocos:** vocoder research, not proof that a particular native FFT routine is accurate.
- **Original IndicF5:** cite official model release separately; absent as an original journal-paper PDF from the core collection.

## Recommended evaluation table for your own experiments

| Model/runtime | Device | Precision | CFM steps | Audio duration | Synthesis latency | RTF (time/audio) | Peak RSS | Quality measure |
|---|---|---|---:|---:|---:|---:|---:|---|
| PyTorch baseline | Laptop | FP32 | — | — | — | — | — | — |
| Native LiteRT | Galaxy S23 | INT8 | 12 | — | — | — | — | — |
| Native LiteRT | Galaxy S23 | INT8 | 16 | — | — | — | — | — |
| Native LiteRT | Lenovo Tab K10 | INT8 | 16 | — | — | — | — | — |

Fill values from original experiment logs rather than estimating from papers.
