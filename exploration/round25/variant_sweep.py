#!/usr/bin/env python3
"""RV64 mix round25 Track B: affine-variant sweep of S-box candidates.

S'(x) = P_out( S( P_in(x) ) ) XOR c
  P_in : 16 evenly-sampled of 24 input bit-permutations
  P_out: 16 evenly-sampled of 24 output bit-permutations
  c    : all 16 4-bit output XOR constants
=> 4096 variants per candidate.

For each variant: verify bijectivity + DU=4/NL=4, synthesize standalone via
run_synth.py (same emission as screen_broad.py: gen_r25._v_sbox16_stmts),
record (P_in, P_out, c, crit, cells, area).

Checkpointed every 100 variants -> variant_sweep_<name>.json (resumable).
Polite gate: own in-flight <= 2, foreign yosys < 2 (sleep 60s retry).
Early stop: crit < 2.8u. Convergence skip: after >=1024 done, top-10 within 0.1u.
"""
import itertools, json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
OUT = os.path.join(R25, "sbox_variant_sweep")
sys.path.insert(0, R25)
import gen_r25

LOG = os.path.join(R25, "variant_sweep.log")
os.makedirs(OUT, exist_ok=True)

CANDS = {
    "midori_sb0": [0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6],
    "ulbc_s1":    [0x8,0x0,0x1,0x5,0xc,0x7,0x4,0x6,0x2,0xa,0x3,0xd,0xe,0xf,0xb,0x9],
    "thf_blink_s0":[0x1,0x0,0x9,0x3,0x8,0x5,0xe,0x7,0x4,0x2,0xc,0xb,0xa,0xf,0x6,0xd],
}
BASE_DELAY = {"midori_sb0": 3.0, "ulbc_s1": 3.4, "thf_blink_s0": 3.4}
ORDER = ["midori_sb0", "ulbc_s1", "thf_blink_s0"]

ALL_PERMS = sorted(itertools.permutations(range(4)))          # 24, index 0 = identity
SAMPLE_IDX = [round(i * 23 / 15) for i in range(16)]            # 16 evenly spread
assert len(set(SAMPLE_IDX)) == 16 and SAMPLE_IDX[0] == 0 and SAMPLE_IDX[-1] == 23
PERMS = [ALL_PERMS[i] for i in SAMPLE_IDX]                     # p as tuple: newbit[p[i]] = oldbit[i]

def apply_perm(x, p):
    y = 0
    for i in range(4):
        if (x >> i) & 1:
            y |= 1 << p[i]
    return y

def du_nl(tab):
    dd = {}
    for a in range(1, 16):
        for x in range(16):
            d = tab[x] ^ tab[x ^ a]
            dd[(a, d)] = dd.get((a, d), 0) + 1
    du = max(dd.values())
    wmax = 0
    pc = [bin(i).count("1") for i in range(16)]
    for a in range(1, 16):
        for b in range(1, 16):
            s = 0
            for x in range(16):
                s += 1 if (pc[a & x] + pc[b & tab[x]]) % 2 == 0 else -1
            if abs(s) > wmax:
                wmax = abs(s)
    return du, 8 - wmax // 2

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

# ---- concurrency gate ----
MY_PID = os.getpid()
def _proc_tree():
    out = subprocess.run(["ps", "-eo", "pid,ppid,comm"], capture_output=True,
                         text=True).stdout.splitlines()
    procs = {}
    for ln in out[1:]:
        p = ln.split()
        if len(p) == 3:
            try:
                procs[int(p[0])] = (int(p[1]), p[2])
            except ValueError:
                pass
    return procs

def _descendants(procs, root):
    kids = {root}
    changed = True
    while changed:
        changed = False
        for pid, (ppid, _) in procs.items():
            if ppid in kids and pid not in kids:
                kids.add(pid); changed = True
    return kids

