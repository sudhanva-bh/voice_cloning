import soundfile as sf
import numpy as np
import glob
from transformers import pipeline

pipe = pipeline('automatic-speech-recognition', model='openai/whisper-tiny')

for f in sorted(glob.glob('/mnt/c/voice_cloning/scratch/parity_test/*.wav')):
    data, sr = sf.read(f)
    if data.ndim > 1: data = data[:, 0]
    res = pipe({'raw': data.astype(np.float32), 'sampling_rate': sr})
    print(f'{f.split("/")[-1]}: {len(data)/sr:.2f}s, rms={np.sqrt(np.mean(data**2)):.4f}, text="{res["text"].strip()}"')

data, sr = sf.read('/mnt/c/voice_cloning/scratch/mobile_generated_voice.wav')
if data.ndim > 1: data = data[:, 0]
res = pipe({'raw': data.astype(np.float32), 'sampling_rate': sr})
print(f'mobile_generated_voice.wav: {len(data)/sr:.2f}s, rms={np.sqrt(np.mean(data**2)):.4f}, text="{res["text"].strip()}"')
