#!/usr/bin/env python3
"""Model-size sweep at a fixed prompt (~1300 tok): prefill cost across 7B/8B/9B.
One model resident at a time (memory-safe); prefill is read directly from
prompt_eval_duration, which excludes load time. Different families -> this is a
size+architecture comparison, noted honestly in the paper."""
import json, urllib.request, math

URL = "http://localhost:11434/api/generate"
NS = 1e9
REPS = 3
OUT = "/home/bapista/workspace/research/prefill-latency-paper/data/model_size_summary.json"
MODELS = [("qwen2.5:7b", "7B"), ("llama3.1:8b", "8B"), ("gemma2:9b", "9B")]

BASE = ("The quick brown fox jumps over the lazy dog while the sun sets slowly "
        "over the quiet green hills and a gentle wind moves across the wide field. ")
FILLER_WORDS = 1200  # ~1300 tokens for most tokenizers
Q = "\n\nBased on the text above, reply with a single short sentence."

def gen(model, prompt, num_predict=64, keep_alive=None):
    opt = {"num_predict": num_predict, "temperature": 0, "num_ctx": 4096}
    body = {"model": model, "prompt": prompt, "stream": False, "options": opt}
    if keep_alive is not None:
        body["keep_alive"] = keep_alive
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=400) as r:
        return json.load(r)

def mstd(xs):
    n = len(xs); m = sum(xs)/n
    sd = math.sqrt(sum((x-m)**2 for x in xs)/(n-1)) if n > 1 else 0.0
    return round(m, 2), round(sd, 2)

rows = []
print(f"{'model':<16}{'params':>7}{'p_tok':>7}{'prefill_s':>12}{'pf_tps':>10}{'pf%':>8}")
for model, params in MODELS:
    try:
        gen(model, "hi", num_predict=1)  # load + warm
    except Exception as e:
        print(f"{model:<16} LOAD FAILED: {e}"); continue
    pf, tps, pct, ptoks = [], [], [], []
    for rep in range(REPS):
        nonce = f"[m {model} rep {rep} seed {rep*13+7}] "
        words = (BASE * (FILLER_WORDS // 14 + 1)).split()[:FILLER_WORDS]
        ka = 0 if rep == REPS - 1 else None   # unload after last rep to free RAM
        d = gen(model, nonce + " ".join(words) + Q, keep_alive=ka)
        pe_t = d.get("prompt_eval_count", 0) or 0
        pe_s = (d.get("prompt_eval_duration", 0) or 0) / NS
        ev_s = (d.get("eval_duration", 0) or 0) / NS
        pf.append(pe_s); ptoks.append(pe_t)
        tps.append(pe_t/pe_s if pe_s else 0)
        pct.append(100*pe_s/(pe_s+ev_s) if (pe_s+ev_s) else 0)
    ptok = round(sum(ptoks)/len(ptoks))
    pf_m, pf_sd = mstd(pf); tps_m, tps_sd = mstd(tps); pct_m, pct_sd = mstd(pct)
    row = dict(model=model, params=params, prompt_tok=ptok,
               prefill_s_mean=pf_m, prefill_s_std=pf_sd,
               prefill_tps_mean=tps_m, prefill_tps_std=tps_sd,
               prefill_pct_mean=round(pct_m), prefill_pct_std=round(pct_sd, 1))
    rows.append(row)
    print(f"{model:<16}{params:>7}{ptok:>7}{f'{pf_m}+/-{pf_sd}':>12}"
          f"{f'{tps_m}':>10}{f'{round(pct_m)}':>8}", flush=True)

with open(OUT, "w") as f:
    json.dump(rows, f, indent=2)
print("DONE ->", OUT)