def foreign_yosys():
    procs = _proc_tree()
    mine = _descendants(procs, MY_PID)
    return sum(1 for pid, (_, comm) in procs.items()
               if comm == "yosys" and pid not in mine)

def gate_wait():
    while True:
        n = foreign_yosys()
        if n < 2:
            return
        log(f"gate full ({n} foreign yosys), sleeping 60s")
        time.sleep(60)

# ---- synth one variant ----
# NOTE: parse ONLY the RESULT line (output also has REF/DUT lines with their
# own crit= fields; a naive first-match grabs the REF mul64 numbers).
def parse_result(out):
    for line in out.split("\n"):
        if line.startswith("RESULT"):
            crit = cells = area = None
            for tok in line.split():
                if tok.startswith("crit="):
                    crit = float(tok.split("=", 1)[1])
                elif tok.startswith("cells="):
                    cells = int(tok.split("=", 1)[1])
                elif tok.startswith("area="):
                    area = float(tok.split("=", 1)[1])
            if crit is not None and cells is not None and area is not None:
                return crit, cells, area
    return None, None, None

def synth_variant(cand, idx, tab):
    gate_wait()
    name = f"sbox_{cand}_v{idx:04d}"
    lines = [f"module {name}(input [63:0] x, output [63:0] y);",
             "reg [63:0] y;", "always @(*) begin"]
    lines += ["    " + l.strip() for l in gen_r25._v_sbox16_stmts(tab, "x", "y")]
    lines += ["end", "endmodule"]
    vp = os.path.join(OUT, f"{name}.v")
    with open(vp, "w") as f:
        f.write("\n".join(lines) + "\n")
    wd = os.path.join(OUT, f"synth_{cand}_v{idx:04d}")
    os.makedirs(wd, exist_ok=True)
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "run_synth.py"), vp, name, wd],
            capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        crit, cells, area = parse_result(out)
        if crit is None:
            return None, None, None, f"no RESULT in output: {out[-500:]}"
        return crit, cells, area, None
    except Exception as e:
        return None, None, None, f"{type(e).__name__}: {e}"
    finally:
        # keep the .v source, drop mapped/ys clutter
        for fn in os.listdir(wd):
            p = os.path.join(wd, fn)
            if os.path.isdir(p):
                subprocess.run(["rm", "-rf", p])
            elif fn.startswith("mapped_") or fn.startswith("s_"):
                os.remove(p)

# ---- variant enumeration ----
# processing order: fixed pseudo-random stride so early batches are representative
STRIDE = 7919
PROC_ORDER = [(k * STRIDE) % 4096 for k in range(4096)]
assert len(set(PROC_ORDER)) == 4096

