# On-Device Multilingual Voice Cloning — revised presentation

15 slides, 16:9. Presenter: Sudhanva B H. This specification provides all audience-facing copy under **Slide text**, in reading order. Text before ` | ` is a card heading or table key. Presenter notes are separate.

## Art direction and slide pacing

Use the supplied 16-page PDF as the visual foundation. Preserve the dark bookends, off-white content pages, compact numbered section labels, aligned cards, navy callout bands, and blue data accents. Reuse the cover's split text/device composition, the original problem slide's three cards, the architecture slide's layered flow, and the results slide's tabular treatment. Replace the old output screenshot placeholder with the current app capture. Retire standalone literature, solver formula, low-step ablation, and thread-scaling pages. Their evidence belongs in the engineering report.

- Canvas 1280 × 720. Use a 64 px left/right margin, 48 px top margin, 24–32 px gutters, and a consistent title baseline. Use warm off-white `#F7F6F2`, dark navy `#0F172A`, royal blue `#2146C7`, orange `#FF5500` for restrained highlights, and green `#087A55` for verified evidence. Cards use white on light pages and `#1E293B` on navy. Use dark navy text on white.
- Use a condensed bold sans (Barlow Condensed or Arial Narrow Bold) for headings at 44–54 px and a legible sans (Inter or Arial) for body at 22–27 px. Section labels are 15–16 px, bold and uppercase. Evidence footers may use 17–19 px. Keep original screenshots proportional. Crop to relevant controls and preserve the dark app theme. Use native Canva text, tables, diagrams, and shapes.
- Read the original cover and closing as bookends. Present slides 2–4 in the first four minutes, the workflow on slides 5–10, then discuss challenges, results, and next work. Use orange for limitations and green only for documented evidence.

## 01. On-Device Multilingual Voice Cloning

**Main message** — The project deploys offline, reference-conditioned speech generation on Android.

**Slide text**
- On-Device Multilingual Voice Cloning
- Offline speech synthesis from a short voice sample and new text
- Sudhanva B H

**Layout** — Navy cover, large two-line title in the left 62%, subtitle beneath, presenter credit below a fine rule. Put the phone screenshot on the right and align it with the title block.

**Diagram or chart** — None.

**Assets** — Use [screen_20261121_174325.png](android/samples/screen_20261121_174325.png) for the device image. Retain the app title and wizard.

**Speaker notes** — Good morning, everyone. I’m Sudhanva B H, and today I’ll present our work on on-device multilingual voice cloning. The idea is simple: give the phone a short recording, tell it what was said in that recording, and then give it something new to say. The app generates the new speech locally on Android. I’ll start with why that’s difficult, then walk through how we built the app and what our measurements tell us about running it on a phone.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §1 and §6.

## 02. The offline voice cloning problem

**Main message** — Local voice cloning must handle language, speaker adaptation, and device constraints at once.

**Slide text**
- 01 / Motivation
- Indian scripts | The system must handle several scripts and speaking rhythms.
- New speakers | A short recording and its transcript provide the voice reference.
- Phone constraints | Models and working memory must fit on the device.
- Example | A teacher records their own voice and generates regional-language lesson audio offline.

**Layout** — Preserve the original problem slide's three white cards, with a navy use-case band below. No decorative icon required.

**Diagram or chart** — Three aligned cards of equal width, without arrows.

**Assets** — None.

**Speaker notes** — Imagine a teacher who wants to turn a written lesson into audio in their own voice. They record a short sample, enter the exact words they spoke, and type the lesson they want narrated. The system has to handle the language of the lesson, pick up the voice characteristics from a short clip, and do the computation within the phone’s memory and CPU limits. We call this zero-shot voice cloning because there’s no separate training step for that speaker. Running all of that locally was the engineering problem we set out to solve.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §1.

## 03. Project evolution

**Main message** — The team established a mobile baseline, verified Indic speech on a laptop, and deployed the Indic model natively on Android.

**Slide text**
- 02 / Previous work
- Flutter + Sherpa-ONNX | ZipVoice-Distill established an English mobile baseline.
- IndicF5 on laptop | PyTorch trials demonstrated Indic-language synthesis and informed duration tuning.
- IndicF5 + LiteRT on Android | Kotlin and C++ run the converted IndicF5 and Vocos models locally.
- An intermediate ONNX export tested model portability before the LiteRT deployment.

