import numpy as np
import soundfile as sf
import torch
from ai_edge_litert.interpreter import Interpreter
import sys
sys.path.insert(0, '/mnt/c/voice_cloning')
from scripts.infer_litert import load_vocab, extract_mel_spectrogram

DIT_PATH = '/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_dit_int8.tflite'
VOCOS_PATH = '/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_vocos_int8.tflite'
VOCAB_PATH = '/mnt/c/voice_cloning/android/app/src/main/assets/vocab.txt'
REF_AUDIO_PATH = '/mnt/c/voice_cloning/android/app/src/main/assets/samples/ref_en.wav'

ref_text = 'Some call me nature.'
gen_text = 'Google LiteRT is fast and clear.'
num_steps = 8
cfg_strength = 2.0
sway_coef = -1.0
seed = 42

vocab = load_vocab(VOCAB_PATH)
ref_mel, _ = extract_mel_spectrogram(REF_AUDIO_PATH)
ref_mel_np = ref_mel.numpy().T # [T, 100]
ref_frames = ref_mel_np.shape[0]

print(f'ref_frames: {ref_frames}')

full_text = f'{ref_text.strip()} {gen_text.strip()}'
tokens = [vocab.get(c, -1) for c in full_text]
tokens = tokens[:128] + [-1] * max(0, 128 - len(tokens))
text_tokens = np.array([tokens], dtype=np.int32)
null_text = np.full((1, 128), -1, dtype=np.int32)

cond_mel = np.zeros((1, 512, 100), dtype=np.float32)
cond_mel[0, :ref_frames, :] = ref_mel_np
null_cond = np.zeros((1, 512, 100), dtype=np.float32)

np.random.seed(seed)
mel_out = np.random.randn(1, 512, 100).astype(np.float32)

# Sway schedule
t_steps = [i / num_steps for i in range(num_steps + 1)]
t_steps = [t + sway_coef * (np.cos(np.pi / 2 * t) - 1 + t) for t in t_steps]

dit = Interpreter(model_path=DIT_PATH)
dit.allocate_tensors()
din = dit.get_input_details()
dout = dit.get_output_details()

for step in range(num_steps):
    t_val = np.array([t_steps[step]], dtype=np.float32)
    dt = t_steps[step + 1] - t_steps[step]

    # cond
    dit.set_tensor(din[0]['index'], mel_out)
    dit.set_tensor(din[1]['index'], cond_mel)
    dit.set_tensor(din[2]['index'], text_tokens)
    dit.set_tensor(din[3]['index'], t_val)
    dit.invoke()
    v_cond = dit.get_tensor(dout[0]['index']).copy()

    # null
    dit.set_tensor(din[0]['index'], mel_out)
    dit.set_tensor(din[1]['index'], null_cond)
    dit.set_tensor(din[2]['index'], null_text)
    dit.set_tensor(din[3]['index'], t_val)
    dit.invoke()
    v_null = dit.get_tensor(dout[0]['index']).copy()

    v = v_cond + (v_cond - v_null) * cfg_strength
    mel_out += dt * v
    print(f'Step {step+1}/{num_steps}: |v_cond|={np.linalg.norm(v_cond):.2f}, |v_null|={np.linalg.norm(v_null):.2f}, |v|={np.linalg.norm(v):.2f}')

mel_out[0, :ref_frames, :] = cond_mel[0, :ref_frames, :]

# Run Vocos INT8
vocos = Interpreter(model_path=VOCOS_PATH)
vocos.allocate_tensors()
vin = vocos.get_input_details()
vout = vocos.get_output_details()

voc_in = np.transpose(mel_out, (0, 2, 1))
vocos.set_tensor(vin[0]['index'], voc_in)
vocos.invoke()
spec = vocos.get_tensor(vout[0]['index'])

real = torch.from_numpy(spec[0, 0, :, :])
imag = torch.from_numpy(spec[0, 1, :, :])

# PyTorch iSTFT
complex_spec = torch.complex(real, imag)
win = torch.hann_window(1024)
wav = torch.istft(complex_spec, n_fft=1024, hop_length=256, win_length=1024, window=win, center=True).numpy()

ref_samples = ref_frames * 256
gen_wav = wav[ref_samples:]
max_val = np.max(np.abs(gen_wav))
if max_val > 1e-4:
    gen_wav = gen_wav * (0.95 / max_val)

sf.write('/mnt/c/voice_cloning/scratch/test_py_device_match.wav', gen_wav, 24000)
print('Wrote /mnt/c/voice_cloning/scratch/test_py_device_match.wav!')

# Now compare with mobile_generated_voice.wav
mob_wav, _ = sf.read('/mnt/c/voice_cloning/scratch/mobile_generated_voice.wav')
print(f'Py wav shape: {gen_wav.shape}, Mob wav shape: {mob_wav.shape}')

min_len = min(len(gen_wav), len(mob_wav))
diff = np.abs(gen_wav[:min_len] - mob_wav[:min_len])
print(f'Max diff: {np.max(diff):.4f}, Mean diff: {np.mean(diff):.4f}')
corr = np.corrcoef(gen_wav[:min_len], mob_wav[:min_len])[0, 1]
print(f'Correlation between Python & Mobile: {corr:.4f}')
