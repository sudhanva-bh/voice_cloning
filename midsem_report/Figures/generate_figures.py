#!/usr/bin/env python3
"""
Script to generate all publication-quality figures for the CS F377 report.
Generates:
1. lenovo_rtf.pdf - Mean RTF by utterance tier on Lenovo Tab K10
2. lenovo_vmrss.pdf - Post-utterance VmRSS across all 9 trials on Lenovo Tab K10
3. system_architecture.pdf - Overall System Architecture (Mermaid equivalent)
4. indicf5_pipeline.pdf - IndicF5 Zero-Shot Inference Pipeline (Mermaid equivalent)
5. runtime_architecture.pdf - Native Runtime & Deployment Architecture (Mermaid equivalent)
6. optimization_roadmap.pdf - Future Edge Optimization Roadmap (Mermaid equivalent)
Also saves the .mmd source files for all architecture diagrams.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

OUT_DIR = r"c:\voice_cloning\midsem_report\Figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Set global academic typography
plt.rcParams.update({
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Helvetica'],
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 13,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

# -------------------------------------------------------------
# 1. CHART 1: Lenovo Tab K10 Mean RTF by Utterance Tier
# -------------------------------------------------------------
def generate_lenovo_rtf():
    tiers = ['Short (~5w)', 'Medium (~25w)', 'Long (~65w)']
    mean_rtf = [18.222, 10.783, 11.197]
    min_rtf = [16.820, 10.194, 8.968]
    max_rtf = [19.986, 11.688, 15.049]
    
    # Calculate asymmetric error bars: [mean - min, max - mean]
    yerr = [
        [mean_rtf[i] - min_rtf[i] for i in range(3)],
        [max_rtf[i] - mean_rtf[i] for i in range(3)]
    ]
    
    fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=300)
    bars = ax.bar(tiers, mean_rtf, yerr=yerr, capsize=6, color=['#2b5c8f', '#4682b4', '#5c9bd5'],
                  edgecolor='#1a365d', linewidth=1.2, width=0.52, zorder=3,
                  error_kw={'ecolor': '#1a365d', 'linewidth': 1.5, 'capthick': 1.5})
    
    # Value labels on top of bars
    for i, bar in enumerate(bars):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + yerr[1][i] + 0.6,
                f"Mean: {mean_rtf[i]:.2f}x\n[{min_rtf[i]:.2f}x–{max_rtf[i]:.2f}x]",
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1a202c')
        
    ax.set_ylabel('Real-Time Factor (RTF = Latency / Audio Duration)', fontweight='bold')
    ax.set_xlabel('Utterance Length Tier (N=3 Trials per Tier)', fontweight='bold')
    ax.set_title('ZipVoice PoC Throughput on Lenovo Tab K10\n(MediaTek Helio P22T, 4 GB RAM, CPU-Only)', fontsize=11, pad=12)
    ax.set_ylim(0, 24)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "lenovo_rtf.pdf"))
    plt.close(fig)
    print("Generated lenovo_rtf.pdf")

# -------------------------------------------------------------
# 2. CHART 2: Lenovo Tab K10 Post-Utterance VmRSS Across 9 Trials
# -------------------------------------------------------------
def generate_lenovo_vmrss():
    trials = [f'S{i}' for i in range(1, 4)] + [f'M{i}' for i in range(1, 4)] + [f'L{i}' for i in range(1, 4)]
    vmrss_values = [1301, 1298, 1276, 2337, 1532, 1901, 2326, 2491, 2367]
    categories = ['Short']*3 + ['Medium']*3 + ['Long']*3
    colors = ['#3182ce']*3 + ['#dd6b20']*3 + ['#319795']*3
    
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=300)
    x = range(len(trials))
    bars = ax.bar(x, vmrss_values, color=colors, edgecolor='#2d3748', linewidth=1.1, width=0.6, zorder=3)
    
    # Value annotations
    for i, v in enumerate(vmrss_values):
        ax.text(i, v + 40, f"{v}", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2d3748')
        
    # Group indicators & Means
    ax.axvspan(-0.4, 2.4, color='#ebf8ff', alpha=0.6, zorder=1)
    ax.axvspan(2.6, 5.4, color='#fffaf0', alpha=0.6, zorder=1)
    ax.axvspan(5.6, 8.4, color='#e6fffa', alpha=0.6, zorder=1)
    
    # Category mean lines
    ax.hlines(1291.7, -0.3, 2.3, colors='#2b6cb0', linestyles='--', linewidth=1.8, zorder=4, label='Tier Arithmetic Mean')
    ax.hlines(1923.3, 2.7, 5.3, colors='#c05621', linestyles='--', linewidth=1.8, zorder=4)
    ax.hlines(2394.7, 5.7, 8.3, colors='#285e61', linestyles='--', linewidth=1.8, zorder=4)
    
    ax.text(1.0, 1370, 'Short Mean: 1291.7 MB', ha='center', fontsize=8.5, color='#2b6cb0', fontweight='bold')
    ax.text(4.0, 2000, 'Med Mean: 1923.3 MB', ha='center', fontsize=8.5, color='#c05621', fontweight='bold')
    ax.text(7.0, 2460, 'Long Mean: 2394.7 MB', ha='center', fontsize=8.5, color='#285e61', fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f"Short {i}\n(S{i})" for i in range(1, 4)] + 
                       [f"Med {i}\n(M{i})" for i in range(1, 4)] + 
                       [f"Long {i}\n(L{i})" for i in range(1, 4)], fontsize=9)
    ax.set_ylabel('Post-Utterance VmRSS (MB) via /proc/self/status', fontweight='bold')
    ax.set_xlabel('Individual Synthesis Trials (N=9, 0 LMK Terminations)', fontweight='bold')
    ax.set_title('Post-Utterance Resident Memory (VmRSS) on Lenovo Tab K10\n(Demonstrating Observed Allocation Variability Across Trials)', fontsize=11, pad=12)
    ax.set_ylim(0, 2800)
    ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "lenovo_vmrss.pdf"))
    plt.close(fig)
    print("Generated lenovo_vmrss.pdf")

# -------------------------------------------------------------
# 3. DIAGRAM 1: Overall System Architecture (Phase Progression)
# -------------------------------------------------------------
def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    
    def draw_box(x, y, w, h, text, title=None, bg="#edf2f7", border="#4a5568", is_sub=False):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
                             fc=bg, ec=border, lw=1.5, zorder=2)
        ax.add_patch(box)
        if title:
            ax.text(x + w/2, y + h - 2.5, title, ha='center', va='top', fontsize=9.5, fontweight='bold', color='#1a202c', zorder=3)
            ax.text(x + w/2, y + h/2 - 1.2, text, ha='center', va='center', fontsize=8.5, color='#2d3748', zorder=3)
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9, color='#1a202c', fontweight='bold' if is_sub else 'normal', zorder=3)

    def draw_arrow(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#2b6cb0", lw=1.8), zorder=4)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.2, label, ha='center', va='bottom', fontsize=8, color="#2b6cb0", fontweight='bold', zorder=5)

    # Outer containers
    # Phase 1
    p1 = FancyBboxPatch((2, 33), 96, 24, boxstyle="round,pad=0.8,rounding_size=1.5",
                        fc="#f7fafc", ec="#2b6cb0", lw=2, linestyle="--", zorder=1)
    ax.add_patch(p1)
    ax.text(5, 55, "PHASE 1: Mobile Proof of Concept (Implemented & Benchmarked)", fontsize=11, fontweight='bold', color="#2b6cb0")

    draw_box(4, 36, 14, 14, "3–5s WAV/M4A\nClassroom Mic", "Teacher Audio", bg="#ebf8ff", border="#3182ce")
    draw_arrow(18.5, 43, 22.5, 43)
    draw_box(22.5, 36, 15, 14, "16-bit PCM Mono\n24 kHz, RMS Norm", "Preprocessing", bg="#ebf8ff", border="#3182ce")
    draw_arrow(38, 43, 42, 43)
    draw_box(42, 36, 17, 14, "ZipVoice-Distill\n123M Zipformer\nINT8 (5.5M+124M)", "Acoustic Model", bg="#e6fffa", border="#319795")
    draw_arrow(59.5, 43, 63.5, 43)
    draw_box(63.5, 36, 15, 14, "Sherpa-ONNX\nin Flutter Isolate\n(CPU-Only)", "Mobile Runtime", bg="#feebc8", border="#dd6b20")
    draw_arrow(79, 43, 83, 43)
    draw_box(83, 36, 13, 14, "Lenovo Tab K10\n4 GB RAM\nNo LMK Crashing", "Measured Target", bg="#fed7d7", border="#e53e3e")

    # Phase 2
    p2 = FancyBboxPatch((2, 4), 96, 25, boxstyle="round,pad=0.8,rounding_size=1.5",
                        fc="#f7fafc", ec="#805ad5", lw=2, linestyle="-", zorder=1)
    ax.add_patch(p2)
    ax.text(5, 26.5, "PHASE 2 & 3: IndicF5 Engineering & Native Runtime Pipeline (Developed Architecture)", fontsize=11, fontweight='bold', color="#805ad5")

    draw_box(4, 7, 14, 15, "Tamil, Telugu,\nHindi Text +\n3.8s Teacher Audio", "Multilingual Input", bg="#faf5ff", border="#805ad5")
    draw_arrow(18.5, 14.5, 22.5, 14.5)
    draw_box(22.5, 7, 15, 15, "ConvNeXt-V2\n100-ch Mel Spect.\nChannel Concat", "Fused Conditioning", bg="#faf5ff", border="#805ad5")
    draw_arrow(38, 14.5, 42, 14.5)
    draw_box(42, 7, 17, 15, "IndicF5 DiT (335M)\nStatic INT8 (349 MB)\n8-Step Euler + Sway", "Diffusion Engine", bg="#e6fffa", border="#319795")
    draw_arrow(59.5, 14.5, 63.5, 14.5)
    draw_box(63.5, 7, 16, 15, "Vocos Vocoder\nINT8 (22 MB)\nAnalytical iSTFT", "Neural Vocoder", bg="#ebf8ff", border="#3182ce")
    draw_arrow(80, 14.5, 84, 14.5)
    draw_box(84, 7, 12, 15, "Dart FFI Bridge\nNative C++ Engine\nArena Memory", "Edge Deployment", bg="#feebc8", border="#dd6b20")

    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "system_architecture.pdf"))
    plt.close(fig)
    print("Generated system_architecture.pdf")

    # Save Mermaid source
    mmd_content = """graph TD
    subgraph Phase1["PHASE 1: Mobile Proof of Concept (Implemented & Measured)"]
        A1["Teacher Reference Audio<br/>(3-5s Classroom Mic)"] --> B1["Audio Preprocessing<br/>(24 kHz PCM, RMS Normalization)"]
        B1 --> C1["ZipVoice-Distill<br/>(123M INT8 Zipformer)"]
        C1 --> D1["Sherpa-ONNX Runtime<br/>(Flutter Android Isolate)"]
        D1 --> E1["Lenovo Tab K10 Execution<br/>(CPU-Only, 4 GB RAM, 0 LMK Kills)"]
    end

    subgraph Phase2["PHASE 2 & 3: IndicF5 Engineering & Native Runtime Pipeline (Developed)"]
        A2["Teacher Audio + Transcript<br/>+ Indic Target Text"] --> B2["Fused Conditioning<br/>(ConvNeXt-V2 Text + Mel Prefix)"]
        B2 --> C2["IndicF5 Diffusion Transformer<br/>(22 Layers, INT8 349 MB, 8-Step Euler)"]
        C2 --> D2["Vocos Neural Vocoder<br/>(INT8 22 MB, Analytical iSTFT)"]
        D2 --> E2["Native C++ & Dart FFI Engine<br/>(Pre-allocated Static Arenas, Flutter App)"]
    end
