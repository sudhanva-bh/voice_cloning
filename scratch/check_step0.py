import numpy as np
from ai_edge_litert.interpreter import Interpreter

interp = Interpreter(model_path='/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_dit_int8.tflite', num_threads=4)
interp.allocate_tensors()

# Load real inputs from compare_device_py
sys_path = '/mnt/c/voice_cloning'
import sys; sys.path.insert(0, sys_path)
from scripts.infer_litert import load_vocab, extract_mel_spectrogram

vocab = load_vocab('/mnt/c/voice_cloning/android/app/src/main/assets/vocab.txt')
ref_mel, _ = extract_mel_spectrogram('/mnt/c/voice_cloning/android/app/src/main/assets/samples/ref_en.wav')
ref_mel_np = ref_mel.numpy().T
ref_frames = ref_mel_np.shape[0]

full_text = 'Some call me nature. Google LiteRT is fast and clear.'
tokens = [vocab.get(c, -1) for c in full_text]
tokens = tokens[:128] + [-1] * max(0, 128 - len(tokens))
text_tokens = np.array([tokens], dtype=np.int32)

cond_mel = np.zeros((1, 512, 100), dtype=np.float32)
cond_mel[0, :ref_frames, :] = ref_mel_np

np.random.seed(42)
mel_out = np.random.randn(1, 512, 100).astype(np.float32)

interp.set_tensor(0, mel_out)
interp.set_tensor(1, cond_mel)
interp.set_tensor(2, text_tokens)
interp.set_tensor(3, np.array([0.0], dtype=np.float32))

interp.invoke()

out = interp.get_tensor(2622)
print('out shape:', out.shape, 'norm:', np.linalg.norm(out), 'min:', out.min(), 'max:', out.max())
print('out[0, 0, :5]:', out[0, 0, :5])
