#!/usr/bin/env python3
"""Quantization sweep at a fixed prompt (~1300 tok): prefill cost across
Q4/Q5/Q8 of the SAME model (Qwen2.5-7B-Instruct). Isolates quantization —
same architecture, same tokenizer, only weight precision differs. One model
resident at a time (memory-safe); prefill is read directly from
prompt_eval_duration, which excludes load time. N=5 reps, mean +/- std."""
import json, os, urllib.request, math

URL = "http://localhost:11434/api/generate"
NS = 1e9
REPS = 5
OUT = "/home/bapista/workspace/research/cpu-llm-latency/paper1/data/quant_summary.json"
RAW = "/home/bapista/workspace/research/cpu-llm-latency/paper1/data/quant_raw.jsonl"
# Same base model (Qwen2.5-7B-Instruct), three weight precisions.
MODELS = [
    ("qwen2.5:7b", "Q4_K_M"),                 # ~4.7 GB
    ("qwen2.5:7b-instruct-q5_K_M", "Q5_K_M"), # ~5.4 GB
    ("qwen2.5:7b-instruct-q8_0", "Q8_0"),     # ~8.1 GB
]
# REVERSE=1 runs Q8->Q5->Q4 so Q8 sees the coldest CPU (thermal-confound check).
if os.environ.get("REVERSE") == "1":
    MODELS = list(reversed(MODELS))
    OUT = OUT.replace("quant_summary.json", "quant_summary_reverse.json")

BASE = ("The quick brown fox jumps over the lazy dog while the sun sets slowly "
        "over the quiet green hills and a gentle wind moves across the wide field. ")
FILLER_WORDS = 1200  # ~1300 tokens for the Qwen tokenizer
Q = "\n\nBased on the text above, reply with a single short sentence."


def gen(model, prompt, num_predict=64, keep_alive=None):
    opt = {"num_predict": num_predict, "temperature": 0, "num_ctx": 4096}
    body = {"model": model, "prompt": prompt, "stream": False, "options": opt}
    if keep_alive is not None:
        body["keep_alive"] = keep_alive
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


def mstd(xs):
    n = len(xs); m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return round(m, 2), round(sd, 2)


rows = []
print(f"{'quant':<10}{'p_tok':>7}{'prefill_s':>14}{'pf_tps':>9}{'pf%':>7}")
for model, quant in MODELS:
    try:
        gen(model, "hi", num_predict=1)  # load + warm
    except Exception as e:
        print(f"{quant:<10} LOAD FAILED: {e}"); continue
    pf, tps, pct, ptoks = [], [], [], []
    for rep in range(REPS):
        nonce = f"[q {quant} rep {rep} seed {rep * 17 + 3}] "
        words = (BASE * (FILLER_WORDS // 14 + 1)).split()[:FILLER_WORDS]
        ka = 0 if rep == REPS - 1 else None   # unload after last rep to free RAM
        d = gen(model, nonce + " ".join(words) + Q, keep_alive=ka)
        pe_t = d.get("prompt_eval_count", 0) or 0
        pe_s = (d.get("prompt_eval_duration", 0) or 0) / NS
        ev_s = (d.get("eval_duration", 0) or 0) / NS
        pf.append(pe_s); ptoks.append(pe_t)
        tps.append(pe_t / pe_s if pe_s else 0)
        pct.append(100 * pe_s / (pe_s + ev_s) if (pe_s + ev_s) else 0)
        with open(RAW, "a") as rf:
            rf.write(json.dumps(dict(quant=quant, rep=rep, prompt_tok=pe_t,
                     prefill_s=round(pe_s, 3), prefill_tps=round(pe_t / pe_s, 2) if pe_s else 0,
                     reverse=os.environ.get("REVERSE") == "1")) + "\n")
    ptok = round(sum(ptoks) / len(ptoks))
    pf_m, pf_sd = mstd(pf); tps_m, tps_sd = mstd(tps); pct_m, pct_sd = mstd(pct)
    row = dict(model=model, quant=quant, prompt_tok=ptok,
               prefill_s_mean=pf_m, prefill_s_std=pf_sd,
               prefill_tps_mean=tps_m, prefill_tps_std=tps_sd,
               prefill_pct_mean=round(pct_m), prefill_pct_std=round(pct_sd, 1))
    rows.append(row)
    print(f"{quant:<10}{ptok:>7}{f'{pf_m}+/-{pf_sd}':>14}"
          f"{f'{tps_m}':>9}{f'{round(pct_m)}':>7}", flush=True)

with open(OUT, "w") as f:
    json.dump(rows, f, indent=2)
print("DONE ->", OUT)
