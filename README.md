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

## Companion work

- **Paper 2 — [On-Device LLM Latency on Apple Silicon (MLX)](https://doi.org/10.5281/zenodo.21786211)** ·
  the same measurement on unified-memory hardware, where the bottleneck inverts
  ([code](https://github.com/bapista/mlx-llm-latency))
- **Paper 3 — [The Bottleneck Moves Twice: Three Regimes of On-Device LLM Latency](https://doi.org/10.5281/zenodo.21818301)** ·
  combines both studies: the bottleneck moves *twice* on a single device as context grows —
  decode-bound, then prefill-bound, then memory-bound
- **[Rung](https://github.com/bapista/rung)** — effort-aware, on-device-first LLM router
- **[Ratchet](https://github.com/bapista/ratchet)** — eval-and-promote gate for fine-tuned adapters

## Hardware

Primary machine: AMD Ryzen 7 8845HS (8C/16T, Zen 4), 14 GiB, **CPU-only**, Ollama
(llama.cpp). Cross-vendor replication on an **Intel Core i7-10700T** (Comet Lake) —
both findings reproduce (§4.5). See §3 for the protocol.

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

**Zero-install build (recommended):** [Tectonic](https://tectonic-typesetting.github.io)
is a single self-contained binary that fetches only the packages this paper uses:

```
tectonic main.tex          # → main.pdf, one command, no TeX distro required
```

The committed `main.pdf` was built this way (6 pages, arXiv-ready draft).

## Reproduce the measurements

Each script is self-contained (standard library only) and talks to a local
Ollama on `localhost:11434`. Re-run e.g.:

```
python3 data/quant_sweep.py                 # Q4/Q5/Q8 prefill sweep
REVERSE=1 python3 data/quant_sweep.py       # reversed order (thermal-confound check)
python3 data/review_pass_experiment.py      # review-pass latency + LLM-judge quality
```

### Cross-hardware run (second CPU class)

`data/cross_hw_sweep.py` is a self-contained one-command harness for a **second
machine** (e.g. an ARM board) — the single biggest way to strengthen the paper
(shows prefill dominance + the Q8-fastest quant ordering are not an AMD/Zen-4
artifact). Copy the one file over and run:

```
python3 cross_hw_sweep.py          # auto-detects arch/CPU/RAM; runs both sweeps
```

It needs Ollama + the same models (`qwen2.5:7b`, `qwen2.5:7b-instruct-q5_K_M`,
`-q8_0`); it gracefully skips a quant that won't fit in RAM. Output
`cross_hw_<hostname>.json` drops one comparable row into the sweep/quant tables.
Env knobs: `OLLAMA_BASE`, `REPS` (default 5), `LENGTHS`.

## Data honesty

No measurements are invented. Every number in the paper traces to a raw file in
`data/`. The review-pass experiment and the quant sweep both run against
`localhost` on the machine above; the effort-router deployment context (§6,
Appendix A) is transcribed from the production system's source.

## Remaining before submission

- **Compile to PDF** on a full-TeX machine (no TeX on the measurement box).
- ✅ **Second CPU vendor DONE** — Intel i7-10700T (Comet Lake): prefill dominance +
  Q8-fastest ordering both reproduce (§4.5, Table 6; `data/cross_hw_olympus.json`).
  Remaining: a **non-x86 (ARM/mobile)** datapoint via `data/cross_hw_sweep.py`.
- Broader review-pass quality set (harder/generative prompts, human labels).
- arXiv submission (cs.PF / cs.DC) → a systems/edge-ML workshop.

## Author

Bapista Khan — Collab-Foundry / NeuronAI — bapistakhan@gmail.com
