# Reference Literature Collection

**Project:** On-Device Multilingual Zero-Shot Voice Cloning Using IndicF5 and Google LiteRT  
**Date:** 12 November 2026  
**Corpus:** 21 main references and 5 supplementary references (26 PDFs)

## Abstract

This collection reviews neural zero-shot and multilingual text-to-speech synthesis, the mathematical and architectural foundations of F5-TTS and IndicF5, and techniques for deploying neural inference on resource-constrained systems. Particular emphasis is placed on flow-matching sampling, diffusion-transformer optimization, neural vocoding, post-training quantization, LiteRT/TensorFlow Lite, and Android hardware benchmarking. References are arranged in descending order of relevance to an IndicF5-based on-device speech synthesis system. Journal, conference, and preprint literature are identified separately.

## Publication distribution

| Publication type | Main | Supplementary | Total |
|---|---:|---:|---:|
| Peer-reviewed journal | 13 | 4 | 17 |
| Conference proceedings | 5 | 1 | 6 |
| Research preprint | 3 | 0 | 3 |
| **Total** | **21** | **5** | **26** |

The 17 journal papers comprise IEEE (including IEEE/ACM joint journals), ACM, and Elsevier publications. The conference papers provide foundational research not published exclusively as journal articles in this collection. IndicF5-specific research preprints are retained because of their direct architectural relevance.

## Publication index and source URLs

The abbreviated titles below correspond to the complete bibliographic records and local PDF links in the following sections.

