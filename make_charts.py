"""
Generate comparison charts for Qwen3.6-35B-A3B MLX DWQ vs Q8_K_XL GGUF.

Produces a single PNG with four panels (2x2 layout):
  1. Agent multi-turn bench (prefill-cached, short turns) — n=3 each, avg wall time
  2. Pure decode throughput — tok/s, n=3 each (short prompt → long output)
  3. Real research workflow (Hermes + Kenya Hara MUJI task) — wall time + tool calls
  4. Compression A/B (long prompt 68K + medium output 1.2K) — n=3 each

Output: results_comparison.png
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = ['Helvetica', 'Arial', 'sans-serif']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

Q8_COLOR = '#D97757'   # warm amber
DWQ_COLOR = '#4A90A4'  # calm teal

fig, axes = plt.subplots(2, 2, figsize=(14, 11))
axes = axes.flatten()
fig.suptitle('Qwen3.6-35B-A3B on M4 Max 128GB — DWQ MLX vs Q8_K_XL GGUF (n=3, temp=0.0)',
             fontsize=14, fontweight='bold', y=0.995)

# --- Panel 1: Agent multi-turn bench (avg wall time per 70 rounds) ---
ax = axes[0]
q8_times = [126.2, 134.2, 108.5]
dwq_times = [133.4, 125.7]  # warm runs only (run 1 was cold outlier 77s)
labels = ['Q8 GGUF', 'DWQ 4bit']
means = [np.mean(q8_times), np.mean(dwq_times)]
stds = [np.std(q8_times), np.std(dwq_times)]
xpos = [0, 1]
bars = ax.bar(xpos, means, yerr=stds, capsize=8, color=[Q8_COLOR, DWQ_COLOR],
              edgecolor='black', linewidth=0.8, width=0.55)
for b, m in zip(bars, means):
    ax.text(b.get_x() + b.get_width()/2, m + 3, f'{m:.1f}s', ha='center', fontsize=11, fontweight='bold')
ax.set_xticks(xpos)
ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel('Wall time per 70 rounds (s, lower = better)', fontsize=10)
ax.set_title('(1) Agent multi-turn bench\nprefill-heavy (stability 210/210 both)',
             fontsize=11, fontweight='bold')
ax.set_ylim(0, 160)
# annotate winner
delta1 = (means[1] - means[0]) / means[0] * 100
ax.text(0.5, 150, f'Q8 faster by {abs(delta1):.1f}%', ha='center',
        fontsize=10, style='italic', color='gray')

# --- Panel 2: Pure decode tok/s ---
ax = axes[1]
q8_decode = [59.27, 59.95, 59.74]
dwq_decode = [86.07, 88.49, 88.11]
means = [np.mean(q8_decode), np.mean(dwq_decode)]
stds = [np.std(q8_decode), np.std(dwq_decode)]
bars = ax.bar(xpos, means, yerr=stds, capsize=8, color=[Q8_COLOR, DWQ_COLOR],
              edgecolor='black', linewidth=0.8, width=0.55)
for b, m in zip(bars, means):
    ax.text(b.get_x() + b.get_width()/2, m + 2, f'{m:.1f}', ha='center', fontsize=11, fontweight='bold')
ax.set_xticks(xpos)
ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel('Decode throughput (tok/s, higher = better)', fontsize=10)
ax.set_title('(2) Pure decode throughput\n84t prompt → 1500t output',
             fontsize=11, fontweight='bold')
ax.set_ylim(0, 110)
delta2 = (means[1] - means[0]) / means[0] * 100
ax.text(0.5, 100, f'DWQ faster by +{delta2:.1f}%', ha='center',
        fontsize=10, style='italic', color='gray')

# --- Panel 3: Real research workflow ---
ax = axes[2]
q8_wall = 471  # 7m 51s
dwq_wall = 399  # 6m 39s
q8_tools = 14
dwq_tools = 9

# primary: wall time bars
x = np.arange(2)
wall = [q8_wall, dwq_wall]
bars = ax.bar(x, wall, color=[Q8_COLOR, DWQ_COLOR], edgecolor='black',
              linewidth=0.8, width=0.55)
for b, m in zip(bars, wall):
    mins, secs = divmod(int(m), 60)
    ax.text(b.get_x() + b.get_width()/2, m + 10, f'{mins}m {secs}s',
            ha='center', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel('Wall time (s, lower = better)', fontsize=10)
ax.set_title('(3) Real research workflow\nHermes + Kenya Hara MUJI task (n=1)',
             fontsize=11, fontweight='bold')
ax.set_ylim(0, 570)

# secondary: tool-call count as overlaid text
delta3 = (dwq_wall - q8_wall) / q8_wall * 100
ax.text(0.5, 540, f'DWQ faster by +{abs(delta3):.1f}%', ha='center',
        fontsize=10, style='italic', color='gray')
for i, tc in enumerate([q8_tools, dwq_tools]):
    ax.text(i, 30, f'{tc} tool calls', ha='center', fontsize=10,
            color='white', fontweight='bold')

# --- Panel 4: Compression A/B (long prompt + medium output) ---
ax = axes[3]
q8_comp_times = [180.4, 37.0, 36.5]
dwq_comp_times = [100.0, 21.0, 21.0]
means = [np.mean(q8_comp_times), np.mean(dwq_comp_times)]
bars = ax.bar(xpos, means, color=[Q8_COLOR, DWQ_COLOR],
              edgecolor='black', linewidth=0.8, width=0.55)
for b, m in zip(bars, means):
    ax.text(b.get_x() + b.get_width()/2, m + 3, f'{m:.1f}s', ha='center', fontsize=11, fontweight='bold')
# overlay dots for individual runs
for i, runs in enumerate([q8_comp_times, dwq_comp_times]):
    ax.scatter([i] * len(runs), runs, color='black', s=25, zorder=3, alpha=0.6)
ax.set_xticks(xpos)
ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel('Wall time per compression (s, lower = better)', fontsize=10)
ax.set_title('(4) Compression A/B workload\n68K prompt + 1.2K output, includes cold+warm',
             fontsize=11, fontweight='bold')
ax.set_ylim(0, 220)
delta4 = (means[1] - means[0]) / means[0] * 100
ax.text(0.5, 205, f'DWQ faster by +{abs(delta4):.1f}%', ha='center',
        fontsize=10, style='italic', color='gray')
# cold vs warm breakdown
ax.text(0, 195, 'cold: 180s\nwarm: ~37s', ha='center', fontsize=7.5, color='#555')
ax.text(1, 115, 'cold: 100s\nwarm: ~21s', ha='center', fontsize=7.5, color='#555')

# --- Shared footer ---
footer = (
    'Source: github.com/BrownBear127/qwen-mlx-bench — bench.py + pure_decode_bench.py + Hermes CLI + compression_bench.py. '
    'Stability: 210/210 clean rounds both configs (0 degradation). '
    'Takeaway: bench shape matters. DWQ wins decode-bound AND long-prompt cold-prefill workloads (memory-bandwidth-bound on Metal); '
    'Q8 GGUF slightly faster only on prefill-cached short-turn loops.'
)
fig.text(0.5, 0.01, footer, ha='center', fontsize=8.5, color='#555',
         wrap=True, style='italic')

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig('results_comparison.png', dpi=180, bbox_inches='tight')
print("Saved: results_comparison.png")
plt.close()
