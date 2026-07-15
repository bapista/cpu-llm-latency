#!/usr/bin/env python3
"""Controlled prefill-vs-decode sweep: N repetitions per prompt length,
mean +/- sample std. Direct Ollama timing fields, warm resident model,
unique nonce per run to defeat prefix cache. CPU-only."""
import json, urllib.request, math

MODEL = "qwen2.5:7b"
URL = "http://localhost:11434/api/generate"
NS = 1e9
REPS = 5
RAW = "/home/bapista/workspace/research/prefill-latency-paper/data/prefill_reps_raw.jsonl"
SUMM = "/home/bapista/workspace/research/prefill-latency-paper/data/prefill_reps_summary.json"

def gen(prompt, num_predict=64, num_ctx=4096):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
        "options": {"num_predict": num_predict, "num_ctx": num_ctx, "temperature": 0}}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=400) as r:
        return json.load(r)

def one(prompt):
    d = gen(prompt)
    pe_t = d.get("prompt_eval_count", 0) or 0
    pe_s = (d.get("prompt_eval_duration", 0) or 0) / NS
    ev_t = d.get("eval_count", 0) or 0
    ev_s = (d.get("eval_duration", 0) or 0) / NS
    return dict(prompt_tok=pe_t, prefill_s=pe_s, prefill_tps=(pe_t/pe_s if pe_s else 0),
                decode_tok=ev_t, decode_s=ev_s, decode_tps=(ev_t/ev_s if ev_s else 0),
                total_s=(d.get("total_duration",0) or 0)/NS,
                prefill_pct=(100*pe_s/(pe_s+ev_s) if (pe_s+ev_s) else 0))

def mstd(xs):
    n = len(xs); m = sum(xs)/n
    sd = math.sqrt(sum((x-m)**2 for x in xs)/(n-1)) if n > 1 else 0.0
    return round(m, 2), round(sd, 2)

BASE = ("The quick brown fox jumps over the lazy dog while the sun sets slowly "
        "over the quiet green hills and a gentle wind moves across the wide field. ")
Q = "\n\nBased on the text above, reply with a single short sentence."
TARGETS = [0, 100, 300, 600, 1200, 2200]

gen("hi", num_predict=1)  # global warm
open(RAW, "w").close()
summary = []
print(f"REPS={REPS}  model={MODEL}")
for i, w in enumerate(TARGETS):
    runs = []
    for rep in range(REPS):
        nonce = f"[doc {i} rep {rep} seed {w*7+rep*13+3}] "  # unique -> no cache hit
        words = (BASE * (w // 14 + 1)).split()[:w] if w > 0 else []
        r = one(nonce + " ".join(words) + Q)
        r["target_words"] = w; r["rep"] = rep
        with open(RAW, "a") as f:
            f.write(json.dumps(r) + "\n")
        runs.append(r)
    ptok = round(sum(r["prompt_tok"] for r in runs)/len(runs))
    pf_m, pf_s = mstd([r["prefill_s"] for r in runs])
    pct_m, pct_s = mstd([r["prefill_pct"] for r in runs])
    ptps_m, ptps_s = mstd([r["prefill_tps"] for r in runs])
    dec_m, dec_s = mstd([r["decode_s"] for r in runs])
    dtps_m, dtps_s = mstd([r["decode_tps"] for r in runs])
    row = dict(prompt_tok=ptok, prefill_s_mean=pf_m, prefill_s_std=pf_s,
               prefill_pct_mean=round(pct_m), prefill_pct_std=round(pct_s,1),
               prefill_tps_mean=ptps_m, prefill_tps_std=ptps_s,
               decode_s_mean=dec_m, decode_s_std=dec_s,
               decode_tps_mean=dtps_m, decode_tps_std=dtps_s)
    summary.append(row)
    print(f"tok={ptok:>5}  prefill={pf_m:>6}+/-{pf_s:<5}s  pct={round(pct_m):>3}+/-{round(pct_s,1)}%  "
          f"pf_tps={ptps_m}+/-{ptps_s}  dec={dec_m}+/-{dec_s}s", flush=True)
with open(SUMM, "w") as f:
    json.dump(summary, f, indent=2)
print("DONE ->", SUMM)