"""
    with open(os.path.join(OUT_DIR, "system_architecture.mmd"), "w", encoding="utf-8") as f:
        f.write(mmd_content)

# -------------------------------------------------------------
# 4. DIAGRAM 2: IndicF5 Zero-Shot Inference Pipeline
# -------------------------------------------------------------
def generate_indicf5_pipeline():
    fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 55)

    def draw_node(x, y, w, h, title, sub, bg="#edf2f7", border="#4a5568"):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.0",
                           fc=bg, ec=border, lw=1.4, zorder=2)
        ax.add_patch(b)
        ax.text(x + w/2, y + h - 2.2, title, ha='center', va='top', fontsize=8.8, fontweight='bold', color='#1a202c', zorder=3)
        ax.text(x + w/2, y + h/2 - 1.2, sub, ha='center', va='center', fontsize=7.8, color='#4a5568', zorder=3)

    def draw_arr(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#2b6cb0", lw=1.6), zorder=4)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.0, label, ha='center', va='bottom', fontsize=7.5, color="#2b6cb0", fontweight='bold', zorder=5)

    # Inputs
    draw_node(2, 38, 14, 13, "Reference Audio", "3.5–5.0s WAV (24 kHz)", "#ebf8ff", "#3182ce")
    draw_node(2, 21, 14, 13, "Ref Transcript", "Matching text string", "#ebf8ff", "#3182ce")
    draw_node(2, 4, 14, 13, "Target Indic Text", "Tamil / Telugu / Hindi", "#faf5ff", "#805ad5")

    # Conditioning
    draw_node(20, 38, 16, 13, "Mel-Spectrogram", "100-channel Filterbank\nHop 256, N_fft 1024", "#ebf8ff", "#3182ce")
    draw_node(20, 12, 16, 14, "Text Tokenization", "vocab.txt (187 tokens)\nConvNeXt-V2 Encoder", "#faf5ff", "#805ad5")

    draw_arr(16.5, 44.5, 19.5, 44.5)
    draw_arr(16.5, 27.5, 19.5, 20.0)
    draw_arr(16.5, 10.5, 19.5, 16.5)

    # Fused conditioning
    draw_node(40, 20, 16, 20, "Fused Conditioning", "Concatenation along\nChannel Dimension\n[x, cond, text_embed]\nNO Cross-Attention", "#fffaf0", "#dd6b20")
    draw_arr(36.5, 44.5, 39.5, 33.0)
    draw_arr(36.5, 19.0, 39.5, 27.0)

    # Diffusion Loop Box
    loop_box = FancyBboxPatch((59, 12), 22, 38, boxstyle="round,pad=0.6,rounding_size=1.2",
                              fc="#f0fff4", ec="#38a169", lw=1.8, linestyle="--", zorder=1)
    ax.add_patch(loop_box)
    ax.text(70, 48, "8-Step Euler ODE Loop", ha='center', fontsize=9.5, fontweight='bold', color="#22543d", zorder=3)
    ax.text(70, 45, "Sway Schedule: c = -1.0\nCFG Scale: gamma = 2.0", ha='center', fontsize=7.8, color="#276749", zorder=3)

    draw_node(61, 28, 18, 14, "22-Layer DiT", "Bidirectional Self-Attn\nRoPE Embeddings\nVelocity Estimation", "#ffffff", "#38a169")
    draw_node(61, 15, 18, 10, "Gaussian Noise", "Initial y0 ~ N(0, I)", "#edf2f7", "#718096")

    draw_arr(56.5, 30, 60.5, 35, "Cond")
    draw_arr(70, 25.5, 70, 27.5) # loop arrow
    ax.annotate('', xy=(79.5, 38), xytext=(79.5, 32),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.7", color="#2f855a", lw=1.5), zorder=4)
    ax.text(82, 35, "t -> t+dt", fontsize=7.5, color="#2f855a", fontweight='bold')

    # Output Vocoder
    draw_node(85, 29, 13, 14, "Vocos Vocoder", "Analytical iSTFT\nINT8 (22 MB)\n13.5M Params", "#ebf8ff", "#3182ce")
    draw_node(85, 10, 13, 14, "Waveform Output", "24 kHz Audio\nTeacher Voice\nCloned Speech", "#e6fffa", "#319795")

    draw_arr(81.5, 36, 84.5, 36, "Target Mel")
    draw_arr(91.5, 28.5, 91.5, 24.5)

    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "indicf5_pipeline.pdf"))
    plt.close(fig)
    print("Generated indicf5_pipeline.pdf")

    # Save Mermaid source
    mmd_content = """graph TD
    A["Reference Audio (3.5–5.0s, 24 kHz)"] --> D["100-Channel Mel Extraction"]
    B["Reference Transcript"] --> E["Multilingual Tokenization (vocab.txt)"]
    C["Target Indic Text"] --> E
    E --> F["ConvNeXt-V2 Text Representation"]
    D --> G["Fused Sequence Conditioning<br/>(Channel Concatenation, No Cross-Attention)"]
    F --> G
    
    H["Gaussian Noise y0 ~ N(0, I)"] --> I
    G --> I

    subgraph ODE["8-Step Numerical ODE Integration Loop"]
        I["DiT Backbone (22 Layers, Bidirectional Self-Attention + RoPE)"]
        I --> J["Classifier-Free Guidance (gamma = 2.0)"]
        J --> K["Euler Step Update (Sway Schedule c = -1.0)"]
        K -.->|Repeat 8 Steps| I
    end

    K --> L["Target Mel Slicing"]
    L --> M["Vocos Neural Vocoder (INT8 22 MB, Analytical iSTFT)"]
    M --> N["Synthesized Waveform (Teacher Voice Cloned Speech)"]
