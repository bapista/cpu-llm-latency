# Zenodo preprint — ready-to-paste bundle
### Paper 3: "The Bottleneck Moves Twice: Three Regimes of On-Device LLM Latency"
### Prepared 2026-08-06. Submit at https://zenodo.org/uploads/new

## ⚠️ READ THE PAPER FIRST
A published Zenodo record is **permanent**. New versions can be added; records cannot be withdrawn.
The paper was drafted on 2026-08-06 and has not yet been read end-to-end by the author.
**Three factual errors were caught in that draft on the same day** (the Apple Silicon model set, the
crossover direction, and a claim that both platforms measured the same model families). All are fixed —
but the error rate is the reason to read before minting a DOI.

**Specifically check:** every number in Table~2 against `data_apple_silicon_raw.json`; the CPU figures in
§2 against `data_cpu_summary.json`; and that the 2.4$\times$ gating result is stated as it is in Paper 1.

---

## Files to upload
1. **`Khan_2026_Three_Regimes_On_Device_LLM_Latency.pdf`** — the paper (4pp)
2. **`three-regimes-artifacts.zip`** — LaTeX source, `references.bib`, figure + figure-generation script,
   and both raw datasets

Both are in `hotmobile/` (the zip at the top level, the PDF inside `zenodo_bundle/`).

---

## Metadata (paste into the Zenodo form)

**Resource type:** Publication → Preprint

**Title**
```
The Bottleneck Moves Twice: Three Regimes of On-Device LLM Latency
```

**Authors**
```
Khan, Bapista
```
Affiliation: Collab-Foundry

**Description** (paste as-is)
```
On-device language models are increasingly deployed for privacy, offline operation and cost, yet the
latency intuition the community carries is inherited from datacentre GPU serving, where autoregressive
decode dominates. We instrumented end-to-end inference across two on-device platforms and four model
sizes, and found that the bottleneck does not merely differ between devices — it moves, twice, on a
single device, as a function of context length alone.

On an 8 GB Apple Silicon device a 3B model is decode-bound at short context (prefill 20% of latency),
becomes prefill-bound through the middle (peaking at 80% near 1,500 tokens), and then re-inverts toward
decode past ~2,029 tokens as weights plus KV cache exhaust unified memory and decode throughput collapses
from 49 to 17 tok/s. Smaller models on the same device never reach the third regime; a CPU-only machine,
by contrast, never leaves the second, climbing monotonically to 95% prefill.

How many regimes a deployment traverses is set by the headroom between model footprint and memory
capacity — which makes it a design-time property, not a runtime detail. We argue this has immediate
consequences for how the mobile systems community benchmarks, schedules and budgets on-device inference,
and that single-number throughput reporting conceals all three transitions.

Harnesses, raw data, LaTeX source and the figure-generation script are released with this record.
```

**Keywords**
```
on-device inference · mobile systems · large language models · latency · prefill · decode ·
memory wall · KV cache · Apple Silicon · MLX · edge AI · measurement
```

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0)
*(matches the two prior preprints; the artifact code is MIT in its own repositories)*

**Related identifiers** — add all four:
| Relation | Identifier |
|---|---|
| *is supplemented by* (or *cites*) | `10.5281/zenodo.21765705` — Paper 1, CPU study |
| *is supplemented by* (or *cites*) | `10.5281/zenodo.21786211` — Paper 2, Apple Silicon study |
| *is supplemented by* | `https://github.com/bapista/cpu-llm-latency` |
| *is supplemented by* | `https://github.com/bapista/mlx-llm-latency` |

**Version:** `1.0.0`  ·  **Language:** English

---

## After publishing
1. Add the new DOI to the LinkedIn **Publications** section (all three should be listed — currently only
   Paper 1 is).
2. Add the DOI to both GitHub repo READMEs under "Companion work".
3. Update `INTERVIEW_TALKING_POINTS.md` — the three-regime framing supersedes the two-paper story and is
   a sharper answer to "what would you research?"
4. **Do not** submit to a second venue. HotMobile forbids simultaneous submission; a preprint is fine,
   another workshop is not.
5. Draft the LinkedIn post — the reversal is the hook and the figure is the artifact.

## Then: HotMobile
Deadline **9 October 2026, 11:59pm AoE** · https://hotmobile27.hotcrp.com/ (submissions not yet open) ·
≤6pp · sigconf 10pt · non-anonymous. Current draft is **4 pages**, leaving room for the CCS block and any
expansion a reviewer would want.