**Layout** — Three cards across the center, equal height. Use the strongest royal-blue treatment on the Android card. Put the ONNX note below the middle-to-right transition.

**Diagram or chart** — Connect the three cards with two right arrows. Read left to right. The card copy names the model, runtime, and application technology.

**Assets** — None.

**Speaker notes** — We developed the system in three stages. First, we built a Flutter app and ran ZipVoice-Distill through Sherpa-ONNX. That gave us a working English baseline on Android. Second, we tried IndicF5 on a laptop with PyTorch. Those tests showed that we could generate speech in Indian languages and helped us work out how much audio to allocate for a given line of text. We also exported IndicF5 to ONNX to investigate mobile portability. For the current Android app, we kept IndicF5, moved inference to Google LiteRT, and built the app in Kotlin with a C++ engine. Here’s how those pieces fit together.

**References** — [Timeline](reports/timeline.md) and [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§2–5.

## 04. Current Android architecture

**Main message** — Kotlin coordinates the app and native C++ handles the audio pipeline and LiteRT inference.

**Slide text**
- 03 / Current architecture
- Reference audio + reference transcript + target text
- Android app | Kotlin manages inputs, progress, and output.
- Audio and text preparation | C++ extracts audio features and encodes text. Kotlin splits long text.
- IndicF5 on LiteRT | The speech model generates acoustic features on the phone CPU.
- Vocos on LiteRT | The vocoder and native audio code turn features into sound.
- Generated audio → Playback · WAV download · Share

**Layout** — Stack input and Android app bands at top, followed by three cards in a single row. Place the output band below. Keep arrows outside text boxes.

**Diagram or chart** — Input ↓ Android app ↓ Audio and text preparation → IndicF5 on LiteRT → Vocos on LiteRT ↓ Generated audio and actions. Add a thin navy bracket or band indicating the native C++ inference pipeline beneath the model cards if space permits.

**Assets** — None. Build with editable boxes and arrows.

**Speaker notes** — Start with the three inputs at the top: the recording, its transcript, and the new text. Kotlin manages the app and breaks longer text into pieces. At the preparation stage, our C++ engine extracts features from the recording and converts the text into a form the model can use. LiteRT then runs two models on the phone’s CPU. IndicF5 produces a representation of the new speech, and Vocos helps turn it into a waveform. The app takes the resulting audio and makes it available for playback, download, or sharing. Let’s follow that path from the first screen.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§6 and 10.

## 05. Collect a reference voice

**Main message** — The app needs usable audio and the exact words spoken in it.

**Slide text**
- 04 / Workflow · Reference voice
- Record or import | Use the microphone or select a 24 kHz PCM WAV.
- Enter the transcript | Type the words spoken in the recording.
- Prepare the voice reference | The app checks the inputs and extracts audio features once per generation.

**Layout** — Left half for the three numbered actions. Right half for a large screenshot crop framing Reference Script and Reference Voice Audio. Keep the sample duration visible.

**Diagram or chart** — Stack the three cards top-to-bottom. A small green “ready” cue may be taken from the screenshot.

**Assets** — [screen_20261121_174325.png](android/samples/screen_20261121_174325.png), crop from the top of Reference Script to the bottom of Reference Voice Audio.

**Speaker notes** — Here at the top of the app, I enter the exact words spoken in the reference clip. Then I can record directly into the app or import a 24-kilohertz PCM WAV. The screenshot shows a reference clip ready for preview. This step matters because the recording supplies the voice characteristics, and the transcript tells the model what words those characteristics are attached to. The app checks that it can read the audio and that I’ve entered text. I still need to make sure the transcript matches what I said. Then I can give the app the new words to speak.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §11.

## 06. Enter the target text

**Main message** — Target text specifies what the generated voice will say.

**Slide text**
- 05A / Workflow · Target text
- Type target text | Enter the words you want the voice to say.
- Quick Ideas | Pick a preset and edit it in the target text field.
- Select Generate Cloned Speech to start.

**Layout** — Put the two input options and generation action on the left. Enlarge the Target Speech Text screenshot on the right so the multilingual example and Quick Ideas control are visible.

**Diagram or chart** — None.

**Assets** — [screen_20261121_174730.png](android/samples/screen_20261121_174730.png), cropped to Target Speech Text, Quick Ideas, and the generation controls.

**Speaker notes** — Once the reference is ready, I enter the words I want the model to say. I can type the text directly or pick a Quick Ideas preset and edit it. The screenshot shows a Hindi example in the same field. The reference transcript stays separate because it describes the recording, while the target text specifies the speech the app will generate. When I tap Generate, the app checks how to split the passage for the model.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §18.

## 07. Split longer text into chunks

**Main message** — Each chunk must share the model's fixed audio window with the reference clip.

**Slide text**
- 05B / Workflow · Chunking
- “Open your books. Read the first line.”
- Chunk 1 | Open your books.
- Chunk 2 | Read the first line.
- The app prefers sentence breaks and uses shorter splits when needed.

**Layout** — Show the input sentence pair and the two labeled chunk columns across the upper part of the slide. Place the frame-budget graphic below as a full-width band. Keep the original warm off-white background and blue and orange accents.

**Diagram or chart** — Use the supplied 512-frame budget graphic. The example shows 356 frames used by the reference and 156 frames remaining for target speech. Place a down arrow between the example text and its two ordered chunks.

**Assets** — [Frame-budget graphic](presentations/chunking-frame-budget.png).

**Speaker notes** — IndicF5 has a fixed window of 512 mel frames, about five and a half seconds at this sample rate. The reference and the new speech share that space. In the example at the bottom, a reference of about three point eight seconds uses 356 frames. That leaves 156 frames, or about one point seven seconds, for new speech in that chunk. To handle a paragraph, the app tries sentence breaks first, then clause or word breaks if a segment is still too long. It generates the chunks in order, reusing the same reference features for each one.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §14.

## 08. Generate acoustic features with IndicF5

**Main message** — IndicF5 shapes noise into a speech representation guided by the reference and target text.

**Slide text**
- 06 / Workflow · Neural speech generation
- Start with noise
- Refine using the voice reference and target text
- Produce acoustic features for the new speech
- IndicF5 uses a Diffusion Transformer and Continuous Flow Matching.
- Google LiteRT runs the converted pretrained model on Android.

**Layout** — Three-stage sequence in the middle with one navy text band underneath. Use larger text on the three stage cards and ample space around arrows.

**Diagram or chart** — Noise → Guided refinement → Acoustic features. Add the actual input names to the middle card rather than a tensor diagram.

**Assets** — None.

**Speaker notes** — For each chunk, IndicF5 starts with noise and gradually shapes it into a representation of speech. The voice reference guides how the result should sound, and the target text guides what it should say. The Diffusion Transformer predicts how to change that representation at each step. Continuous Flow Matching is the method behind those predictions, and our C++ sampler applies them step by step. We used a pretrained IndicF5 model and adapted it to run on Android through LiteRT. At this point we have acoustic features, and the next step is making them audible.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§7 and 12. [F5-TTS paper](https://aclanthology.org/2025.acl-long.313/).

## 09. Reconstruct and join the waveform

**Main message** — Vocos and the native audio pipeline create a playable clip from the generated features.

**Slide text**
- 07 / Workflow · Waveform generation
- Decode | Vocos predicts a frequency representation from the acoustic features.
- Reconstruct | Native audio code turns that representation into a waveform.
- Join | Short fades and pauses connect the chunks into one clip.

**Layout** — Three horizontal steps inside a dark band. Below, show two labeled chunk blocks separated by a small gap and an arrow to one final WAV label.

**Diagram or chart** — Acoustic features → Vocos → Native waveform reconstruction. Lower strip: Chunk 1 · short pause · Chunk 2 → One WAV clip. Use labeled bars as an illustration, with no measured signal axis.

**Assets** — None.

**Speaker notes** — Vocos takes those acoustic features and predicts a frequency representation. Our native audio code reconstructs a waveform from it and keeps the portion corresponding to the new speech. When there are several chunks, the app joins the waveforms in order. It trims excess silence, gently fades the edges of each chunk, and inserts brief pauses. The short tail at the end gives the final sounds room to decay. The result is one WAV file, even when the original text needed several passes through the model.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§13–14.

## 10. Play, save, and share

**Main message** — The app tracks generation and saves the finished WAV in a local library.

**Slide text**
- 08 / Workflow · Playback and export
- During generation | Follow progress by chunk and cancel if needed.
- After generation | Play or seek, revisit saved clips, and see the run’s RTF and memory reading.
- Take the WAV with you | Download the clip or share it through Android.
- Latest saved clip shown

**Layout** — Use three white cards on the left and a large crop of Generated Speech & Library on the right. Use a caption if the crop includes live telemetry.

**Diagram or chart** — None.

**Assets** — [screen_20261121_174707.png](android/samples/screen_20261121_174707.png), crop to Generated Speech & Library and seek bar. The crop illustrates the player. Action buttons below the supplied capture are described in the slide copy.

**Speaker notes** — While the phone is generating speech, the app shows which chunk is in progress. I can cancel from that screen if I need to. Once the WAV is saved, I can listen, seek to a different point, or come back to it later in the local library. I can also download the WAV or send it through Android’s share menu. The player displays the saved run’s real-time factor and its memory reading. Those figures belong to that particular clip. I’ll explain how to interpret them when we get to the results.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§17–18.

## 11. Fitting the models on Android

**Main message** — Direct LiteRT conversion and INT8 weight quantization cut the stored model size by about 75%.

**Slide text**
- 09 / Engineering · Model size and memory
- Problem | The two FP32 model files total 1,339.54 MiB.
- Solution | Convert to LiteRT and store eligible weights at 8-bit precision.
- Outcome | The two Android model assets total 341.20 MiB, a 74.5% reduction.
- FP32 model files | 1,339.54 MiB
- INT8 model files | 341.20 MiB
- Model file sizes are separate from process memory measurements.

**Layout** — Three short Problem / Solution / Outcome rows on the left. Place a two-bar comparison on the right, above the file-vs-memory footnote.

**Diagram or chart** — Horizontal bars with a shared zero baseline, max 1,340 MiB. FP32 slate, INT8 royal blue. Print exact values beside bars.

**Assets** — None.

**Speaker notes** — One of the first challenges was the size of the models. Together, the two full-precision files take about thirteen hundred and forty mebibytes. We converted the pretrained models to LiteRT and stored eligible weights at eight-bit precision. The two model files packaged in the Android app now total about three hundred and forty-one mebibytes. That’s a reduction of seventy-four point five percent. These bars compare file sizes on disk. When the app runs, it also needs memory for the interpreter, intermediate data, and the rest of the Android process. We measure that separately.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§8 and 19.

## 12. Speed, stability, and longer speech

**Main message** — The mobile implementation balances compute, stable output, and the fixed model window.

**Slide text**
- 10 / Engineering · Runtime trade-offs
- CPU cost | Five XNNPACK threads and selectable step counts let the app trade compute time for quality.
- Fixed model window | Reuse the prepared voice reference, synthesize chunks in order, and stitch the waveform.
- Audio artifacts | Limit extreme values in the solver and preserve the ends of clips with trimming and padding.
- Android integration | Build the interpreter once per model and reuse its tensor allocation during inference.

**Layout** — Use a two-by-two grid. In each card, set the issue in blue and its implementation below in navy. Small orange accent on the audio artifacts card.

**Diagram or chart** — None. The process diagrams on slides 4 and 8 already show how these pieces connect.

**Assets** — None.

**Speaker notes** — Getting the models onto the phone was one part of the job. The app also has to run them repeatedly for every chunk. We use five XNNPACK threads on the CPU and offer twelve, sixteen, or twenty-four generation steps, with sixteen as the default. To avoid extra work on paragraphs, we prepare the reference features once per generation and reuse them across chunks. We limit extreme values during sampling and use trimming and padding to protect the ends of clips. We also allocate the model tensors when the interpreters start, then reuse that allocation during generation. Here’s what an earlier device benchmark recorded.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§10 and 12–17.

## 13. What the Galaxy S23 benchmark showed

**Main message** — The report documents offline synthesis and paragraph output, with generation slower than playback.

**Slide text**
- 11 / Results · Reported device benchmark
- Galaxy S23 · Snapdragon 8 Gen 2 · 8 GB · Android 16 · 5 XNNPACK threads · 16 steps reported
- Tested in the reported suite | English, Hindi, Telugu and Tamil
- Tamil short | 2.40 s audio · 3.81 s generation · 1.58× RTF · 380 MB
- Tamil paragraph | 16.10 s audio · 24.47 s generation · 1.52× RTF · 388 MB
- Across 12 reported runs | 1.50–1.64× RTF · 378–389 MB peak VmRSS
- RTF = generation time ÷ audio duration. Above 1 means slower than real time.

**Layout** — Device line directly under heading. Put the two Tamil rows in a clean comparison table with four aligned metric columns. Blue RTF values and an orange explanation band.

**Diagram or chart** — Table columns: Test, Audio, Generation, RTF, Peak VmRSS. Use the last two lines as callouts. Keep the range visually subordinate to the rows.

**Assets** — None.

**Speaker notes** — This table shows the archived Galaxy S23 benchmark. The reported setup used a Snapdragon 8 Gen 2, Android 16, and five XNNPACK threads. The team ran English, Hindi, Telugu, and Tamil examples. For Tamil, the short clip took about three point eight seconds to produce two point four seconds of audio. The paragraph took about twenty-four and a half seconds to produce just over sixteen seconds of speech. Real-time factor, or RTF, is generation time divided by audio duration. A factor of one point five means a second of audio takes about one and a half seconds to generate. The archived suite reported peak resident memory between three hundred and seventy-eight and three hundred and eighty-nine megabytes. Those numbers describe that benchmark. The recent app captures tell a different story.

**References** — [LiteRT report §9](litert_docs/LITERT_COMPREHENSIVE_ENGINEERING_REPORT.md#9-quantitative-empirical-benchmarks--hardware-performance-profiles) and [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §19.

## 14. What the evidence establishes

**Main message** — Conversion parity, deployment verification, and current app readings answer different questions.

**Slide text**
- 12 / Results · Quality and reproducibility
- FP32 conversion parity | 0.0037 dB spectral distortion in the desktop comparison with PyTorch.
- INT8 parity | 0.99923 average velocity cosine similarity versus LiteRT FP32 in the eight-step test.
- Recent app captures | 7.88× and 11.77× RTF, with 933 and 812 MB displayed, respectively.
- Repeat instrumented device tests and add listener, intelligibility, and speaker-similarity evaluation.

**Layout** — Put the two parity findings in white cards with green labels. Put recent telemetry in an adjacent navy card and the validation action across the bottom.

**Diagram or chart** — Evidence cards with their comparison baselines. Avoid charting run groups together because the protocols differ.

**Assets** — None. The source screenshots are used on workflow slides and linked in the report.

**Speaker notes** — The first two results here are desktop checks of model conversion. In the full-precision comparison with PyTorch, the spectral difference was very small. In the eight-bit comparison, the model’s predicted updates pointed in almost the same direction as the full-precision LiteRT model’s updates. Those comparisons tell us how closely the conversions track their baselines. To judge naturalness, intelligibility, and speaker similarity, we need separate tests. The recent app captures show real-time factors of seven point eight eight and eleven point seven seven, with memory readings of nine hundred and thirty-three and eight hundred and twelve megabytes. Those memory readings are single samples after generation, and the captures lack the device and build details we need for a direct comparison. The next step is to repeat the benchmark with those conditions recorded.

**References** — [Phase 2](litert_docs/phase_wise_implementation/phase_2_report.md), [Phase 3](litert_docs/phase_wise_implementation/phase_3_report.md), and [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §§9 and 19.

## 15. Offline Indic voice cloning on Android

**Main message** — The project delivered an offline Android pipeline and identified the work needed to make it faster and better measured.

**Slide text**
- 13 / Conclusion
- Delivered | Pretrained IndicF5 and Vocos on Android with local generation, paragraph support, playback, and WAV export.
- Current limits | Generation can take longer than playback. Performance varies across observed runs.
- Next work | Reproduce benchmarks across devices, test lower-step and accelerator paths, and measure speech quality with listeners.

**Layout** — Return to navy. Place the main title above three horizontal summary cards as on the original closing page. Give “Delivered” green and “Current limits” orange. Leave room below for audience questions.

**Diagram or chart** — None.

**Assets** — None.

**Speaker notes** — To wrap up, we took a pretrained voice model and built an Android pipeline that can generate speech offline from a recording, its transcript, and new text. The app can handle paragraphs by generating chunks and joining them, and it gives the user a WAV they can play, download, or share. The measurements show that generation can take longer than playback and that performance varies across runs. The next priorities are to reproduce the device benchmarks, test faster generation settings and hardware acceleration, and evaluate speech quality with listeners. Thank you for listening. I’d be happy to take questions.

**References** — [Engineering report](TECHNICAL_DOCUMENTATION_REVISED.md), §20.