"""
    with open(os.path.join(OUT_DIR, "indicf5_pipeline.mmd"), "w", encoding="utf-8") as f:
        f.write(mmd_content)

# -------------------------------------------------------------
# 5. DIAGRAM 3: Native Runtime and Deployment Architecture
# -------------------------------------------------------------
def generate_runtime_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 55)

    def draw_panel(x, y, w, h, title, subtitle, bg, border):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
                           fc=bg, ec=border, lw=1.6, zorder=1)
        ax.add_patch(p)
        ax.text(x + 2, y + h - 2.5, title, fontsize=9.5, fontweight='bold', color=border, zorder=2)
        ax.text(x + 2, y + h - 5.0, subtitle, fontsize=7.8, color='#4a5568', zorder=2)

    def draw_box(x, y, w, h, text, title=None, bg="#ffffff", border="#4a5568"):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=0.8",
                           fc=bg, ec=border, lw=1.2, zorder=3)
        ax.add_patch(b)
        if title:
            ax.text(x + w/2, y + h - 1.8, title, ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1a202c', zorder=4)
            ax.text(x + w/2, y + h/2 - 1.0, text, ha='center', va='center', fontsize=7.5, color='#4a5568', zorder=4)
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, color='#1a202c', zorder=4)

    def draw_conn(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->,head_width=0.3,head_length=0.4", color="#4a5568", lw=1.4), zorder=5)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.0, label, ha='center', va='bottom', fontsize=7.5, color="#2b6cb0", fontweight='bold', zorder=6)

    # Panel 1: Flutter UI & Dart Layer
    draw_panel(2, 4, 28, 48, "Flutter Mobile UI Layer", "UI Responsiveness & Accessibility", "#ebf8ff", "#2b6cb0")
    draw_box(4, 38, 24, 7, "Lesson Prep & Voice Selection\nTalkBack Accessibility", "Teacher Interface", "#ffffff", "#3182ce")
    draw_box(4, 28, 24, 7, "Mic Capture (3–5s) / Playback\nFFmpeg Transcoding", "Audio Subsystem", "#ffffff", "#3182ce")
    draw_box(4, 18, 24, 7, "Isolate.run() Decoupling\nPrevents ANR & Jitter", "Background Dart Isolate", "#feebc8", "#dd6b20")
    draw_box(4, 8, 24, 7, "indicf5_service.dart\nDirect Pointer Passing", "Dart FFI Bridge", "#faf5ff", "#805ad5")

    # Panel 2: Native C++ Runtime Engine
    draw_panel(34, 4, 32, 48, "Native C++ Runtime Engine", "libindicf5_engine.so (NDK / C ABI)", "#faf5ff", "#6b46c1")
    draw_box(36, 38, 28, 7, "C ABI: indicf5_synthesize()\nThread Pools & Lifecycles", "C Engine Lifecycle", "#ffffff", "#805ad5")
    draw_box(36, 28, 28, 7, "Pre-allocated Memory Arenas\nEliminates Heap Fragmentation", "Static Tensor Buffers", "#e6fffa", "#319795")
    draw_box(36, 18, 28, 7, "8-Step Euler ODE Solver\nARM NEON SIMD CFG Kernels", "Numerical ODE Solver", "#ffffff", "#805ad5")
    draw_box(36, 8, 28, 7, "Vocos iSTFT Reconstruction\nDirect PCM Buffer Fill", "Analytical Vocoding", "#ffffff", "#805ad5")

    # Panel 3: Execution Paths & Hardware Tiers
    draw_panel(70, 4, 28, 48, "Hardware Tiers & Baselines", "Target Silicon & Empirical Reference", "#fffaf0", "#c05621")
    draw_box(72, 37, 24, 11, "Lenovo Tab K10 Target\nHelio P22T (ARM Cortex-A53)\nPure CPU-Only (No NPU)\nIndicF5 Native Target", "Target Edge Device", "#e6fffa", "#319795")
    draw_box(72, 21, 24, 13, "Sherpa-ONNX on Tab K10\nMean RTF: 10.8x–18.2x\nVmRSS: 1,276–2,491 MB\n0 / 9 LMK Terminations", "Measured ZipVoice PoC", "#edf2f7", "#4a5568")
    draw_box(72, 6, 24, 12, "Qualcomm QNN HTP\nMediaTek Dimensity APU\nGoogle LiteRT Delegation\n(Compatible Hardware Only)", "Future Silicon (Proposed)", "#feebc8", "#dd6b20")

    # Connections
    draw_conn(28.5, 11.5, 35.5, 41.5, "FFI Calls")
    draw_conn(64.5, 27.0, 71.5, 42.0, "C++ Target")
    draw_conn(64.5, 13.0, 71.5, 12.0, "LiteRT (Future)")

    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "runtime_architecture.pdf"))
    plt.close(fig)
    print("Generated runtime_architecture.pdf")

    # Save Mermaid source
    mmd_content = """graph LR
    subgraph UI["Flutter Mobile Application Layer"]
        A["Teacher UI & Accessibility Controls"]
        B["Audio Capture & Playback Subsystem"]
        C["Background Dart Isolate (Isolate.run)"]
        D["Dart FFI Service Bridge"]
        A --> C
        B --> C
        C --> D
    end

    subgraph Native["Native IndicF5 C++ Engine (libindicf5_engine.so)"]
        E["C ABI Entry Points"]
        F["Pre-allocated Static Memory Arenas (280 MB)"]
        G["8-Step Euler ODE Solver with NEON SIMD"]
        H["Vocos Analytical iSTFT Vocoder"]
        D -->|Pointers| E
        E --> F
        F --> G
        G --> H
    end

    subgraph Hardware["Hardware Tiers & Empirical Reference"]
        I["Lenovo Tab K10 Target<br/>(MediaTek Helio P22T, CPU-Only, No NPU)<br/>[IndicF5 Native Target]"]
        J["Measured ZipVoice PoC Baseline<br/>(Sherpa-ONNX, Mean RTF 10.8x-18.2x, 0 LMK Kills)<br/>[Empirical Reference]"]
        K["Future Compatible Silicon<br/>(Google LiteRT, Qualcomm QNN / MediaTek APU)<br/>[Proposed Roadmap]"]
        G -->|C++ Deployment Target| I
        G -.->|Future LiteRT Delegation| K
    end
