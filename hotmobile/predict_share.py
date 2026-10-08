#!/usr/bin/env python3
"""Test Equation 1 as a predictor of prefill share (Section 3.2, Table 4).

Calibrate rho = R_p / R_d once, at one prompt length, then predict the prefill
share at every other length from phi = 1 / (1 + rho * N_o / N_p), using each
point's measured prompt and output token counts. Report the prediction error
against the measured share.

Inputs are the two released raw-results files:
  cpu-llm-latency/data/prefill_reps_raw.jsonl      (Platform A, per run)
  mlx-llm-latency/mlx_prefill_results.json         (Platform B, per run)
"""

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

CPU_RAW = Path.home() / "workspace/research/cpu-llm-latency/data/prefill_reps_raw.jsonl"
MLX_RESULTS = Path.home() / "workspace/research/paper2-mlx/mlx_prefill_results.json"

# Calibrate at the ~630-token point: the middle of the sweep, past the short-prompt
# region where fixed per-request costs distort the rates, and before any collapse.
CALIBRATION_TARGET_CPU = 600      # target_words key in the CPU file (-> 678 tokens)
CALIBRATION_TARGET_MLX = 600      # target_prompt_tokens key in the MLX file (-> 629 tokens)

# Below this many prompt tokens fixed costs dominate a request; reported separately.
SHORT_PROMPT_TOKENS = 300


def point(runs, np_key, no_key, rp_key, rd_key, phi_key, phi_scale):
    return dict(
        Np=st.mean(r[np_key] for r in runs),
        No=st.mean(r[no_key] for r in runs),
        rho=st.mean(r[rp_key] for r in runs) / st.mean(r[rd_key] for r in runs),
        phi=st.mean(r[phi_key] for r in runs) / phi_scale,
    )


def load_cpu():
    groups = defaultdict(list)
    with CPU_RAW.open() as fh:
        for line in fh:
            r = json.loads(line)
            groups[r["target_words"]].append(r)
    pts = {k: point(v, "prompt_tok", "decode_tok", "prefill_tps", "decode_tps", "prefill_pct", 100)
           for k, v in groups.items()}
    return {"A · CPU · Qwen2.5-7B": (pts, CALIBRATION_TARGET_CPU)}


def load_mlx():
    groups = defaultdict(lambda: defaultdict(list))
    for r in json.loads(MLX_RESULTS.read_text())["results"]:
        if r.get("error"):
            continue
        groups[r["model"].split("/")[-1]][r["target_prompt_tokens"]].append(r)
    out = {}
    for model, by_len in sorted(groups.items()):
        pts = {k: point(v, "prompt_tokens", "generation_tokens", "prompt_tps", "generation_tps",
                        "prefill_fraction", 1)
               for k, v in by_len.items()}
        out[f"B · GPU · {model.replace('-Instruct-4bit', '')}"] = (pts, CALIBRATION_TARGET_MLX)
    return out


def main() -> int:
    try:
        configs = {**load_cpu(), **load_mlx()}
    except (OSError, KeyError, ValueError) as exc:
        print(f"cannot read results: {exc}", file=sys.stderr)
        return 1

    for name, (pts, cal_key) in configs.items():
        rho_cal = pts[cal_key]["rho"]
        print(f"\n{name}   rho calibrated at {pts[cal_key]['Np']:.0f} tokens = {rho_cal:.2f}")
        print(f"  {'N_p':>6} {'N_o':>5} {'measured':>9} {'predicted':>10} {'error':>7}")
        for k in sorted(pts, key=lambda k: pts[k]["Np"]):
            p = pts[k]
            pred = 1 / (1 + rho_cal * p["No"] / p["Np"])
            err = 100 * (pred - p["phi"])
            flag = "  (short prompt)" if p["Np"] < SHORT_PROMPT_TOKENS else ""
            print(f"  {p['Np']:6.0f} {p['No']:5.1f} {100 * p['phi']:8.1f}% {100 * pred:9.1f}% "
                  f"{err:+6.1f}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
