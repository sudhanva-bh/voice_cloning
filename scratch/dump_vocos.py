import numpy as np
import soundfile as sf
import torch
from ai_edge_litert.interpreter import Interpreter

VOCOS_PATH = '/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_vocos_int8.tflite'
vocos = Interpreter(model_path=VOCOS_PATH)
vocos.allocate_tensors()
vin = vocos.get_input_details()
vout = vocos.get_output_details()

np.random.seed(42)
dummy_mel = np.random.randn(1, 100, 512).astype(np.float32)
vocos.set_tensor(vin[0]['index'], dummy_mel)
vocos.invoke()
spec = vocos.get_tensor(vout[0]['index']) # [1, 2, 513, 512]

# Save spec to binary file
with open('/mnt/c/voice_cloning/scratch/debug_vocos_spec.bin', 'wb') as f:
    f.write(spec.astype(np.float32).tobytes())

# Compute PyTorch istft
real = torch.from_numpy(spec[0, 0, :, :])
imag = torch.from_numpy(spec[0, 1, :, :])
complex_spec = torch.complex(real, imag)
win = torch.hann_window(1024)
wav_py = torch.istft(complex_spec, n_fft=1024, hop_length=256, win_length=1024, window=win, center=True).numpy()

# Peak normalize
peak = np.max(np.abs(wav_py))
if peak > 1e-4:
    wav_py = wav_py * (0.95 / peak)

sf.write('/mnt/c/voice_cloning/scratch/debug_vocos_py.wav', wav_py, 24000)
print('Wrote debug_vocos_spec.bin and debug_vocos_py.wav! Shape:', wav_py.shape)
