# Prefill Is the Bottleneck

Code, data, and manuscript for a measurement study of **CPU-only, on-device
LLM latency** — the operating regime of sovereign, offline-first AI.

**Finding:** on commodity CPUs with no GPU, **prefill** (reading the prompt),
not decode, dominates end-to-end latency — 92–96% at realistic prompt lengths,
rising monotonically with prompt length and stable across 7B–9B model families.
Two consequences: (1) prefill *speed* is **non-monotonic in quantization** —
the 8-bit build prefills fastest, inverting the "quantize-down-for-speed"
heuristic; (2) acting on this pays off — gating an extra "review/verify" model
pass to only the hardest queries cuts latency **2.4×** with no measurable
quality loss (order-swapped LLM judge).

> This repository was previously two companion papers (prefill-latency +
> effort-router); they were **consolidated into this single paper** on
> 2026-07-15. The two-paper drafts remain in the git history.

## Hardware

All measurements: AMD Ryzen 7 8845HS (8C/16T, Zen 4), 14 GiB shared APU memory,
**CPU-only** (integrated Radeon 780M unused), Ollama (llama.cpp), quantized 7–9B
models. See §3 (Methodology) for the exact protocol.

## Layout

```
main.tex        the paper (native pgfplots figures; no external assets to compile)
references.bib  bibliography (all arXiv ids/authors verified vs arXiv 2026-07-15)
data/           harnesses + raw results:
  prefill_bench.py / prefill_bench_reps.py   prompt-length sweep (N=5)
  model_size_sweep.py                        7B/8B/9B cross-family sweep
  quant_sweep.py                             Q4/Q5/Q8 sweep (REVERSE=1 = thermal check)
  review_pass_experiment.py                  controlled review-pass isolation (N=8)
  *_summary.json / *_raw.jsonl               raw measured data
```

## Build (offline)

```
pdflatex main ; bibtex main ; pdflatex main ; pdflatex main
```

Needs `pgfplots`, `algorithm`, `algpseudocode` (all in a full TeX Live / MacTeX).
Figures render natively at compile time — no Python needed to build the PDF.

## Reproduce the measurements

Each script is self-contained (standard library only) and talks to a local
Ollama on `localhost:11434`. Re-run e.g.:

```
python3 data/quant_sweep.py                 # Q4/Q5/Q8 prefill sweep
REVERSE=1 python3 data/quant_sweep.py       # reversed order (thermal-confound check)
python3 data/review_pass_experiment.py      # review-pass latency + LLM-judge quality
```

## Data honesty

No measurements are invented. Every number in the paper traces to a raw file in
`data/`. The review-pass experiment and the quant sweep both run against
`localhost` on the machine above; the effort-router deployment context (§6,
Appendix A) is transcribed from the production system's source.

## Remaining before submission

- **Compile to PDF** on a full-TeX machine (no TeX on the measurement box).
- **Second hardware class** (e.g. an ARM board) to show prefill dominance and the
  quant ordering generalize across CPU microarchitectures — the biggest single
  strengthener.
- Broader review-pass quality set (harder/generative prompts, human labels).
- arXiv submission (cs.PF / cs.DC) → a systems/edge-ML workshop.

## Author

Bapista Khan — Collab-Foundry / NeuronAI — bapistakhan@gmail.com
