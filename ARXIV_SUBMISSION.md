# arXiv submission — ready-to-paste bundle

**Upload file:** `arxiv-submission.tar.gz` (repo root) — contains `main.tex`,
`references.bib`, `main.bbl`, and an `anc/` folder (harnesses + raw data shown
as downloadable ancillary files). arXiv compiles it with its own TeX Live;
`main.bbl` is included so it doesn't need to run BibTeX.

Submit at: https://arxiv.org/submit

---

## Metadata (paste into the arXiv form)

**Title**
```
Prefill Is the Bottleneck: An Empirical Study of CPU-Only On-Device LLM Latency and One Lever That Exploits It
```

**Authors**
```
Bapista Khan
```
Affiliation: Collab-Foundry / NeuronAI. (Solo author.)

**Abstract** (plain text — paste as-is)
```
Sovereign, offline-first AI increasingly runs large language models (LLMs) on
commodity CPUs with no GPU, yet latency intuition remains grounded in GPU
serving, where autoregressive decode dominates. We instrument end-to-end
inference of a quantized 7B model (Qwen2.5-7B, Q4) on a single CPU-only machine
(AMD Ryzen 7 8845HS, 8 cores / 16 threads, 14 GiB) and sweep prompt length from
55 to 2,336 tokens (5 repetitions per point). Prefill -- reading the prompt --
grows from 38% of end-to-end latency at 55 tokens to 95% at 2,336 tokens,
crossing 90% for prompts beyond ~1,300 tokens. Prefill time scales with prompt
length while decode stays roughly flat (~11-12 tok/s), so end-to-end latency on
CPU is governed by context length, not output length -- inverting the GPU-era
assumption. Error bars are tight (prefill fraction 91+/-0.1% at 1,299 tokens),
and the effect is not model-specific: Llama-3.1-8B and Gemma2-9B also sit at
95-96% prefill at ~1,300 tokens. We further find prefill speed is non-monotonic
in quantization: the 8-bit build prefills fastest and the intermediate K-quant
slowest, inverting the "quantize-down-for-speed" heuristic on CPU. Both effects
reproduce on a second CPU vendor (Intel Comet Lake), where prefill dominance is
if anything stronger. Finally, we translate the measurement into a deployment
lever: in a controlled test, gating a second "review/verify" model pass -- the
costliest optional stage in a typical agent pipeline -- cuts latency 2.4x with
no measurable quality loss under an order-swapped LLM judge, showing the prefill
finding pays off in practice. We release all harnesses and raw data.
```

**Primary category**
```
cs.PF   (Performance)
```
**Cross-list**
```
cs.DC   (Distributed, Parallel, and Cluster Computing)
cs.LG   (Machine Learning)
```
_Rationale: it's a systems/performance measurement study → cs.PF is the truest
primary. If you'd rather optimize for readership, cs.DC or cs.LG as primary is
defensible — but cs.PF is the honest fit._

**Comments**
```
6 pages, 1 figure, 7 tables. Code and data: https://github.com/bapista/cpu-llm-latency
```

**License** — recommend **CC BY 4.0** (most open; lets a later workshop and other
readers reuse/cite freely). The arXiv non-exclusive license is the minimal
alternative if you prefer.

**Journal reference / DOI** — leave blank (none yet).

---

## Submission checklist

1. Log in to arXiv → **Start New Submission**.
2. If prompted for an **endorsement** (likely, as a first-time cs.PF submitter):
   arXiv shows you an **endorsement code + a link**. Copy both into the email
   below and send it to an endorser (see "Who can endorse").
3. Upload `arxiv-submission.tar.gz`. Verify the **PDF arXiv generates** matches
   the committed `main.pdf` (6 pages, Figure 1 + Algorithm 1 render).
4. Paste the metadata above. Set license to CC BY 4.0.
5. Submit. You'll get an **arXiv ID** (e.g. 2607.NNNNN) after moderation (usually
   next business day).
6. Then: put the arXiv URL in the repo README (todo item #9), and start the
   workshop + supervisor-outreach steps.

---

## Endorsement request email

**Who can endorse:** someone who has published enough in **cs.PF or cs.DC** to
hold endorsement rights there. Best first ask: **Prof. Mahbub Hassan** (UNSW) —
he works in networked/edge systems and knows your work; if his endorsement
rights are in cs.NI/cs.DC rather than cs.PF, ask him to endorse for the
cross-list, or to point you to a colleague who can. Wen Hu is a fallback.

> **Subject:** arXiv endorsement request — CPU-only LLM latency (cs.PF)
>
> Dear Prof. Hassan,
>
> I hope you're well. I've finished the write-up of the on-device latency work
> we discussed — an empirical study showing that on CPU-only inference, prefill
> (not decode) dominates end-to-end latency, with a couple of counterintuitive
> findings (an 8-bit model prefills fastest; the result reproduces across two
> CPU vendors). I'm submitting it to arXiv as a solo preprint before taking it
> to an edge-ML workshop.
>
> As a first-time submitter in the Performance category (cs.PF), arXiv asks for
> an endorsement. Would you be willing to endorse me? It takes a minute:
>
>   • Endorsement code: **[PASTE CODE FROM ARXIV]**
>   • Link: **[PASTE ARXIV ENDORSEMENT LINK]**
>
> If your endorsement rights are in cs.DC/cs.NI rather than cs.PF, endorsing for
> the cross-list is just as helpful — or I'm happy to be pointed to a colleague
> who can.
>
> The paper is attached (6 pages), and code + data are open at
> github.com/bapista/cpu-llm-latency. Thank you — and I'd genuinely value any
> feedback.
>
> Best regards,
> Bapista Khan
> Collab-Foundry / NeuronAI

_Attach the compiled `main.pdf` to the email._

---

## Notes / honesty

- arXiv endorsement is per-category and only needed until you've published a few
  papers; a single endorsement clears it.
- Double-check the arXiv-generated PDF before hitting submit — arXiv's TeX Live
  has pgfplots/algorithm/algpseudocode, so it should match, but verify visually.
- Nothing in the paper is fabricated; every number traces to a file in `data/`.
