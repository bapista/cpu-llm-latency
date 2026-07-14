# CPU-Only On-Device LLM Latency

Code, data, and manuscripts for a two-paper program on the latency of running
large language models **on commodity CPUs with no GPU** — the operating regime
of sovereign, offline-first AI.

The two papers form a problem→system pair and cross-cite each other:

| Dir | Paper | One line |
|-----|-------|----------|
| [`paper1/`](paper1/) | **Prefill Is the Bottleneck** | On CPU-only inference, *prefill* (not decode) dominates end-to-end latency — 92–96% at realistic prompt lengths, stable across 7B–9B model families. |
| [`paper2/`](paper2/) | **Spend Cognition, Not Parameters** | An *effort router* that routes the depth of cognition (not model size) to cut latency 2–6× above a ≥7B quality floor; the dominant lever is gating an extra review model pass. |

## Hardware

All measurements: AMD Ryzen 7 8845HS (8C/16T, Zen 4), 14 GiB shared APU memory,
**CPU-only** (integrated Radeon 780M unused), Ollama (llama.cpp), quantized 7–9B
models. See each paper's methodology section for the exact protocol.

## Layout

```
paper1/  prefill-dominated latency study
  main.tex  references.bib  README.md
  data/     benchmark harnesses (prefill_bench.py, model_size_sweep.py) + raw JSONL/JSON
paper2/  effort-router study
  main.tex  references.bib  README.md
  data/     review_pass_experiment.py + review_pass_results.json
```

## Build the papers (offline)

```
cd paper1   # or paper2
pdflatex main ; bibtex main ; pdflatex main ; pdflatex main
```

Needs `pgfplots` (TeX Live / MacTeX). Figures render natively at compile time —
no Python needed to build the PDFs.

## Reproduce the measurements

Each `data/` directory holds the self-contained Python harness (standard library
only; talks to a local Ollama on `localhost:11434`). See each paper's README for
the exact re-run command and which models must be resident.

## Data honesty

No measurements are invented. Every number in the papers traces to a raw file in
the corresponding `data/` directory.

## Author

Bapista Khan — Collab-Foundry / NeuronAI — bapistakhan@gmail.com
