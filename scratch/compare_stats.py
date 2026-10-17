import soundfile as sf
import numpy as np

def stats(path):
    data, sr = sf.read(path)
    fft = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), 1/sr)
    sc = np.sum(freqs * fft) / np.sum(fft)
    p_high = np.sum(fft[freqs > 4000]**2) / np.sum(fft**2)
    name = path.split("/")[-1]
    print(f'{name:27s}: dur={len(data)/sr:.2f}s, min={np.min(data):.3f}, max={np.max(data):.3f}, rms={np.sqrt(np.mean(data**2)):.4f}, sc={sc:.1f}Hz, power>4kHz={p_high*100:.1f}%')

for f in ['official_sample_test.wav', 'pytorch_baseline.wav', 'litert_fp32.wav', 'litert_int8.wav', 'test_new_inlined.wav']:
    stats('/mnt/c/voice_cloning/scratch/parity_test/' + f)
stats('/mnt/c/voice_cloning/scratch/mobile_generated_voice.wav')
