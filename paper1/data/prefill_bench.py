#!/usr/bin/env python3
"""Prefill-vs-decode latency sweep on the resident Ollama model (CPU-only).
Replicates the NeuronAI Latency Lab probe, extended to a prompt-length sweep.
Uses Ollama's own timing fields. Writes JSONL results + prints a table."""
import json, urllib.request, sys

MODEL = "qwen2.5:7b"
URL = "http://localhost:11434/api/generate"
NS = 1e9
OUT = "/tmp/claude-1000/-home-bapista/967b410b-b882-4c89-bcc9-638cee87dbbb/scratchpad/prefill_results.jsonl"

def gen(prompt, num_predict=64, num_ctx=4096):
    body = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"num_predict": num_predict, "num_ctx": num_ctx, "temperature": 0},
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)

def summ(d):
    pe_t = d.get("prompt_eval_count", 0) or 0
    pe_s = (d.get("prompt_eval_duration", 0) or 0) / NS
    ev_t = d.get("eval_count", 0) or 0
    ev_s = (d.get("eval_duration", 0) or 0) / NS
    ld_s = (d.get("load_duration", 0) or 0) / NS
    tot_s = (d.get("total_duration", 0) or 0) / NS
    return dict(
        prefill_tok=pe_t, prefill_s=round(pe_s, 2),
        prefill_tps=round(pe_t / pe_s, 1) if pe_s else None,
        decode_tok=ev_t, decode_s=round(ev_s, 2),
        decode_tps=round(ev_t / ev_s, 1) if ev_s else None,
        load_s=round(ld_s, 2), ttft_s=round(ld_s + pe_s, 2), total_s=round(tot_s, 2),
        prefill_pct=round(100 * pe_s / (pe_s + ev_s)) if (pe_s + ev_s) else None,
    )

BASE = ("The quick brown fox jumps over the lazy dog while the sun sets slowly "
        "over the quiet green hills and a gentle wind moves across the wide field. ")
Q = "\n\nBased on the text above, reply with a single short sentence."
TARGETS = [0, 100, 300, 600, 1200, 2200]  # filler word counts -> ~token spread

gen("hi", num_predict=1)  # warm (discard)
open(OUT, "w").close()
print(f"{'p_tok':>6} {'pf_s':>7} {'pf_tps':>7} {'d_tok':>6} {'dec_s':>7} {'d_tps':>6} {'ttft_s':>7} {'tot_s':>7} {'pf%':>5}")
for i, w in enumerate(TARGETS):
    nonce = f"[document {i} seed {w*7+3}] "  # unique -> defeats prefix cache
    words = (BASE * (w // 14 + 1)).split()[:w] if w > 0 else []
    prompt = nonce + " ".join(words) + Q
    s = summ(gen(prompt))
    rec = {"target_words": w, **s}
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"{s['prefill_tok']:>6} {s['prefill_s']:>7} {str(s['prefill_tps']):>7} "
          f"{s['decode_tok']:>6} {s['decode_s']:>7} {str(s['decode_tps']):>6} "
          f"{s['ttft_s']:>7} {s['total_s']:>7} {str(s['prefill_pct']):>5}", flush=True)
print("DONE")
