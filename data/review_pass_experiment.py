#!/usr/bin/env python3
"""Controlled test of the review-pass lever (paper 2's headline claim).

Latency: single-pass (answer) vs two-pass (answer + review/revise), per query.
Quality: LLM-judge decides whether the revised (two-pass) answer beats the
single-pass answer -- run in BOTH orders to cancel position bias. If the
review pass rarely improves the answer, gating it off the Standard lane is
justified (the paper's claim).

Direct Ollama, warm resident qwen2.5:7b, CPU-only. No app dependency."""
import json, urllib.request, math

MODEL = "qwen2.5:7b"
URL = "http://localhost:11434/api/generate"
NS = 1e9
OUT = "/home/bapista/workspace/research/effort-router-paper/data/review_pass_results.json"

SYS = "You are a concise, accurate assistant. Answer clearly."
QUERIES = [
    "What are the benefits of unit testing?",
    "Explain the difference between REST and GraphQL.",
    "What is photosynthesis?",
    "How does the TCP three-way handshake work?",
    "Summarize the water cycle in a few sentences.",
    "What is a language model?",
    "Why is indexing important in databases?",
    "Explain the CAP theorem.",
]

def gen(prompt, num_predict=256):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
        "options": {"num_predict": num_predict, "temperature": 0, "num_ctx": 4096}}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=400) as r:
        d = json.load(r)
    return d.get("response", "").strip(), (d.get("total_duration", 0) or 0) / NS

def review_prompt(q, ans):
    return (f"{SYS}\n\nQuestion: {q}\n\nA draft answer is below. Revise it to be "
            f"more accurate, complete, and clear. Output only the improved answer.\n\n"
            f"Draft:\n{ans}")

def judge(q, a, b):
    p = (f"Two answers to a question are given. Question: {q}\n\n"
         f"Answer A:\n{a}\n\nAnswer B:\n{b}\n\n"
         f"Which answer is more accurate and helpful? Reply with EXACTLY one token: "
         f"A, B, or TIE.")
    out, _ = gen(p, num_predict=4)
    t = out.strip().upper()
    for tok in ("TIE", "A", "B"):
        if tok in t:
            return tok
    return "TIE"

def mstd(xs):
    n = len(xs); m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return round(m, 2), round(sd, 2)

gen("hi", num_predict=1)  # warm
rows, single_lat, two_lat = [], [], []
# quality tally over the review pass: does 2-pass (revised) beat 1-pass (single)?
revised_better = tie = single_better = 0

print(f"{'query':<38} {'1pass_s':>8} {'2pass_s':>8} {'verdict':>8}")
for q in QUERIES:
    ans, t1 = gen(SYS + "\n\nQuestion: " + q + "\n\nAnswer:")           # single pass
    rev, t2 = gen(review_prompt(q, ans))                                # review pass
    two = t1 + t2
    single_lat.append(t1); two_lat.append(two)
    # judge both orders: single=S, revised=R
    v1 = judge(q, ans, rev)   # A=single, B=revised
    v2 = judge(q, rev, ans)   # A=revised, B=single
    # normalize to "did revised win?"
    rev_wins = (v1 == "B") + (v2 == "A")
    sng_wins = (v1 == "A") + (v2 == "B")
    if rev_wins > sng_wins: verdict = "revised"; revised_better += 1
    elif sng_wins > rev_wins: verdict = "single"; single_better += 1
    else: verdict = "tie"; tie += 1
    rows.append(dict(query=q, single_s=round(t1, 2), two_pass_s=round(two, 2),
                     review_s=round(t2, 2), verdict=verdict, v1=v1, v2=v2))
    print(f"{q[:38]:<38} {t1:>8.2f} {two:>8.2f} {verdict:>8}", flush=True)

sm, ss = mstd(single_lat); tm, ts = mstd(two_lat)
summary = dict(
    n=len(QUERIES), model=MODEL,
    single_pass_s=dict(mean=sm, std=ss),
    two_pass_s=dict(mean=tm, std=ts),
    two_pass_overhead_x=round(tm / sm, 2) if sm else None,
    quality=dict(revised_better=revised_better, tie=tie, single_better=single_better),
    rows=rows,
)
with open(OUT, "w") as f:
    json.dump(summary, f, indent=2)
print("\n=== SUMMARY ===")
print(f"single-pass:  {sm} +/- {ss} s")
print(f"two-pass:     {tm} +/- {ts} s   ({summary['two_pass_overhead_x']}x)")
print(f"quality (review pass helped?):  revised_better={revised_better}  tie={tie}  single_better={single_better}")
print("wrote", OUT)
