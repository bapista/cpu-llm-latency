# Effort-Router paper (paper 2 of 2)

**Thesis:** on CPU-only on-device deployment, where prefill dominates latency
(paper 1), route the *depth of cognition* — not model size — to cut latency
2–6× without dropping below a ≥7B quality floor.

Companion to paper 1 (`../prefill-latency-paper/`). Paper 1 = the problem
(prefill dominates); this = the system that exploits it. They cite each other
→ a coherent research *program*, not two loose papers.

## Files
- `main.tex` — full draft, pre-filled with real numbers from NeuronAI's
  `DESIGN_effort_router.md` (2026-06-21/22). Native pgfplots before/after bar
  chart. `[FILL]`/blue-notes = genuinely-owed work, not fabrication.
- `references.bib` — verified entries + self-cite to paper 1 + routing refs
  (FrugalGPT, RouteLLM). `% VERIFY` flags on a few ids.

## Headline results (dev-log measurements, warm, CPU-only, Ryzen 7 8845HS)
| Lane | Before | After |
|---|---:|---:|
| Reflex ("thanks!") | 14–25 s | 4.5 s |
| Standard plain ("unit tests") | 90.9 s | 22.1 s |
| Standard RAG ("photosynthesis") | 143.5 s | 54.7 s |
| Deep ("/think REST vs GraphQL") | 190 s | 104 s |

Two non-obvious findings carry the paper:
1. The **review/verify second model pass**, not prompt length, was the dominant
   Standard cost — gating it to Deep cut plain-Standard ~4×.
2. **Single-slot model loading** silently evicted chat↔embedder, adding ~45 s/RAG
   query; `MAX_LOADED=2` fixed it.

## Remaining before submission (honest)
1. ✅ **Quality eval** — DONE (2026-07-14). Controlled review-pass isolation,
   N=8 matched queries, order-swapped LLM-judge: review pass costs **2.41×**
   latency (11.96→28.79 s) for a quality win in only **1/8** cases (7 tie, 0
   worse). Wired into §5 Eval (Table 3, `tab:reviewpass`) + Limitations.
   Data: `data/review_pass_results.json`, harness `data/review_pass_experiment.py`.
2. **Controlled per-lane re-run** (partial): the review-pass lever is now
   controlled, but the full per-lane table (Table 2) is still dev-log. Owed:
   ≥5 reps + error bars, matched queries per lane, warm and cold.
3. ✅ **`_classify_lane` pseudocode** — DONE (2026-07-15). Algorithm 1
   (`alg:route`) in §3, faithful to `neuronai-ui/backend/main.py` (ClassifyLane
   + hot-affinity RouteEffort); needs `algorithm`+`algpseudocode` (MacTeX-full).
   Still owed: 2–3 more related-work cites (early-exit / adaptive computation,
   LLM-as-judge cost, speculative decoding).
4. ✅ **Repo live** (2026-07-14): https://github.com/bapista/cpu-llm-latency
   (`paper2/`), public, in the new Reproducibility section. URL resolves (HTTP 200).

## Build (offline)
```
pdflatex main ; bibtex main ; pdflatex main ; pdflatex main
```
Needs `pgfplots`. No Python. (No TeX on tuxedo — build on the Mac.)

## Source data
Numbers trace to `~/workspace/software/neuronai-ui/backend/DESIGN_effort_router.md`
(§11–16) and `main.py`. Re-running them cleanly = task #1 above.
