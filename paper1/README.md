# Prefill-Dominated Latency — arXiv paper skeleton

Empirical characterization: on CPU-only on-device LLM inference, **prefill**
(not decode) dominates end-to-end latency (~87–89% in the Latency Lab runs).

## Files
- `main.tex` — the paper. Neutral `article` class, compiles on any standard
  TeX install. All `[FILL: ...]` markers render **red** so gaps are obvious.
- `references.bib` — placeholder bibliography; swap stubs for real cites.

## Build (offline)
```
pdflatex main
bibtex   main
pdflatex main
pdflatex main
```
No TeX installed? `sudo apt install texlive-latex-recommended texlive-bibtex-extra`
(or build on the Mac with MacTeX). Fully offline once installed — fits the
sovereign/offline-first ethos.

## STATUS (2026-07-14): real data filled ✅
Measured live on the NeuronAI box (AMD Ryzen 7 8845HS, CPU-only, Qwen2.5-7B Q4,
Ollama 0.19.0). Raw data + harness in `data/`.
- ✅ Hardware table, methodology, money table, **full prompt-length sweep**
  (35%→95% prefill, monotonic), native pgfplots figure — all filled with
  primary data.
- ✅ Abstract, intro, discussion, limitations, conclusion — written to the data.

### Remaining `[FILL]`
1. ✅ **Related-work citations** — DONE (14 real, verified entries in
   `references.bib`, wired into §2). A few arXiv ids/author lists carry
   `% VERIFY` comments — confirm before submission.
2. ✅ **Multi-model (7B/8B/9B) sweep** — DONE (2026-07-14). At a fixed ~1,300-tok
   prompt (N=3), prefill stays **92–96%** across Qwen2.5-7B / Llama-3.1-8B /
   Gemma2-9B — dominance is not a Qwen artifact. Wired into §4.3 (Table 4,
   `tab:modelsize`) + abstract/scope/limitations. Data: `data/model_size_summary.json`,
   harness `data/model_size_sweep.py`.
   ↳ Still owed: **multi-quant (Q4/Q5/Q8)** sweep with ≥5 reps (preliminary
   Q4-vs-Q5 datapoint from NeuronAI logs: 49 vs 36 tok/s prefill).
3. ✅ **Repo live** (2026-07-14): https://github.com/bapista/cpu-llm-latency
   (`paper1/`), public, in the Reproducibility section. URL resolves (HTTP 200).

## Build (offline)
```
pdflatex main ; bibtex main ; pdflatex main ; pdflatex main
```
Needs `pgfplots` (standard in `texlive-pictures` / MacTeX). No Python needed —
the figure renders natively at compile time.

## Re-run the benchmark
`python3 data/prefill_bench.py` (needs Ollama running with `qwen2.5:7b` resident).
Writes `data/prefill_results.jsonl`.

## Experiments that make it bulletproof
1. Prompt-length sweep → **verify:** prefill fraction rises monotonically.
2. Replicate across ≥2 model sizes → **verify:** fraction stable within X%.
3. ≥5 repetitions per config → **verify:** error bars on the money table.

## Venue path
1. **arXiv now** (cs.PF / cs.DC) — claims priority, gives a citable artifact.
2. Then a workshop: **EdgeSys** (EuroSys), **EuroMLSys**, **TinyML**, or an
   Efficient-ML / On-Device Intelligence workshop. One acceptance clears the
   publication gate Prof. Hassan named.

## Note on co-authorship
If Hassan agrees to co-supervise, adding him as co-author strengthens the PhD
case considerably. Ask before listing him — commented placeholder is in
`main.tex`.

## Data honesty
No measurements are invented in these files. Every number comes from your
Latency Lab logs. Point me at the raw output and I'll help fill the `[FILL]`s.