| Ref. | Paper | Publisher / source | Journal / venue | Type | Year | Research relevance | Publication URL |
|---|---|---|---|---|---|---|---|
| 01 | Pivot-FSOF | Elsevier | Journal of Systems Architecture | Journal | 2026 | DiT-TTS optimization on edge GPU | [Link](https://doi.org/10.1016/j.sysarc.2026.103915) |
| 02 | F5-TTS | ACL | ACL 2025 | Conference | 2025 | Base DiT/flow-matching TTS architecture | [Link](https://aclanthology.org/2025.acl-long.313/) |
| 03 | IndicF5 depth-pruning distillation | arXiv | arXiv | Preprint | 2026 | IndicF5 teacher-model compression | [Link](https://arxiv.org/abs/2607.18662) |
| 04 | Spectral evolution in CFM TTS | arXiv | arXiv | Preprint | 2026 | IndicF5 sampling and spectral stability | [Link](https://arxiv.org/abs/2609.34431) |
| 05 | QuantEdge | IEEE | IEEE Access | Journal | 2025 | Quantization on edge hardware | [Link](https://doi.org/10.1109/ACCESS.2025.3609798) |
| 06 | Flow Matching for Generative Modeling | ICLR | ICLR 2023 | Conference | 2023 | CFM mathematical foundation | [Link](https://arxiv.org/abs/2210.02747) |
| 07 | Vocos | ICLR | ICLR 2024 | Conference | 2024 | Fourier neural vocoding | [Link](https://arxiv.org/abs/2306.00814) |
| 08 | ZMM-TTS | IEEE/ACM | IEEE/ACM TASLP | Journal | 2024 | Multilingual zero-shot TTS | [Link](https://doi.org/10.1109/TASLP.2024.3451951) |
| 09 | Matcha-TTS | IEEE | ICASSP 2024 | Conference | 2024 | Efficient conditional flow matching | [Link](https://doi.org/10.1109/ICASSP48485.2024.10448291) |
| 10 | FlashSpeech | arXiv | arXiv manuscript | Preprint | 2024 | Low-step zero-shot synthesis | [Link](https://arxiv.org/abs/2404.14700) |
| 11 | Voice Cloning: A Survey | IEEE | IEEE Access | Journal | 2026 | Voice-cloning literature taxonomy | [Link](https://doi.org/10.1109/ACCESS.2026.3722351) |
| 12 | U-Style | IEEE/ACM | IEEE/ACM TASLP | Journal | 2024 | Speaker/style disentanglement | [Link](https://doi.org/10.1109/TASLP.2024.3453606) |
| 13 | PerTTS | IEEE | IEEE TASLP | Journal | 2026 | Controllable speaker style | [Link](https://doi.org/10.1109/TASLPRO.2025.3639814) |
| 14 | Sometimes Painful but Promising | ACM | ACM journal | Journal | 2026 | Mobile memory and latency trade-offs | [Link](https://doi.org/10.1145/3788870) |
| 15 | SIMD-CP | ACM | ACM journal | Journal | 2026 | Mixed-precision DNN execution | [Link](https://doi.org/10.1145/3771939) |
| 16 | E2-TTS | IEEE | SLT 2024 | Conference | 2024 | Precursor to F5-TTS | [Link](https://doi.org/10.1109/SLT61566.2024.10832320) |
| 17 | CMDF-TTS | Elsevier | Neural Networks | Journal | 2025 | Limited target-speaker data | [Link](https://doi.org/10.1016/j.neunet.2025.107432) |
| 18 | VALL-E | IEEE | IEEE TASLP | Journal | 2025 | Neural-codec zero-shot TTS alternative | [Link](https://doi.org/10.1109/TASLPRO.2025.3530270) |
| 19 | EinsteinNet Android deployment | Elsevier | Smart Agricultural Technology | Journal | 2025 | TFLite Android device evaluation | [Link](https://doi.org/10.1016/j.atech.2025.101072) |
| 20 | On-Device DL for RIS Beamforming | IEEE | IEEE Open Journal of the Communications Society | Journal | 2026 | LiteRT Micro and INT8 benchmarking | [Link](https://doi.org/10.1109/OJCOMS.2026.3687306) |
| 21 | ML Classification in Mobile Applications | Elsevier | Egyptian Informatics Journal | Journal | 2026 | Kotlin/TFLite low-end Android | [Link](https://doi.org/10.1016/j.eij.2026.100987) |
| S01 | Empirical Guidelines for Edge LLMs | ACM | ACM journal | Journal | 2025 | Edge memory and throughput | [Link](https://doi.org/10.1145/3736721) |
| S02 | Voicebox | NeurIPS | NeurIPS 2023 | Conference | 2023 | Multilingual generative speech | [Link](https://proceedings.neurips.cc/paper_files/paper/2023/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html) |
| S03 | Controllable Timbre Cloning | Elsevier | Neurocomputing | Journal | 2025 | Timbre and style transfer | [Link](https://doi.org/10.1016/j.neucom.2025.132529) |
| S04 | Multi-Level Expressive Voice Cloning | IEEE | IEEE Access | Journal | 2026 | Expressive speaker modeling | [Link](https://doi.org/10.1109/ACCESS.2026.3691952) |
| S05 | Multilingual Audio Dubbing | Elsevier | Results in Engineering | Journal | 2025 | Multilingual application context | [Link](https://doi.org/10.1016/j.rineng.2025.106241) |

## IndicF5 model reference

**AI4Bharat — IndicF5: High-Quality Text-to-Speech for Indian Languages.** Original software/model release, distinct from the peer-reviewed publications above. [Official repository](https://github.com/AI4Bharat/IndicF5) · [Model card](https://huggingface.co/ai4bharat/IndicF5).

## A. Core research literature (21 papers)


### Essential: IndicF5, F5-TTS and efficient edge TTS

#### 01. Pivot-FSOF: A Full-Stack Optimization Framework for Real-Time DiT-Based TTS on Edge Devices

- **Authors:** Chenhe Gong; Huan Guo; Wenjie Zhang; Mingjiang Wang
- **Year:** 2026
- **Venue / publisher:** Journal of Systems Architecture (Elsevier)
- **Publication status:** Journal
- **DOI:** [`10.1016/j.sysarc.2026.103915`](https://doi.org/10.1016/j.sysarc.2026.103915)
- **Publication URL:** [https://doi.org/10.1016/j.sysarc.2026.103915](https://doi.org/10.1016/j.sysarc.2026.103915)
- **Local file:** [`01_Pivot_FSOF_Edge_DiT_TTS.pdf`](01_Pivot_FSOF_Edge_DiT_TTS.pdf)
- **Role:** Edge inference

**Summary.** Introduces full-stack algorithm/hardware co-design for DiT-based speech synthesis on NVIDIA Jetson AGX Orin. It combines pivot-aware structured pruning, sensitivity-aware INT8 quantization, distillation, fused CUDA RoPE, zero-copy transfers and CUDA Graphs. The authors report 27% fewer network layers, a 9.13× end-to-end speedup versus an ONNX Runtime FP32 baseline, and a 2.23× speedup versus a TensorRT FP16 baseline.

**Project relevance.** Closest selected comparison for accelerating flow-based TTS under edge memory and latency constraints; the work highlights deployment-stack and hardware differences.

**Scope and limitations.** Jetson GPU/CUDA results cannot be transferred directly to ARM CPU/XNNPACK or Android; not an IndicF5 Android implementation.

#### 02. F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching

- **Authors:** Yushen Chen; Zhikang Niu; Ziyang Ma; Keqi Deng; Chunhui Wang; Jian Zhao; Kai Yu; Xie Chen
- **Year:** 2025
- **Venue / publisher:** Proceedings of ACL 2025 (Association for Computational Linguistics)
- **Publication status:** Conference
- **DOI:** [`10.18653/v1/2025.acl-long.313`](https://doi.org/10.18653/v1/2025.acl-long.313)
- **Publication URL:** [https://aclanthology.org/2025.acl-long.313/](https://aclanthology.org/2025.acl-long.313/)
- **Local file:** [`02_F5_TTS_Flow_Matching.pdf`](02_F5_TTS_Flow_Matching.pdf)
- **Role:** TTS foundations

**Summary.** Introduces a non-autoregressive flow-matching TTS system using a diffusion transformer and a ConvNeXt text representation. It avoids explicit duration predictors and phoneme alignment, then uses Sway Sampling to adjust ODE inference timesteps. The paper reports zero-shot synthesis, cross-language behavior and a favorable real-time factor in its evaluated environment.

**Project relevance.** Architecture and inference-step reference for the IndicF5-derived DiT backbone, text conditioning, and sampler.

**Scope and limitations.** Not a LiteRT or physical Android deployment paper.

#### 03. Staged Depth-Pruning Distillation of a Flow-Matching Text-to-Speech Teacher: A Compact Hindi Speech Synthesizer

- **Authors:** Sivateja Trikutam
- **Year:** 2026
- **Venue / publisher:** arXiv research manuscript
- **Publication status:** Preprint
- **DOI:** Not verified from the supplied PDF
- **Publication URL:** [https://arxiv.org/abs/2607.18662](https://arxiv.org/abs/2607.18662)
- **Local file:** [`03_IndicF5_Depth_Pruning.pdf`](03_IndicF5_Depth_Pruning.pdf)
- **Role:** IndicF5

**Summary.** Uses IndicF5 as a large teacher and gradually reduces transformer depth (22 to 16, 12, 8, and 6 blocks) with staged fine-tuning under a limited Hindi-data budget. It assesses intelligibility with ASR-based WER and identifies sharp capacity degradation at the smallest size; it also documents feature and library parity pitfalls.

**Project relevance.** Direct IndicF5 adaptation and compression comparison: pruning/distillation versus INT8 and runtime optimization of the existing model.

**Scope and limitations.** Primarily Hindi and GPU testing; does not establish native LiteRT Android performance.

#### 04. Harmonizing Spectral Evolution in Conditional Flow Matching for TTS

- **Authors:** Isha Pandey; Varad Deshpande; Abhijat Bharadwaj; Ganesh Ramakrishnan
- **Year:** 2026
- **Venue / publisher:** Research manuscript (publication venue not established from supplied PDF)
- **Publication status:** Preprint/manuscript
- **DOI:** Not verified from the supplied PDF
- **Publication URL:** [https://arxiv.org/abs/2609.34431](https://arxiv.org/abs/2609.34431)
- **Local file:** [`04_IndicF5_Spectral_Optimization.pdf`](04_IndicF5_Spectral_Optimization.pdf)
- **Role:** IndicF5

**Summary.** Studies mismatched growth of low- and high-frequency content during conditional flow-matching speech generation. The proposed training-free method uses a discrete wavelet transform to intervene selectively in mel-spectrogram frequency bands as an ODE solver runs. The experiments include Matcha-TTS, F5-TTS and IndicF5.

**Project relevance.** Highly relevant to short-step ODE stability and maintaining acoustic quality when reducing function evaluations.

**Scope and limitations.** No direct demonstration of LiteRT/Android integration in this PDF.

#### 05. QuantEdge: A Hybrid Quantization Approach for Optimized AI Deployment Across Edge Devices

- **Authors:** Rasim Mahmudov; Deok-Hwan Kim
- **Year:** 2025
- **Venue / publisher:** IEEE Access
- **Publication status:** Journal
- **DOI:** [`10.1109/ACCESS.2025.3609798`](https://doi.org/10.1109/ACCESS.2025.3609798)
- **Publication URL:** [https://doi.org/10.1109/ACCESS.2025.3609798](https://doi.org/10.1109/ACCESS.2025.3609798)
- **Local file:** [`05_QuantEdge_Edge_Quantization.pdf`](05_QuantEdge_Edge_Quantization.pdf)
- **Role:** Edge inference

**Summary.** Presents a hybrid quantization framework that chooses precision configurations according to the capabilities of different edge devices. It compares latency, accuracy, memory and energy across devices including Jetson, Raspberry Pi and edge accelerators. The reported experiments demonstrate device-dependent benefits instead of a one-size-fits-all quantization strategy.

**Project relevance.** A methodological reference for evaluating weight compression and quantization trade-offs against actual inference latency and speech-quality parity.

**Scope and limitations.** Workloads/hardware differ from large flow-matching speech models and Android XNNPACK.

#### 06. Flow Matching for Generative Modeling

- **Authors:** Yaron Lipman; Ricky T. Q. Chen; Heli Ben-Hamu; Maximilian Nickel; Matt Le
- **Year:** 2023
- **Venue / publisher:** ICLR 2023 (International Conference on Learning Representations)
- **Publication status:** Conference
- **DOI:** Not verified from the supplied PDF
- **Publication URL:** [https://arxiv.org/abs/2210.02747](https://arxiv.org/abs/2210.02747)
- **Local file:** [`06_Flow_Matching_Foundations.pdf`](06_Flow_Matching_Foundations.pdf)
- **Role:** TTS foundations

**Summary.** Formalizes simulation-free training of continuous normalizing flows by fitting conditional vector fields along specified probability paths. It highlights optimal-transport interpolation and numerical ODE sampling, establishing the mathematical framework later used by conditional flow-matching speech generators.

**Project relevance.** Establishes noise-to-mel integration, continuous-time velocity prediction, and step-size effects relevant to measured low-step device behavior.

**Scope and limitations.** General generative modeling; not speech-specific or about deployed software.

#### 07. Vocos: Closing the Gap Between Time-Domain and Fourier-Based Neural Vocoders for High-Quality Audio Synthesis

- **Authors:** Hubert Siuzdak
- **Year:** 2024
- **Venue / publisher:** ICLR 2024
- **Publication status:** Conference
- **DOI:** Not verified from the supplied PDF
- **Publication URL:** [https://arxiv.org/abs/2306.00814](https://arxiv.org/abs/2306.00814)
- **Local file:** [`07_Vocos_Neural_Vocoder.pdf`](07_Vocos_Neural_Vocoder.pdf)
- **Role:** Vocoder

**Summary.** Proposes a vocoder that directly predicts Fourier-domain spectral representations instead of relying on computationally expensive time-domain upsampling. Its evaluation reports competitive audio quality with substantially improved computational efficiency.

**Project relevance.** Provides the architectural basis for the deployed Vocos stage and the iSTFT reconstruction workload in native C++.

**Scope and limitations.** The paper does not study the Android FFT implementation considered here or LiteRT conversion.


### Multilingual, zero-shot and efficient synthesis

#### 08. ZMM-TTS: Zero-Shot Multilingual and Multispeaker Speech Synthesis Conditioned on Self-Supervised Discrete Speech Representations

- **Authors:** Cheng Gong; Xin Wang; Erica Cooper; Dan Wells; Longbiao Wang; Jianwu Dang; Korin Richmond; Junichi Yamagishi
- **Year:** 2024
- **Venue / publisher:** IEEE/ACM Transactions on Audio, Speech, and Language Processing
- **Publication status:** Journal
- **DOI:** [`10.1109/TASLP.2024.3451951`](https://doi.org/10.1109/TASLP.2024.3451951)
- **Publication URL:** [https://doi.org/10.1109/TASLP.2024.3451951](https://doi.org/10.1109/TASLP.2024.3451951)
- **Local file:** [`08_ZMM_TTS_Multilingual.pdf`](08_ZMM_TTS_Multilingual.pdf)
- **Role:** Multilingual TTS

**Summary.** Combines text- and speech-based self-supervised representations for multilingual, multispeaker speech synthesis. It evaluates speaker similarity and intelligibility for known and unseen speakers and examines transfer to low-resource or previously unseen languages.

**Project relevance.** Helps establish expectations for zero-shot cross-speaker and cross-language generalization, including underrepresented languages.

**Scope and limitations.** Different acoustic representation and training method; no mobile deployment.

#### 09. Matcha-TTS: A Fast TTS Architecture with Conditional Flow Matching

- **Authors:** Shivam Mehta; Ruibo Tu; Jonas Beskow; Éva Székely; Gustav Eje Henter
- **Year:** 2024
- **Venue / publisher:** IEEE ICASSP 2024
- **Publication status:** Conference
- **DOI:** [`10.1109/ICASSP48485.2024.10448291`](https://doi.org/10.1109/ICASSP48485.2024.10448291)
- **Publication URL:** [https://doi.org/10.1109/ICASSP48485.2024.10448291](https://doi.org/10.1109/ICASSP48485.2024.10448291)
- **Local file:** [`09_Matcha_TTS.pdf`](09_Matcha_TTS.pdf)
- **Role:** TTS foundations

**Summary.** Develops an encoder–decoder text-to-speech model using optimal-transport conditional flow matching and an ODE-based decoder. It emphasizes efficient synthesis with relatively few solver evaluations, compact memory usage and strong acoustic quality.

**Project relevance.** Technical background for flow-matching inference and the relationship between ODE steps, speed and fidelity.

**Scope and limitations.** Not an IndicF5 DiT deployment and no Android target.

#### 10. FlashSpeech: Efficient Zero-Shot Speech Synthesis

- **Authors:** Zhen Ye et al.
- **Year:** 2024
- **Venue / publisher:** arXiv research manuscript
- **Publication status:** Preprint (no journal record confirmed)
- **DOI:** Not verified from the supplied PDF
- **Publication URL:** [https://arxiv.org/abs/2404.14700](https://arxiv.org/abs/2404.14700)
- **Local file:** [`10_FlashSpeech_Efficient_TTS.pdf`](10_FlashSpeech_Efficient_TTS.pdf)
- **Role:** Multilingual TTS

**Summary.** Investigates efficient zero-shot speech generation as an alternative to slower iterative synthesis pipelines. Its stated objective is to retain expressive, speaker-conditioned audio while reducing inference overhead, demonstrating the broader field’s focus on fewer expensive sampling operations.

**Project relevance.** Useful comparison when discussing quality versus generation-time trade-offs in zero-shot speech systems.

**Scope and limitations.** Not a LiteRT or IndicF5 on-device implementation.

#### 11. Voice Cloning: A Survey of Zero-Shot and Controllable Speech Synthesis

- **Authors:** Niraj Kumar Tiwari; Deepak Kumar; Asif Ekbal
- **Year:** 2026
- **Venue / publisher:** IEEE Access
- **Publication status:** Journal
- **DOI:** [`10.1109/ACCESS.2026.3722351`](https://doi.org/10.1109/ACCESS.2026.3722351)
- **Publication URL:** [https://doi.org/10.1109/ACCESS.2026.3722351](https://doi.org/10.1109/ACCESS.2026.3722351)
- **Local file:** [`11_Voice_Cloning_Survey.pdf`](11_Voice_Cloning_Survey.pdf)
- **Role:** Multilingual TTS

**Summary.** Surveys voice-cloning architectures with emphasis on zero-shot conditioning and controllability, organizing model types and evaluation considerations. It provides broad context for the progression from earlier neural TTS to recent generative and prompt-driven voice-cloning approaches.

**Project relevance.** Best umbrella citation to introduce the field and motivate selecting a speaker-conditioned zero-shot model.

**Scope and limitations.** Survey-level rather than a practical mobile deployment baseline.

#### 12. U-Style: Cascading U-nets with Multi-Level Speaker and Style Modeling for Zero-Shot Voice Cloning

- **Authors:** Tao Li; Zhichao Wang; Xinfa Zhu; Jian Cong; Qiao Tian; Yuping Wang; Lei Xie
- **Year:** 2024
- **Venue / publisher:** IEEE/ACM Transactions on Audio, Speech, and Language Processing
- **Publication status:** Journal
- **DOI:** [`10.1109/TASLP.2024.3453606`](https://doi.org/10.1109/TASLP.2024.3453606)
- **Publication URL:** [https://doi.org/10.1109/TASLP.2024.3453606](https://doi.org/10.1109/TASLP.2024.3453606)
- **Local file:** [`12_U_Style_Voice_Cloning.pdf`](12_U_Style_Voice_Cloning.pdf)
- **Role:** Multilingual TTS

**Summary.** Proposes a cascaded U-Net architecture with separate speaker/style modeling to improve cloning for voices unseen during model training. It addresses preserving identity while handling acoustic style, a common problem in reference-conditioned TTS.

**Project relevance.** Useful as an alternative architectural approach and for understanding speaker similarity versus expression.

**Scope and limitations.** No direct LiteRT quantization or Android hardware study; published status needs bibliographic confirmation.

#### 13. PerTTS: Personalized and Controllable Zero-Shot Spontaneous Style Text-to-Speech Synthesis

- **Authors:** Weiqin Li; Qian Chen; Dan Luo; Tianjiao Du; Yafeng Chen; Zhiyong Wu; Xixin Wu; Helen Meng
- **Year:** 2026
- **Venue / publisher:** IEEE Transactions on Audio, Speech, and Language Processing
- **Publication status:** Journal
- **DOI:** [`10.1109/TASLPRO.2025.3639814`](https://doi.org/10.1109/TASLPRO.2025.3639814)
- **Publication URL:** [https://doi.org/10.1109/TASLPRO.2025.3639814](https://doi.org/10.1109/TASLPRO.2025.3639814)
- **Local file:** [`13_PerTTS_Zero_Shot.pdf`](13_PerTTS_Zero_Shot.pdf)
- **Role:** Multilingual TTS

**Summary.** Examines personalized zero-shot synthesis where both speaker characteristics and spontaneous conversational speaking style matter. It studies controllability of the generated speech in addition to standard naturalness and speaker adaptation.

**Project relevance.** Provides motivation to assess not only words and latency but also speaker identity and prosody after INT8 conversion.

**Scope and limitations.** Not centered on Android or flow-matching runtime optimization.


### Edge inference and alternative architectures

#### 14. Sometimes Painful but Promising: Feasibility and Trade-Offs of On-Device Language Model Inference

- **Authors:** Maximilian Abstreiter; Sasu Tarkoma; Roberto Morabito
- **Year:** 2026
- **Venue / publisher:** ACM publication (title page does not specify full issue metadata)
- **Publication status:** Journal
- **DOI:** [`10.1145/3788870`](https://doi.org/10.1145/3788870)
- **Publication URL:** [https://doi.org/10.1145/3788870](https://doi.org/10.1145/3788870)
- **Local file:** [`14_On_Device_Inference_Tradeoffs.pdf`](14_On_Device_Inference_Tradeoffs.pdf)
- **Role:** Edge inference

**Summary.** Empirically studies resource constraints and trade-offs encountered when executing language models locally rather than relying on cloud inference. Its discussion of throughput, latency, and device feasibility informs hardware-sensitive deployment studies.

**Project relevance.** Supports framing and reporting memory/latency constraints and differences between mobile device classes.

**Scope and limitations.** Language models are not spectrogram-generating speech models; metrics must not be compared directly.

#### 15. SIMD-CP: SIMD with Redundant Bits Compression and Mixed-Precision Packing for Quantized DNNs

- **Authors:** Hayata Kaneko; Ryuto Ishibashi; Lin Meng
- **Year:** 2026
- **Venue / publisher:** ACM publication
- **Publication status:** Journal
- **DOI:** [`10.1145/3771939`](https://doi.org/10.1145/3771939)
- **Publication URL:** [https://doi.org/10.1145/3771939](https://doi.org/10.1145/3771939)
- **Local file:** [`15_SIMD_CP_Mixed_Precision.pdf`](15_SIMD_CP_Mixed_Precision.pdf)
- **Role:** Edge inference

**Summary.** Investigates mixed-precision SIMD packing and compressed representations to accelerate quantized neural-network operations. It highlights how arithmetic layout and underlying hardware vectorization can affect efficiency beyond nominal model size.

**Project relevance.** Helps explain why INT8 footprint reduction alone does not guarantee proportional latency reduction on ARM CPUs.

**Scope and limitations.** Not an evaluation of the XNNPACK or Android implementation in this project.

#### 16. E2 TTS: Embarrassingly Easy Fully Non-Autoregressive Zero-Shot TTS

- **Authors:** Sefik Emre Eskimez et al.
- **Year:** 2024
- **Venue / publisher:** IEEE Spoken Language Technology Workshop (SLT 2024)
- **Publication status:** Conference
- **DOI:** [`10.1109/SLT61566.2024.10832320`](https://doi.org/10.1109/SLT61566.2024.10832320)
- **Publication URL:** [https://doi.org/10.1109/SLT61566.2024.10832320](https://doi.org/10.1109/SLT61566.2024.10832320)
- **Local file:** [`16_E2_TTS.pdf`](16_E2_TTS.pdf)
- **Role:** TTS foundations

**Summary.** Introduces an alignment-free, fully non-autoregressive zero-shot TTS formulation. The model simplifies text/speech alignment and demonstrates that a generative backbone can learn conditional speech without explicit duration supervision.

**Project relevance.** Useful predecessor to F5-TTS, showing why simpler flow-based architectures are attractive.

**Scope and limitations.** An architectural foundation, not the deployed IndicF5 model or an Android study.

#### 17. CMDF-TTS: Text-to-Speech Method with Limited Target Speaker Corpus

- **Authors:** Ye Tao; Jiawang Liu; Chaofeng Lu; Meng Liu; Xiugong Qin; Yunlong Tian; Yongjie Du
- **Year:** 2025
- **Venue / publisher:** Neural Networks (Elsevier)
- **Publication status:** Journal
- **DOI:** [`10.1016/j.neunet.2025.107432`](https://doi.org/10.1016/j.neunet.2025.107432)
- **Publication URL:** [https://doi.org/10.1016/j.neunet.2025.107432](https://doi.org/10.1016/j.neunet.2025.107432)
- **Local file:** [`17_CMDF_TTS.pdf`](17_CMDF_TTS.pdf)
- **Role:** Multilingual TTS

**Summary.** Investigates text-to-speech when the available target-speaker corpus is limited, tackling an important challenge for personalized synthesis. It represents an alternative approach to adapting speech systems with restricted speaker data.

**Project relevance.** Useful for motivating a short reference-clip, zero-shot approach rather than per-speaker training.

**Scope and limitations.** Its adaptation/data assumptions differ from the deployed fixed IndicF5 model.

#### 18. Neural Codec Language Models Are Zero-Shot Text to Speech Synthesizers

- **Authors:** Chengyi Wang; Sanyuan Chen; Yu Wu; Ziqiang Zhang; Long Zhou; Shujie Liu; Zhuo Chen; Yanqing Liu; Huaming Wang; Jinyu Li; Lei He; Sheng Zhao; Furu Wei
- **Year:** 2025 (journal version; initial preprint 2023)
- **Venue / publisher:** IEEE Transactions on Audio, Speech and Language Processing
- **Publication status:** Journal
- **DOI:** [`10.1109/TASLPRO.2025.3530270`](https://doi.org/10.1109/TASLPRO.2025.3530270)
- **Publication URL:** [https://doi.org/10.1109/TASLPRO.2025.3530270](https://doi.org/10.1109/TASLPRO.2025.3530270)
- **Local file:** [`18_VALL_E_Neural_Codec.pdf`](18_VALL_E_Neural_Codec.pdf)
- **Role:** Multilingual TTS

**Summary.** Introduces VALL-E, a conditional neural-codec language model treating speech generation as discrete token prediction. It reports speaker-conditioned synthesis from a short voice prompt, illustrating a prominent competing family of zero-shot models.

**Project relevance.** Provides a conceptual contrast with IndicF5’s continuous mel flow-matching process and iterative ODE inference.

**Scope and limitations.** Architecture is not the same as the model being deployed; mobile benchmarking is absent.


### LiteRT and Android deployment

#### 19. EinsteinNet and State-of-the-Art ML Models for Android-Based Orange Classification: Integration, Evaluation, and Deployment

- **Authors:** Ashif Ahmed Shuvo; Wahada Jinnat Oishy Bhuian; Afzal Rahman; Abdullah Iqbal
- **Year:** 2025
- **Venue / publisher:** Smart Agricultural Technology (Elsevier)
- **Publication status:** Journal
- **DOI:** [`10.1016/j.atech.2025.101072`](https://doi.org/10.1016/j.atech.2025.101072)
- **Publication URL:** [https://doi.org/10.1016/j.atech.2025.101072](https://doi.org/10.1016/j.atech.2025.101072)
- **Local file:** [`19_Android_TFLite_EinsteinNet.pdf`](19_Android_TFLite_EinsteinNet.pdf)
- **Role:** LiteRT/Android

**Summary.** Converts several CNN models to TensorFlow Lite and measures offline inference on a Google Pixel 6, covering quantized size, prediction performance, latency and power. The paper shows that a compact model need not be the fastest: EinsteinNet has a small quantized footprint but much higher latency than selected alternatives.

**Project relevance.** Direct reference for Android model packaging, CPU execution, mobile benchmarking and the size–latency trade-off.

**Scope and limitations.** Image classification on Pixel 6 rather than speech generation on the target devices.

#### 20. On-Device Deep Learning for RIS Beamforming: Design and Latency-Rate Trade-Offs

- **Authors:** Luca Urbinati; Nicolò Decarli; Francesco Guidi; Anna Guerra; Barbara Mavì Masini; Alberto Zanella
- **Year:** 2026
- **Venue / publisher:** IEEE Open Journal of the Communications Society
- **Publication status:** Journal
- **DOI:** [`10.1109/OJCOMS.2026.3687306`](https://doi.org/10.1109/OJCOMS.2026.3687306)
- **Publication URL:** [https://doi.org/10.1109/OJCOMS.2026.3687306](https://doi.org/10.1109/OJCOMS.2026.3687306)
- **Local file:** [`20_LiteRT_INT8_Edge_Deployment.pdf`](20_LiteRT_INT8_Edge_Deployment.pdf)
- **Role:** LiteRT/Android

**Summary.** Investigates on-device neural-network control for reconfigurable intelligent surfaces, using LiteRT conversion and full-INT8 quantization in a microcontroller-oriented pipeline. It measures how model capacity, inference latency, RAM/Flash usage and task-level performance trade off on actual embedded hardware.

**Project relevance.** Strong LiteRT quantization and hardware-aware evaluation method reference; distinguish CPU/MCU memory constraints from Snapdragon Android execution.

**Scope and limitations.** TinyML microcontrollers and beamforming, not Android, XNNPACK or TTS.

#### 21. Implementation of Machine Learning Classification for Non-Communicable Diseases in Mobile Applications

- **Authors:** Faisal Rahutomo; Sutrisno; Bambang Harjito
- **Year:** 2026
- **Venue / publisher:** Egyptian Informatics Journal (Elsevier)
- **Publication status:** Journal
- **DOI:** [`10.1016/j.eij.2026.100987`](https://doi.org/10.1016/j.eij.2026.100987)
- **Publication URL:** [https://doi.org/10.1016/j.eij.2026.100987](https://doi.org/10.1016/j.eij.2026.100987)
- **Local file:** [`21_Android_TFLite_Mobile_Implementation.pdf`](21_Android_TFLite_Mobile_Implementation.pdf)
- **Role:** LiteRT/Android

**Summary.** Builds a native Kotlin Android application integrating TensorFlow Lite models and tests computation/UI behavior on a Snapdragon 439 smartphone with 4 GB RAM. Its measurements include inference time, CPU use and UI rendering statistics, providing a practical example of offline application integration.

**Project relevance.** Supports discussion of application-level constraints on modest Android hardware and separation of inference and UI responsiveness.

**Scope and limitations.** Tabular health classification, not a 335M-parameter flow-matching speech model; reported RAM use was not measured.


## B. Supplementary literature (5 papers)

These are useful for additional context but are not part of the core 21-paper shortlist.

#### S01. Empirical Guidelines for Deploying LLMs onto Resource-Constrained Edge Devices

- **Authors:** Ruiyang Qin et al.
- **Year:** 2025
- **Venue / publisher:** ACM publication
- **Publication status:** Journal
- **DOI:** [`10.1145/3736721`](https://doi.org/10.1145/3736721)
- **Publication URL:** [https://doi.org/10.1145/3736721](https://doi.org/10.1145/3736721)
- **Local file:** [`S01_Edge_LLM_Deployment_Guidelines.pdf`](supplementary/S01_Edge_LLM_Deployment_Guidelines.pdf)
- **Role:** Supplementary

**Summary.** Studies deployment choices and performance bottlenecks for local large-language-model inference on memory-limited edge devices, providing practical guidance for selecting hardware and inference settings.

**Project relevance.** Supplementary framing for memory budgeting and performance methodology.

**Scope and limitations.** LLM token decoding is not DiT mel synthesis.

#### S02. Voicebox: Text-Guided Multilingual Universal Speech Generation at Scale

- **Authors:** Matthew Le et al.
- **Year:** 2023
- **Venue / publisher:** NeurIPS 2023 (Advances in Neural Information Processing Systems)
- **Publication status:** Conference
- **DOI:** [`10.52202/075280-0618`](https://doi.org/10.52202/075280-0618)
- **Publication URL:** [https://proceedings.neurips.cc/paper_files/paper/2023/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html](https://proceedings.neurips.cc/paper_files/paper/2023/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html)
- **Local file:** [`S02_Voicebox_Speech_Generation.pdf`](supplementary/S02_Voicebox_Speech_Generation.pdf)
- **Role:** Supplementary

**Summary.** Introduces text-guided multilingual speech generation with non-autoregressive flow matching and audio-context conditioning; includes speech infilling and zero-shot-style generative capabilities.

**Project relevance.** Historical context for flow-matching audio models before F5-TTS.

**Scope and limitations.** No Android LiteRT deployment.

#### S03. Controllable Timbre Cloning and Style Replication with Reference Speech Examples for Multimodal Human–Computer Interaction

- **Authors:** Tianwei Lan; Yuhang Guo; Mengyuan Deng; Jing Wang; Wenwu Wang; Chong Feng
- **Year:** 2025
- **Venue / publisher:** Neurocomputing (Elsevier)
- **Publication status:** Journal
- **DOI:** [`10.1016/j.neucom.2025.132529`](https://doi.org/10.1016/j.neucom.2025.132529)
- **Publication URL:** [https://doi.org/10.1016/j.neucom.2025.132529](https://doi.org/10.1016/j.neucom.2025.132529)
- **Local file:** [`S03_Controllable_Timbre_Cloning.pdf`](supplementary/S03_Controllable_Timbre_Cloning.pdf)
- **Role:** Supplementary

**Summary.** Studies controllable speaker timbre and speaking-style replication using separate reference characteristics, emphasizing the disentangling and recombination of identity and style in generated speech.

**Project relevance.** Relevant if the review examines timbre similarity, expressiveness, or prompt design.

**Scope and limitations.** Not about mobile optimization or LiteRT.

#### S04. A Multi-Level Expressive Voice Cloning Method Based on Adaptive Grouped Code Modeling

- **Authors:** Yan Zhu; Rui Zhou; Gang Chen
- **Year:** 2026
- **Venue / publisher:** IEEE Access
- **Publication status:** Journal
- **DOI:** [`10.1109/ACCESS.2026.3691952`](https://doi.org/10.1109/ACCESS.2026.3691952)
- **Publication URL:** [https://doi.org/10.1109/ACCESS.2026.3691952](https://doi.org/10.1109/ACCESS.2026.3691952)
- **Local file:** [`S04_Expressive_Voice_Cloning.pdf`](supplementary/S04_Expressive_Voice_Cloning.pdf)
- **Role:** Supplementary

**Summary.** Proposes adaptive grouped-code modeling to improve controllability over expressive features such as rhythm, pitch, and intensity while cloning a target voice.

**Project relevance.** Supports optional evaluation of expressive and prosodic quality after deployment optimization.

**Scope and limitations.** No direct IndicF5 or Android LiteRT results.

#### S05. Gen AI Driven Multilingual Audio Dubbing and Synthesis System for Cross-Language Video Platforms

- **Authors:** Rishabh Kannojia; Anuj Kumar Singh; Ishaan Sharma; Shivani Gupta
- **Year:** 2025
- **Venue / publisher:** Results in Engineering (Elsevier)
- **Publication status:** Journal
- **DOI:** [`10.1016/j.rineng.2025.106241`](https://doi.org/10.1016/j.rineng.2025.106241)
- **Publication URL:** [https://doi.org/10.1016/j.rineng.2025.106241](https://doi.org/10.1016/j.rineng.2025.106241)
- **Local file:** [`S05_Multilingual_Audio_Dubbing.pdf`](supplementary/S05_Multilingual_Audio_Dubbing.pdf)
- **Role:** Supplementary

**Summary.** Presents a multilingual dubbing workflow combining speech recognition, translation, and synthesis for cross-language video content. The work motivates practical use of multilingual speech generation in accessibility and content delivery.

**Project relevance.** Application context for multilingual voices and the educational/communications setting.

**Scope and limitations.** Application pipeline differs from offline IndicF5 neural inference and device-level optimization.

## C. Comparative literature matrix

| # | Method / paper | Platform studied | Quantization / optimization | Most useful comparison |
|---|---|---|---|---|
| 01 | Pivot-FSOF: A Full-Stack Optimization Framework for Real-Time DiT-Based TTS on Edge Devices | NVIDIA Jetson AGX Orin / CUDA | pruning, INT8, CUDA graphs | nearest edge-DiT TTS precedent |
| 02 | F5-TTS: A Fairytaler that Fakes Fluent and Faithful Speech with Flow Matching | Research TTS system | DiT, Sway Sampling | base architecture |
| 03 | Staged Depth-Pruning Distillation of a Flow-Matching Text-to-Speech Teacher: A Compact Hindi Speech Synthesizer | GPU Hindi student models | depth-pruning distillation | IndicF5 model reduction |
| 04 | Harmonizing Spectral Evolution in Conditional Flow Matching for TTS | Flow-matching TTS models | frequency-selective ODE intervention | IndicF5 acoustic step optimization |
| 05 | QuantEdge: A Hybrid Quantization Approach for Optimized AI Deployment Across Edge Devices | Heterogeneous edge platforms | hybrid edge quantization | INT8 trade-off |
| 06 | Flow Matching for Generative Modeling | Foundational generative modeling | conditional vector-field learning | mathematical justification |
| 07 | Vocos: Closing the Gap Between Time-Domain and Fourier-Based Neural Vocoders for High-Quality Audio Synthesis | Fourier vocoding | spectral neural vocoder | audio reconstruction |
| 08 | ZMM-TTS: Zero-Shot Multilingual and Multispeaker Speech Synthesis Conditioned on Self-Supervised Discrete Speech Representations | Multilingual TTS | self-supervised representations | cross-lingual evaluation |
| 09 | Matcha-TTS: A Fast TTS Architecture with Conditional Flow Matching | Flow-matching TTS | OT-CFM ODE decoder | step efficiency |
| 10 | FlashSpeech: Efficient Zero-Shot Speech Synthesis | Zero-shot speech models | efficient zero-shot inference | fast zero-shot generation |
| 11 | Voice Cloning: A Survey of Zero-Shot and Controllable Speech Synthesis | Survey | classification of techniques | taxonomy/evaluation |
| 12 | U-Style: Cascading U-nets with Multi-Level Speaker and Style Modeling for Zero-Shot Voice Cloning | Zero-shot voice cloning | multi-level speaker/style features | speaker similarity |
| 13 | PerTTS: Personalized and Controllable Zero-Shot Spontaneous Style Text-to-Speech Synthesis | Expressive zero-shot TTS | spontaneous style control | prosody/style |
| 14 | Sometimes Painful but Promising: Feasibility and Trade-Offs of On-Device Language Model Inference | On-device language models | device profiling | memory/latency framing |
| 15 | SIMD-CP: SIMD with Redundant Bits Compression and Mixed-Precision Packing for Quantized DNNs | Quantized DNN SIMD | mixed-precision SIMD packing | integer performance |
| 16 | E2 TTS: Embarrassingly Easy Fully Non-Autoregressive Zero-Shot TTS | Alignment-free TTS | non-autoregressive synthesis | F5 architectural predecessor |
| 17 | CMDF-TTS: Text-to-Speech Method with Limited Target Speaker Corpus | Limited-data speech synthesis | speaker-data efficiency | short-reference motivation |
| 18 | Neural Codec Language Models Are Zero-Shot Text to Speech Synthesizers | Neural-codec TTS | autoregressive codec tokens | contrasting model family |
| 19 | EinsteinNet and State-of-the-Art ML Models for Android-Based Orange Classification: Integration, Evaluation, and Deployment | Google Pixel 6 / Android | TFLite quantized Android CNNs | mobile model-size vs latency |
| 20 | On-Device Deep Learning for RIS Beamforming: Design and Latency-Rate Trade-Offs | Embedded microcontrollers / LiteRT Micro | full-INT8 LiteRT microcontroller | LiteRT hardware-aware calibration |
| 21 | Implementation of Machine Learning Classification for Non-Communicable Diseases in Mobile Applications | Snapdragon 439 / Kotlin Android | native Kotlin and TFLite | budget Android application benchmarking |

## D. Research synthesis and outstanding questions

The selected literature demonstrates *separate* advances in (a) DiT-TTS optimization (01), (b) IndicF5 compression and inference improvements (03–04), (c) quantized inference (05, 15, 20), and (d) Android/TFLite integration (19, 21). The selected works do not individually document deployment of IndicF5 via LiteRT on native Android. This is an observation about the present reference set, not a claim of universal novelty.

Research questions arising from the reviewed methods:

1. How much model-size reduction and mel/speaker-quality change follow post-training INT8 export of IndicF5 and Vocos?
2. Which native runtime operations dominate end-to-end audio generation, and how do XNNPACK delegation, worker threads and fixed shapes influence latency?
3. How do 12/16/24 inference steps trade generated-audio quality for total synthesis time on a Snapdragon device?
4. Can reference-mel caching, fixed-window chunking and audio stitching support longer utterances at bounded peak memory?
5. How do performance and stability differ between flagship and low-budget Android systems?

Device-specific results from the accompanying engineering report represent primary project experiments and are distinct from published results in this collection.

## E. Thematic classification

| Research theme | References | Scope |
|---|---|---|
| Zero-shot and multilingual TTS | 11, 08, 12, 13, 17, 18 | Speaker adaptation, multilingual challenges, and architectural alternatives |
| Foundations of flow-matching speech synthesis | 06, 09, 16, 02 | Mathematical formulation, simplified F5 pipeline, and sampling |
| IndicF5-specific efficiency | 03, 04; separate IndicF5 model citation | Pruning/distillation, spectral interventions, and runtime optimization |
| Vocoding | 07 | Fourier-domain reconstruction and the Vocos synthesis stage |
| Edge compression and hardware | 01, 05, 15, 14 | Inference steps, quantization, arithmetic throughput, and memory |
| LiteRT and Android execution | 19, 20, 21 | Model conversion, physical-device measurement, and distinction between microcontroller and Android inference |
| Research gap / contribution | All above selectively | Relationship of the implemented LiteRT/IndicF5 Android system to the selected prior work |



