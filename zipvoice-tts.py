#!/usr/bin/env python3
#
# Copyright (c)  2026  Xiaomi Corporation

"""
This file demonstrates how to use sherpa-onnx Python API
for Chinese/English zero-shot TTS with ZipVoice.


Usage:

wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-zipvoice-distill-int8-zh-en-emilia.tar.bz2
tar xvf sherpa-onnx-zipvoice-distill-int8-zh-en-emilia.tar.bz2
rm sherpa-onnx-zipvoice-distill-int8-zh-en-emilia.tar.bz2

wget https://github.com/k2-fsa/sherpa-onnx/releases/download/vocoder-models/vocos_24khz.onnx

python3 ./python-api-examples/zipvoice-tts.py

You can find more models at
https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models

Please see
https://k2-fsa.github.io/sherpa/onnx/tts/zipvoice.html
for details.

"""

from email.mime import audio
import time
from pathlib import Path

import librosa
import sherpa_onnx
import soundfile as sf
from datetime import datetime


def create_tts():
    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(
                tokens="./sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/tokens.txt",
                encoder="./sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/encoder.int8.onnx",
                decoder="./sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/decoder.int8.onnx",
                data_dir="./sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/espeak-ng-data",
                lexicon="./sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/lexicon.txt",
                vocoder="./vocos_24khz.onnx",
            ),
            debug=False,
            num_threads=2,
            provider="cpu",
        )
    )
    if not tts_config.validate():
        raise ValueError(
            "Please read the previous error messages and re-check your config"
        )

    return sherpa_onnx.OfflineTts(tts_config)


def main():
    reference_audio_file = (
        # "./samples/sudheendra_voice_clone_2.wav"
        "./samples/vamsi.ogg"
    )
    if not Path(reference_audio_file).is_file():
        raise ValueError(f"Reference audio {reference_audio_file} does not exist")

    tts = create_tts()

    reference_audio, sample_rate = librosa.load(reference_audio_file, sr=None)
    reference_text = "The quick brown fox jumps over the lazy dog while the morning sun rises slowly over the quiet hills, casting long golden shadows across the valley. I am having breakfast at the lovely sunset."
    text = "Hello guys, Vamsi here. Remember the girl whose date of birth I asked? Well, now we are together. Feel jealous you single guys. I am going on a date now. hahaha"

    gen_config = sherpa_onnx.GenerationConfig()
    gen_config.reference_audio = reference_audio
    gen_config.reference_sample_rate = sample_rate
    gen_config.reference_text = reference_text
    gen_config.num_steps = 4
    gen_config.extra["min_char_in_sentence"] = "30"

    start = time.time()
    audio = tts.generate(text, gen_config)
    end = time.time()

    if len(audio.samples) == 0:
        print("Error in generating audios. Please read previous error messages.")
        return

    elapsed_seconds = end - start
    audio_duration = len(audio.samples) / audio.sample_rate
    real_time_factor = elapsed_seconds / audio_duration

    output_dir = Path("./generated")
    output_dir.mkdir(exist_ok=True)

    reference_name = Path(reference_audio_file).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = output_dir / f"{reference_name}_{timestamp}.wav"

    sf.write(
        output_filename,
        audio.samples,
        samplerate=audio.sample_rate,
        subtype="PCM_16",
    )
    print(f"Saved to {output_filename}")
    print(f"The text is '{text}'")
    print(f"Elapsed seconds: {elapsed_seconds:.3f}")
    print(f"Audio duration in seconds: {audio_duration:.3f}")
    print(f"RTF: {elapsed_seconds:.3f}/{audio_duration:.3f} = {real_time_factor:.3f}")


if __name__ == "__main__":
    main()