"""
    with open(os.path.join(OUT_DIR, "runtime_architecture.mmd"), "w", encoding="utf-8") as f:
        f.write(mmd_content)

# -------------------------------------------------------------
# 6. DIAGRAM 4: Future Optimization Roadmap
# -------------------------------------------------------------
def generate_optimization_roadmap():
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)

    def draw_card(x, y, w, h, title, status, points, bg, border):
        c = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.0",
                           fc=bg, ec=border, lw=1.5, zorder=2)
        ax.add_patch(c)
        ax.text(x + 2, y + h - 2.5, title, fontsize=9.5, fontweight='bold', color=border, zorder=3)
        ax.text(x + w - 2, y + h - 2.5, status, fontsize=7.5, fontweight='bold', color='#718096', ha='right', zorder=3)
        for i, pt in enumerate(points):
            ax.text(x + 2, y + h - 6.0 - i*3.0, f"• {pt}", fontsize=8, color='#2d3748', zorder=3)

    def draw_arr(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", color="#4a5568", lw=1.6), zorder=4)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.2, label, ha='center', va='bottom', fontsize=7.5, color="#2b6cb0", fontweight='bold', zorder=5)

    # Stages
    draw_card(2, 6, 21, 38, "Baseline CPU Path", "MEASURED",
              ["Lenovo Tab K10 Target", "8-Step Euler ODE solver", "CPU NEON float32/int8", "RTF: 8.9x–19.9x (K10)", "Post-VmRSS: up to 2491 MB", "Operational, non-real-time"],
              "#fed7d7", "#e53e3e")

    draw_arr(23.5, 25, 27.5, 25, "Distillation")

    draw_card(28, 6, 21, 38, "Step Reduction", "PROPOSED",
              ["FlashSpeech / Consistency", "2-Step Flow Distillation", "Eliminates 6 forward passes", "Target: ~75% latency drop", "Preserves voice timbre", "CPU speedup on K10"],
              "#feebc8", "#dd6b20")

    draw_arr(49.5, 25, 53.5, 25, "LiteRT")

    draw_card(54, 6, 21, 38, "Runtime Engine", "PLANNED",
              ["Google LiteRT Migration", "Kernel Operator Fusion", "Zero-Copy Buffer Sharing", "Working Memory Capping", "Target: Peak RSS < 850 MB", "Reduces allocator jitter"],
              "#e6fffa", "#319795")

    draw_arr(75.5, 25, 79.5, 25, "Hardware")

    draw_card(80, 6, 18, 38, "NPU Acceleration", "TARGET",
              ["Compatible Silicon Only", "Qualcomm Hexagon HTP", "MediaTek NeuroPilot", "Not available on K10", "Sub-1.0x Real-Time Factor", "Future device deployments"],
              "#faf5ff", "#805ad5")

    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "optimization_roadmap.pdf"))
    plt.close(fig)
    print("Generated optimization_roadmap.pdf")

    # Save Mermaid source
    mmd_content = """graph LR
    A["Baseline CPU Inference<br/>(Lenovo Tab K10, 8 Euler Steps)<br/>[Measured: RTF ~10x-18x]"]
    -->|Flow Distillation| B["Sampling Step Distillation<br/>(2-Step FlashSpeech Consistency)<br/>[Target: ~75% Compute Drop]"]
    -->|Runtime Engine| C["Google LiteRT & Operator Fusion<br/>(Zero-Copy Arenas, Memory Capping)<br/>[Target: Strict RAM Confinement]"]
    -->|Compatible Hardware| D["NPU Hardware Acceleration<br/>(Qualcomm QNN HTP / MediaTek APU)<br/>[Target: Sub-1.0x Real-Time Factor]"]
"""
    with open(os.path.join(OUT_DIR, "optimization_roadmap.mmd"), "w", encoding="utf-8") as f:
        f.write(mmd_content)

if __name__ == '__main__':
    generate_lenovo_rtf()
    generate_lenovo_vmrss()
    generate_system_architecture()
    generate_indicf5_pipeline()
    generate_runtime_architecture()
    generate_optimization_roadmap()
    print("All figures and .mmd sources successfully created.")
