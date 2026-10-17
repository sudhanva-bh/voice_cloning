import soundfile as sf
import numpy as np
from transformers import pipeline

pipe = pipeline('automatic-speech-recognition', model='openai/whisper-tiny')
for path in ['/mnt/c/voice_cloning/scratch/parity_test/litert_int8.wav', 
             '/mnt/c/voice_cloning/scratch/parity_test/test_new_inlined.wav', 
             '/mnt/c/voice_cloning/scratch/test_py_device_match.wav']:
    try:
        data, sr = sf.read(path)
        res = pipe({'raw': data.astype(np.float32), 'sampling_rate': sr})
        print(f'{path}: "{res["text"]}"')
    except Exception as e:
        print(f'{path}: error {e}')
