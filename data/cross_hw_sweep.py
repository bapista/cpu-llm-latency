#!/usr/bin/env python3
"""Cross-hardware sweep for the prefill-latency paper.

Runs the two generalization-critical measurements on ANY machine (a second CPU
class), so the results drop straight into the paper's tables next to the Ryzen 7
8845HS numbers and show the findings are not an AMD/Zen-4 artifact:

  (1) prompt-length prefill% curve  -> does prefill still dominate, and rise
      with prompt length, on this CPU?
  (2) Q4/Q5/Q8 quant ordering       -> is Q8_0 still the fastest to prefill
      (the non-monotonic finding), or is that microarchitecture-specific?

Self-contained: standard library only, talks to a local Ollama. Copy this one
file to the target box and run:

    python3 cross_hw_sweep.py

Env knobs (all optional):
    OLLAMA_BASE   default http://localhost:11434
    REPS          default 5
    LENGTHS       comma-separated token targets, default "64,384,1300,2300"

Captures hardware provenance (arch, CPU, cores, RAM, Ollama version) and writes
cross_hw_<hostname>.json next to this script. Commit that file to data/ and add
one row per machine to the paper's Table 2 (sweep) / Table 5 (quant)."""
import json, os, platform, socket, subprocess, urllib.request, math

OLLAMA = os.environ.get("OLLAMA_BASE", "http://localhost:11434").rstrip("/")
URL = OLLAMA + "/api/generate"
NS = 1e9
REPS = int(os.environ.get("REPS", "5"))
LENGTHS = [int(x) for x in os.environ.get("LENGTHS", "64,384,1300,2300").split(",")]
HERE = os.path.dirname(os.path.abspath(__file__))

# Same models as the reference run, so numbers are directly comparable.
BASE_MODEL = os.environ.get("BASE_MODEL", "qwen2.5:7b")   # Q4, the curve model
QUANTS = [
    ("qwen2.5:7b", "Q4_K_M"),
    ("qwen2.5:7b-instruct-q5_K_M", "Q5_K_M"),
    ("qwen2.5:7b-instruct-q8_0", "Q8_0"),
]

FILLER = ("The quick brown fox jumps over the lazy dog while the sun sets "
          "slowly over the quiet green hills and a gentle wind moves across "
          "the wide field. ")
Q = "\n\nBased on the text above, reply with a single short sentence."


def hardware():
    """Best-effort hardware provenance; never fails."""
    info = {"hostname": socket.gethostname(), "arch": platform.machine(),
            "system": platform.system(), "cpu": platform.processor() or "?",
            "cores_logical": os.cpu_count()}
    try:  # Linux CPU model + RAM
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    info["cpu"] = line.split(":", 1)[1].strip(); break
        with open("/proc/meminfo") as f:
            kb = int(f.readline().split()[1])
            info["ram_gib"] = round(kb / 1024 / 1024, 1)
    except Exception:
        pass
    if info["cpu"] in ("", "?"):                       # macOS fallback
        try:
            info["cpu"] = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], timeout=5
            ).decode().strip()
        except Exception:
            pass
    try:
        with urllib.request.urlopen(OLLAMA + "/api/version", timeout=5) as r:
            info["ollama_version"] = json.load(r).get("version", "?")
    except Exception:
        info["ollama_version"] = "?"
    return info


def have_model(name):
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=10) as r:
            return any(m["name"] == name for m in json.load(r).get("models", []))
    except Exception:
        return False


def gen(model, prompt, num_predict=64, keep_alive=None):
    opt = {"num_predict": num_predict, "temperature": 0, "num_ctx": 4096}
    body = {"model": model, "prompt": prompt, "stream": False, "options": opt}
    if keep_alive is not None:
        body["keep_alive"] = keep_alive
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r)


def mstd(xs):
    n = len(xs); m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return round(m, 2), round(sd, 2)