def variant_spec(vi):
    ip = vi // 256
    op = (vi // 16) % 16
    c = vi % 16
    return ip, op, c

def build_table(base, ip, op, c):
    pin, pout = PERMS[ip], PERMS[op]
    return [apply_perm(base[apply_perm(x, pin)], pout) ^ c for x in range(16)]

def ckpt_path(cand):
    return os.path.join(R25, f"variant_sweep_{cand}.json")

def save_ckpt(cand, done, best, stop_reason, total_done):
    rec = {
        "candidate": cand,
        "base_table": "".join(f"{v:x}" for v in CANDS[cand]),
        "base_delay": BASE_DELAY[cand],
        "variants_done": total_done,
        "stop_reason": stop_reason,
        "records": done,   # completed records in processing order
        "best": best,
    }
    tmp = ckpt_path(cand) + ".tmp"
    json.dump(rec, open(tmp, "w"), indent=1)
    os.replace(tmp, ckpt_path(cand))
    subprocess.run([sys.executable, "/home/hatch/workspace/system/bin/workreg.py",
                    "heartbeat", "--id", "mix-round-25-variant-sweep"],
                   capture_output=True)

def load_ckpt(cand):
    p = ckpt_path(cand)
    if os.path.exists(p):
        return json.load(open(p))
    return None

def converged(done):
    ok = [r for r in done if r.get("crit") is not None]
    if len(ok) < 1024 or len(ok) < 10:
        return False
    top = sorted(ok, key=lambda r: (r["crit"], r["cells"]))[:10]
    return top[-1]["crit"] - top[0]["crit"] <= 0.1 + 1e-9

def run_candidate(cand):
    base = CANDS[cand]
    ck = load_ckpt(cand)
    if ck and ck.get("stop_reason"):
        log(f"{cand}: already finished ({ck['stop_reason']}), skipping")
        return ck
    done = ck["records"] if ck else []
    done_vi = {r["vi"] for r in done}
    best = ck.get("best") if ck else None
    total = len(done)
    log(f"{cand}: resuming with {total} variants done" if total else f"{cand}: starting sweep (4096 variants)")
    stop_reason = None
    lock = threading.Lock()
    since_ckpt = [0]

    def one(vi):
        nonlocal stop_reason
        ip, op, c = variant_spec(vi)
        tab = build_table(base, ip, op, c)
        # verify: bijective + DU/NL preserved (affine equivalence => must hold)
        assert len(set(tab)) == 16, f"variant {vi} not bijective!"
        du, nl = du_nl(tab)
        crit, cells, area, err = (None, None, None, None)
        if du == 4 and nl == 4:
            crit, cells, area, err = synth_variant(cand, vi, tab)
        rec = {"vi": vi, "pin": list(PERMS[ip]), "pout": list(PERMS[op]), "c": c,
               "table": "".join(f"{v:x}" for v in tab), "du": du, "nl": nl,
               "crit": crit, "cells": cells, "area": area, "err": err}
        with lock:
            done.append(rec)
            since_ckpt[0] += 1
            if crit is not None and crit < 2.8:
                stop_reason = f"early-stop: variant vi={vi} hit {crit}u < 2.8u"
            n = len(done)
            if since_ckpt[0] >= 100 or stop_reason:
                # recompute best
                ok = [r for r in done if r.get("crit") is not None]
                b = min(ok, key=lambda r: (r["crit"], r["cells"])) if ok else None
                if not stop_reason and converged(done):
                    stop_reason = (f"converged: {n} done, top-10 within 0.1u "
                                   f"(best {b['crit']}u/{b['cells']}c)")
                save_ckpt(cand, done, b, stop_reason, n)
                since_ckpt[0] = 0
                log(f"{cand}: {n}/4096 done, best={b['crit']}u/{b['cells']}c vi={b['vi']}"
                    if b else f"{cand}: {n}/4096 done, no synth success yet")
        return stop_reason is not None

    vi_list = [vi for vi in PROC_ORDER if vi not in done_vi]
    with ThreadPoolExecutor(max_workers=2) as ex:
        i = 0
        while i < len(vi_list) and not stop_reason:
            chunk = vi_list[i:i + 2]
            futs = [ex.submit(one, vi) for vi in chunk]
            for f in futs:
                f.result()   # raises if worker crashed; stop_reason checked next loop
            i += len(chunk)
    if not stop_reason:
        stop_reason = "full 4096 sweep complete"
    ok = [r for r in done if r.get("crit") is not None]
    b = min(ok, key=lambda r: (r["crit"], r["cells"])) if ok else None
    save_ckpt(cand, done, b, stop_reason, len(done))
    log(f"{cand}: FINISHED ({stop_reason}); best={b['crit']}u/{b['cells']}c/area={b['area']:.0f} "
        f"vi={b['vi']} pin={b['pin']} pout={b['pout']} c={b['c']}" if b
        else f"{cand}: FINISHED ({stop_reason}); no successful synth")
    return {"candidate": cand, "stop_reason": stop_reason, "best": b}

def main():
    log("variant sweep starting")
    for cand in ORDER:
        run_candidate(cand)
    log("variant sweep: all candidates done")

if __name__ == "__main__":
    main()
