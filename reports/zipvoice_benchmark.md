Confirmed: **ZipVoice-Distill, INT8, ~104MB, 123M base params, NAR flow-matching (Zipformer backbone), trained on Emilia, zero-shot cloning.** This actually changes an earlier finding — ZipVoice *is* a genuine NAR cloning model already integrated in sherpa-onnx, correcting the "sherpa-onnx has no cloning models" claim from earlier research. Worth noting for the deck. Now the prefilled table:

**Slide 6 — English Model Benchmark (prefilled, ready for you to fill measured columns)**

Context line: *Model tested: ZipVoice-Distill (int8, Emilia-trained) — a zero-shot voice-cloning model natively supported by sherpa-onnx, correcting the earlier assumption that no sherpa-onnx model does true cloning.*

| Device | SoC | RAM | NPU? | Model | Params (M) | INT8 Size (MB) | Architecture | Text Length | RTF (median) | RTF (P90) | Peak RSS (MB) | Cold Load (ms) | Pass/Fail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Galaxy S23 | Snapdragon 8 Gen 2 | 8GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Short | | | | | |
| Galaxy S23 | Snapdragon 8 Gen 2 | 8GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Medium | | | | | |
| Galaxy S23 | Snapdragon 8 Gen 2 | 8GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Long | | | | | |
| Galaxy Tab S9 FE+ | Exynos 1380 | 6–12GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Short | | | | | |
| Galaxy Tab S9 FE+ | Exynos 1380 | 6–12GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Medium | | | | | |
| Galaxy Tab S9 FE+ | Exynos 1380 | 6–12GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Long | | | | | |
| Galaxy M53 | Dimensity 900 | 6–8GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Short | | | | | |
| Galaxy M53 | Dimensity 900 | 6–8GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Medium | | | | | |
| Galaxy M53 | Dimensity 900 | 6–8GB | Yes | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Long | | | | | |
| POCO C71 | Unisoc T7250 | 3–6GB | No | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Short | | | | | |
| POCO C71 | Unisoc T7250 | 3–6GB | No | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Medium | | | | | |
| POCO C71 | Unisoc T7250 | 3–6GB | No | ZipVoice-Distill | 123 | ~104 | NAR, flow-matching (Zipformer) | Long | | | | | |

One note: the sherpa-onnx repo lists ZipVoice-Distill's int8 size as **~104 MB** for the zh-en Emilia release — flag if the exact variant/filename you used differs, and I'll adjust the number before it goes on the slide.

Should Part 1's "no sherpa-onnx model does cloning" claim also get corrected on Slide 9, since ZipVoice contradicts it directly?