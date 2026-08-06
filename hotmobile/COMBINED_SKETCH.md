# HotMobile 2027 — combined-paper sketch · drafted 2026-08-06
### Deadline 9 Oct 2026, 11:59pm AoE · ≤6 pages · sigconf 10pt · non-anonymous · hotmobile27.hotcrp.com
### ⚠️ NO SIMULTANEOUS SUBMISSION — this OR EuroMLSys, not both.

## Why combine rather than submit Paper 1 as ported

Two problems with the current port, both about venue fit rather than quality:
1. **It reads as a complete study.** Nine sections including Limitations and an Appendix — a conference paper
   compressed to six pages. HotMobile selects for *provocative and early*, and rejects well-executed work for
   being a conference paper in disguise.
2. **It's a laptop.** An AMD Ryzen with 14 GiB is not obviously mobile. A reviewer will ask why this belongs at a
   *mobile* workshop.

The combined version fixes both **using data already collected**. No new experiments.
- Paper 2's platform is an **8 GB MacBook Air** — unified memory, same silicon lineage as iPhone and iPad.
  That is a mobile systems result.
- The claim across both papers is genuinely provocative in HotMobile's register: **there is no portable
  answer to "where does on-device inference time go."**

---

## Title (pick one)
1. **Your Latency Intuition Doesn't Port: Prefill/Decode Inversion Between CPU and Apple Silicon**
2. **There Is No Portable Latency Intuition for On-Device LLMs**
3. **The Bottleneck Moves: What Two Platforms Say About On-Device LLM Latency**

→ #1. It states a claim, it's arguable, and arguable is what gets a HotMobile slot.

## The one-sentence thesis
*On-device LLM latency has no platform-independent characterisation: on CPU-class hardware prefill dominates and
the binding constraint is compute; on Apple Silicon the balance inverts and the binding constraint is memory —
so any system that schedules, places or budgets inference must measure the hardware rather than assume it.*

---

## Structure (6 pages)

### 1. Introduction — the wrong intuition (~1 page)
- Mobile and on-device AI increasingly runs LLMs locally for privacy, offline operation and cost.
- Latency intuition is inherited from GPU serving, where autoregressive **decode** dominates.
- We measured two on-device platforms end to end. **Neither matches that intuition, and they do not match
  each other.**
- Contributions: (i) the inversion, measured; (ii) the mechanism; (iii) what follows for mobile systems;
  (iv) harnesses and raw data released for both platforms.

### 2. Two platforms, two answers (~1.75 pages) ← **the centrepiece**
Compressed from five results subsections to one contrast. **This table is the paper:**

| | **CPU (x86, 14 GiB)** | **Apple Silicon (MLX, 8 GB)** |
|---|---|---|
| Prefill share of latency | 38% → **95%** (2,336 tok) | caps at **73–80%** |
| Decode throughput | flat ~11–12 tok/s | 49 tok/s → **13** past the wall |
| Per-token cost balance | prefill expensive | prefill **~12× cheaper** than decode |
| Crossover point | ~1,300 tokens (90% prefill) | model-size dependent, ~1,029 tok (largest) |
| What governs latency | **context length** | context length **and memory headroom** |
| Binding constraint | **compute** | **memory** |

Supporting, kept short: reproduces across Qwen2.5-7B / Llama-3.1-8B / Gemma2-9B; reproduces on a second CPU
vendor (Intel Comet Lake); quantization is **non-monotonic** — the 8-bit build prefills fastest, inverting
"quantize down for speed."

### 3. Why they differ (~0.75 page)
Mechanism, briefly: prefill is a parallel, compute-bound pass over the context; decode is sequential and
memory-bandwidth-bound. CPU has little parallelism to exploit, so prefill cost scales and dominates. Unified-memory
Apple Silicon parallelises prefill well, so decode's sequential cost is exposed — until weights plus KV cache
exhaust unified memory, at which point decode collapses. **The two platforms are not two points on one curve;
they are two regimes.**

### 4. What this means for mobile systems (~1.25 pages) ← **the "so what" HotMobile wants**
1. **Single-number benchmarks hide the inversion.** Reporting "tokens/sec" conceals which half of inference the
   number came from, and therefore which platform it transfers to. It transfers to neither.
2. **Placement and offload decisions inherit the wrong prior.** Schedulers that assume decode-bound behaviour
   mis-cost CPU-class edge devices, where context length is the governing variable.
3. **The memory wall makes capability discontinuous, not graceful.** Past ~2,029 tokens decode falls off a
   cliff rather than degrading — an app-level design constraint, not a tuning parameter.
4. **Quantization heuristics don't hold.** Smaller is not faster; on CPU the 8-bit build prefilled fastest.
5. **Context budgeting is a first-class lever, not a micro-optimisation.** Demonstrated: gating the costliest
   optional model pass cut latency **2.4×** with no measurable quality loss under an order-swapped LLM judge.

### 5. Open questions (~0.5 page) ← **HotMobile explicitly likes these**
- Where do **NPUs** sit on this spectrum — a third regime, or between the two?
- Does the inversion survive **MoE** and **speculative decoding**?
- **Can a runtime detect which regime it is in and adapt** — budgeting context when compute-bound, and capping
  KV growth when memory-bound? *(This is the strongest follow-on, and it is a natural PhD thesis direction.)*

### 6. Conclusion + reproducibility (~0.25 page)
Both harnesses and all raw data released:
- CPU — https://github.com/bapista/cpu-llm-latency · DOI 10.5281/zenodo.21765705
- MLX — https://github.com/bapista/mlx-llm-latency · DOI 10.5281/zenodo.21786211

---

## What to cut from the current port
Background & Related Work → fold into the Introduction. Methodology → compress to a paragraph plus a pointer to
the released harnesses. Five results subsections → the contrast table plus three short supporting sentences.
Limitations → fold honestly into §5 rather than a standalone section. Appendix (Effort-Router Lane Classifier) →
drop; it belongs in the archival version.

## What NOT to weaken
The numbers, the second-vendor reproduction, the order-swapped judge, and the released artifacts. Those are why
this is credible rather than a position piece with opinions.

## Honest risks
- Combining two studies into six pages risks doing neither justice. Mitigation: the table carries the evidence,
  the prose carries the argument.
- Reviewers may still see a laptop and a MacBook rather than phones. Mitigation: state the silicon-lineage
  argument explicitly and early — unified memory on an 8 GB device *is* the mobile constraint.
- Both preprints are public. HotMobile permits this (non-anonymous, arXiv preprints fine), but say so plainly.