def filler_for(tok_target):
    words = (FILLER * (tok_target // 14 + 2)).split()[:tok_target]
    return " ".join(words)


def sweep_prompt_length(model):
    """Prefill% vs prompt length on the base (Q4) model."""
    print(f"\n[1/2] prompt-length sweep on {model}")
    print(f"{'target':>7}{'p_tok':>7}{'prefill_s':>13}{'decode_s':>11}{'pf%':>7}")
    rows = []
    for tgt in LENGTHS:
        pf, dc, pct, ptoks = [], [], [], []
        for rep in range(REPS):
            nonce = f"[len {tgt} rep {rep} seed {rep * 31 + 5}] "
            d = gen(model, nonce + filler_for(tgt) + Q)
            pe_t = d.get("prompt_eval_count", 0) or 0
            pe_s = (d.get("prompt_eval_duration", 0) or 0) / NS
            ev_s = (d.get("eval_duration", 0) or 0) / NS
            pf.append(pe_s); dc.append(ev_s); ptoks.append(pe_t)
            pct.append(100 * pe_s / (pe_s + ev_s) if (pe_s + ev_s) else 0)
        pf_m, pf_sd = mstd(pf); dc_m, dc_sd = mstd(dc); pct_m, pct_sd = mstd(pct)
        row = dict(target_tok=tgt, prompt_tok=round(sum(ptoks) / len(ptoks)),
                   prefill_s_mean=pf_m, prefill_s_std=pf_sd,
                   decode_s_mean=dc_m, decode_s_std=dc_sd,
                   prefill_pct_mean=round(pct_m, 1), prefill_pct_std=round(pct_sd, 1))
        rows.append(row)
        print(f"{tgt:>7}{row['prompt_tok']:>7}{f'{pf_m}+/-{pf_sd}':>13}"
              f"{f'{dc_m}':>11}{f'{round(pct_m)}':>7}", flush=True)
    return rows


def sweep_quant():
    """Q4/Q5/Q8 prefill at a fixed ~1300-token prompt. Graceful skip on OOM/missing."""
    print(f"\n[2/2] quant sweep at ~1300 tok")
    print(f"{'quant':<10}{'p_tok':>7}{'prefill_s':>13}{'pf_tps':>9}{'pf%':>7}")
    rows = []
    for model, quant in QUANTS:
        if not have_model(model):
            print(f"{quant:<10} SKIP (model {model} not installed — `ollama pull {model}`)")
            rows.append(dict(quant=quant, model=model, status="not_installed"))
            continue
        try:
            gen(model, "hi", num_predict=1)  # load + warm
        except Exception as e:
            print(f"{quant:<10} SKIP (load failed: {e})")
            rows.append(dict(quant=quant, model=model, status=f"load_failed: {e}"))
            continue
        pf, tps, pct, ptoks = [], [], [], []
        try:
            for rep in range(REPS):
                nonce = f"[q {quant} rep {rep} seed {rep * 17 + 3}] "
                ka = 0 if rep == REPS - 1 else None
                d = gen(model, nonce + filler_for(1300) + Q, keep_alive=ka)
                pe_t = d.get("prompt_eval_count", 0) or 0
                pe_s = (d.get("prompt_eval_duration", 0) or 0) / NS
                ev_s = (d.get("eval_duration", 0) or 0) / NS
                pf.append(pe_s); ptoks.append(pe_t)
                tps.append(pe_t / pe_s if pe_s else 0)
                pct.append(100 * pe_s / (pe_s + ev_s) if (pe_s + ev_s) else 0)
        except Exception as e:
            print(f"{quant:<10} SKIP mid-run (likely OOM: {e})")
            rows.append(dict(quant=quant, model=model, status=f"runtime_error: {e}"))
            continue
        pf_m, pf_sd = mstd(pf); tps_m, tps_sd = mstd(tps); pct_m, pct_sd = mstd(pct)
        row = dict(quant=quant, model=model, status="ok",
                   prompt_tok=round(sum(ptoks) / len(ptoks)),
                   prefill_s_mean=pf_m, prefill_s_std=pf_sd,
                   prefill_tps_mean=tps_m, prefill_tps_std=tps_sd,
                   prefill_pct_mean=round(pct_m), prefill_pct_std=round(pct_sd, 1))
        rows.append(row)
        print(f"{quant:<10}{row['prompt_tok']:>7}{f'{pf_m}+/-{pf_sd}':>13}"
              f"{f'{tps_m}':>9}{f'{round(pct_m)}':>7}", flush=True)
    return rows


def main():
    hw = hardware()
    print("=== cross-hardware sweep ===")
    for k, v in hw.items():
        print(f"  {k:<14} {v}")
    if not have_model(BASE_MODEL):
        print(f"\nBASE_MODEL {BASE_MODEL} not installed. Run: ollama pull {BASE_MODEL}")
        print("(the quant sweep also needs qwen2.5:7b-instruct-q5_K_M and -q8_0)")
        return
    out = dict(hardware=hw, reps=REPS, base_model=BASE_MODEL,
               prompt_length_sweep=sweep_prompt_length(BASE_MODEL),
               quant_sweep=sweep_quant())
    path = os.path.join(HERE, f"cross_hw_{hw['hostname']}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nDONE -> {path}")
    print("Commit this file to data/ and add a row per machine to the paper's "
          "sweep/quant tables.")


if __name__ == "__main__":
    main()
