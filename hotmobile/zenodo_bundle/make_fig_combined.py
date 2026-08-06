#!/usr/bin/env python3
"""Build Figure 1 for the combined HotMobile paper.

One panel, one argument: prefill's share of end-to-end latency against context
length, on both platforms. The CPU curve climbs to ~95%; the Apple Silicon
curves start decode-bound (14-20%) and cap in the 70s. The gap between them
is the paper.

Reads only the released datasets — no new measurements.
Output: fig_combined.pdf (vector, for LaTeX) + fig_combined.png (for slides).
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Inputs (both from released, published datasets) ---
CPU_SUMMARY = Path.home() / "workspace/research/cpu-llm-latency/data/prefill_reps_summary.json"
MLX_RESULTS = Path.home() / "workspace/research/paper2-mlx/mlx_prefill_results.json"
OUT_DIR = Path(__file__).resolve().parent

# --- Style: single column, print-safe, distinguishable in greyscale ---
FIG_W_IN, FIG_H_IN = 3.4, 2.5          # ACM single column
CPU_STYLE = dict(color="#111111", marker="o", lw=2.0, ms=4.5, zorder=5)
MLX_STYLES = [
    dict(color="#1f77b4", marker="s", lw=1.4, ms=3.5, ls="-"),
    dict(color="#2ca02c", marker="^", lw=1.4, ms=3.5, ls="--"),
    dict(color="#d62728", marker="v", lw=1.4, ms=3.5, ls=":"),
]
MEMORY_WALL_TOKENS = 2029               # 3B model, Apple Silicon
# The underlying study flags and excludes one anomalous 1.5B point near 140
# tokens; we exclude it here for the same reason rather than plot a spike.
OUTLIER = ("Qwen2.5-1.5B", 140)


def load_cpu():
    rows = json.loads(CPU_SUMMARY.read_text())
    rows.sort(key=lambda r: r["prompt_tok"])
    return [r["prompt_tok"] for r in rows], [r["prefill_pct_mean"] for r in rows]


def load_mlx():
    """Aggregate raw runs to mean prefill percentage per model per sweep point."""
    data = json.loads(MLX_RESULTS.read_text())
    buckets = defaultdict(list)
    for run in data["results"]:
        prefill, decode = run["prefill_s"], run["decode_s"]
        total = prefill + decode
        if total <= 0:
            continue
        pct = 100.0 * prefill / total
        buckets[(run["model"], run["target_prompt_tokens"])].append((run["prompt_tokens"], pct))

    series = defaultdict(list)
    for (model, _target), points in buckets.items():
        toks = sum(p[0] for p in points) / len(points)
        pct = sum(p[1] for p in points) / len(points)
        series[model].append((toks, pct))

    def size_key(name):  # order 0.5B, 1.5B, 3B rather than alphabetically
        for tag, order in (("0.5B", 0), ("1.5B", 1), ("3B", 2)):
            if tag in name:
                return order
        return 99

    out = []
    for model in sorted(series, key=size_key):
        label_now = model.split("/")[-1].replace("-Instruct-4bit", "")
        pts = sorted(p for p in series[model]
                     if not (label_now == OUTLIER[0] and abs(p[0] - 169) < 40))
        label = model.split("/")[-1].replace("-Instruct-4bit", "")
        out.append((label, [p[0] for p in pts], [p[1] for p in pts]))
    return out


def main() -> int:
    cpu_x, cpu_y = load_cpu()
    mlx = load_mlx()

    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN))

    # The 50% line is where the regime flips — mark it before the data.
    # Regime 1 is everything below the 50% line: prefill is the minority cost.
    ax.axhspan(0, 50, color="#4c78a8", alpha=0.06, zorder=0)
    ax.axhline(50, color="#999999", lw=0.8, zorder=1)
    ax.text(57, 44, "1 · decode-bound", fontsize=6, color="#4c78a8", va="top")
    ax.text(57, 92, "2 · prefill-bound", fontsize=6, color="#666666", va="top")

    # Regime 3 begins where the 3B model exhausts unified memory.
    ax.axvspan(MEMORY_WALL_TOKENS, 2600, color="#d62728", alpha=0.07, zorder=0)
    ax.axvline(MEMORY_WALL_TOKENS, color="#d62728", lw=0.9, ls="--", alpha=0.7, zorder=1)
    ax.text(2560, 92, "3 · memory-bound", fontsize=6, color="#d62728",
            va="top", ha="right")

    # The reversal is the finding — point straight at it.
    ax.annotate("prefill share reverses\nas decode collapses\n(49 $\\rightarrow$ 17 tok/s)",
                xy=(2100, 68.8), xytext=(700, 26),
                fontsize=5.6, color="#d62728", ha="center",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.8,
                                connectionstyle="arc3,rad=-0.25"))

    for (label, xs, ys), style in zip(mlx, MLX_STYLES):
        ax.plot(xs, ys, label=f"Apple Silicon · {label}", **style)
    ax.plot(cpu_x, cpu_y, label="CPU · Qwen2.5-7B", **CPU_STYLE)

    ax.set_xscale("log")
    ax.set_xlabel("Prompt context (tokens, log scale)", fontsize=8)
    ax.set_ylabel("Prefill share of end-to-end latency (%)", fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_xlim(50, 2600)
    ax.set_xticks([55, 140, 300, 600, 1300, 2336])
    ax.set_xticklabels(["55", "140", "300", "600", "1.3k", "2.3k"], fontsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax.grid(True, which="major", alpha=0.18, lw=0.6)
    ax.legend(fontsize=6, loc="upper left", framealpha=0.92, handlelength=2.2)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    fig.tight_layout(pad=0.3)
    for ext in ("pdf", "png"):
        path = OUT_DIR / f"fig_combined.{ext}"
        fig.savefig(path, dpi=300)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
