import os
import urllib.request
import time

papers = [
    {
        'id': '2410.06885',
        'title': 'F5_TTS_Fairytaler_Flow_Matching',
        'url': 'https://arxiv.org/pdf/2410.06885.pdf'
    },
    {
        'id': '2306.00814',
        'title': 'Vocos_Neural_Vocoder',
        'url': 'https://arxiv.org/pdf/2306.00814.pdf'
    },
    {
        'id': '2210.02747',
        'title': 'Flow_Matching_Generative_Modeling',
        'url': 'https://arxiv.org/pdf/2210.02747.pdf'
    },
    {
        'id': '2306.15687',
        'title': 'Voicebox_Universal_Speech_Generation',
        'url': 'https://arxiv.org/pdf/2306.15687.pdf'
    },
    {
        'id': '2309.03199',
        'title': 'Matcha_TTS_Fast_Conditional_Flow_Matching',
        'url': 'https://arxiv.org/pdf/2309.03199.pdf'
    },
    {
        'id': '2404.14700',
        'title': 'FlashSpeech_Efficient_ZeroShot_Speech_Synthesis',
        'url': 'https://arxiv.org/pdf/2404.14700.pdf'
    },
    {
        'id': '2209.03003',
        'title': 'Flow_Straight_and_Fast_Rectified_Flow',
        'url': 'https://arxiv.org/pdf/2409.03003.pdf'  # or fallback
    },
    {
        'id': '2406.18009',
        'title': 'E2_TTS_NonAutoregressive_ZeroShot',
        'url': 'https://arxiv.org/pdf/2406.18009.pdf'
    },
    {
        'id': '2403.07639',
        'title': 'IndicVoices_Multilingual_Indian_Speech',
        'url': 'https://arxiv.org/pdf/2403.07639.pdf'
    }
]

out_dir = os.path.join(os.path.dirname(__file__), '..', 'research_papers')
os.makedirs(out_dir, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for p in papers:
    filename = os.path.join(out_dir, f"{p['title']}.pdf")
    if os.path.exists(filename) and os.path.getsize(filename) > 10000:
        print(f"Already exists: {filename}")
        continue
    print(f"Downloading {p['title']} ({p['id']})...")
    try:
        req = urllib.request.Request(p['url'], headers=headers)
        with urllib.request.urlopen(req, timeout=40) as resp, open(filename, 'wb') as f:
            f.write(resp.read())
        print(f"Downloaded {filename} ({os.path.getsize(filename)} bytes)")
        time.sleep(1.5)
    except Exception as e:
        print(f"Failed to download {p['title']}: {e}")

print("All paper downloads completed.")
