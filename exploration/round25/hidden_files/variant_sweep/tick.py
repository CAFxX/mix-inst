#!/usr/bin/env python3
"""Round-25 Track B variant sweep: cron-driven idempotent state machine.

S'(x) = P_out( S( P_in(x) ) ) XOR c over three base S-boxes
  P_in : 16 evenly-sampled of 24 input bit-permutations
  P_out: 16 evenly-sampled of 24 output bit-permutations
  c    : all 16 4-bit output XOR constants
=> 4096 variants per base box (3 x 4096 = 12288 total).

One tick: process variants for the first unfinished base box until the time
budget is exhausted, checkpointing state.json after every variant. Dead ticks
are retried naturally (state advances only on completed variants). Lockfile
prevents overlapping ticks.

Per variant: verify bijectivity + DU=4/NL=4 (cheap), synthesize standalone via
the authorized run_synth.py flow (pinned Yosys), record mapped critical-path
delay + cells + area + max fanout.

Terminal state: when all three base boxes have a stop_reason (early-stop at
crit<2.8u, convergence, or full 4096), the finalizer appends the top-10
variants per base box to ROUND25_TABLE.md, marks state.json terminal, closes
the work-registry entry, and prints the TERMINAL line (the cron worker then
disables the cron).

Polite concurrency: this tick runs ONE synth at a time (max_workers=1) and
waits while >=2 foreign yosys processes run => at most 2 concurrent heavy
synth pipelines total.
"""
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import time

R25 = "/home/hatch/workspace/mix/exploration/round25"
EXP = "/home/hatch/workspace/mix/exploration"
WORK = os.path.join(R25, "hidden_files", "variant_sweep")
os.makedirs(WORK, exist_ok=True)

STATE = os.path.join(WORK, "state.json")
LOCK = os.path.join(WORK, "tick.lock")
LOG = os.path.join(WORK, "tick.log")
TABLE = os.path.join(R25, "ROUND25_TABLE.md")
WDIR = os.path.join(WORK, "w")
os.makedirs(WDIR, exist_ok=True)

sys.path.insert(0, R25)
import gen_r25  # noqa: E402

BUDGET_S = int(os.environ.get("VS_BUDGET_S", "840"))  # ~14 min per tick
LOCK_STALE_S = 1800     # 30 min
SYNTH_TIMEOUT = 600
EARLY_STOP_CRIT = 2.8

CANDS = {
    "midori_sb0": [0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7,
                   0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6],
    "ulbc_s1": [0x8, 0x0, 0x1, 0x5, 0xc, 0x7, 0x4, 0x6,
                0x2, 0xa, 0x3, 0xd, 0xe, 0xf, 0xb, 0x9],
    "thf_blink_s0": [0x1, 0x0, 0x9, 0x3, 0x8, 0x5, 0xe, 0x7,
                     0x4, 0x2, 0xc, 0xb, 0xa, 0xf, 0x6, 0xd],
}
ORDER = ["midori_sb0", "ulbc_s1", "thf_blink_s0"]

ALL_PERMS = sorted(itertools.permutations(range(4)))          # 24
SAMPLE_IDX = [round(i * 23 / 15) for i in range(16)]            # 16 evenly spread
assert len(set(SAMPLE_IDX)) == 16 and SAMPLE_IDX[0] == 0 and SAMPLE_IDX[-1] == 23
PERMS = [ALL_PERMS[i] for i in SAMPLE_IDX]                     # p: newbit[p[i]] = oldbit[i]

STRIDE = 7919
PROC_ORDER = [(k * STRIDE) % 4096 for k in range(4096)]
assert len(set(PROC_ORDER)) == 4096


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


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


def variant_spec(vi):
    return vi // 256, (vi // 16) % 16, vi % 16


def build_table(base, ip, op, c):
    pin, pout = PERMS[ip], PERMS[op]
    return [apply_perm(base[apply_perm(x, pin)], pout) ^ c for x in range(16)]


# ---- locking ----
def acquire_lock():
    if os.path.exists(LOCK):
        try:
            pid_s, ts_s = open(LOCK).read().split()
            age = time.time() - float(ts_s)
            alive = os.path.exists(f"/proc/{pid_s}")
            if age < LOCK_STALE_S and alive:
                return False
            log(f"breaking stale lock (pid={pid_s}, age={age:.0f}s)")
        except Exception:
            pass
    with open(LOCK, "w") as f:
        f.write(f"{os.getpid()} {time.time()}")
    return True


def release_lock():
    try:
        os.remove(LOCK)
    except OSError:
        pass


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
                kids.add(pid)
                changed = True
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


# ---- synthesis ----
def parse_result(out):
    # parse ONLY the RESULT line (REF/DUT lines carry their own crit= fields)
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


def max_fanout(mapped_v):
    """Max sink count per net in a Yosys write_verilog mapped netlist."""
    sinks = {}
    cur_out = None
    with open(mapped_v) as f:
        for line in f:
            m = re.match(r"\s*\.(\w+)\(([^)]+)\)", line)
            if m:
                port, net = m.group(1), m.group(2)
                if port == "Y":
                    cur_out = net
                else:
                    sinks[net] = sinks.get(net, 0) + 1
    return max(sinks.values()) if sinks else 0


def synth_variant(cand, vi, tab):
    gate_wait()
    name = f"sbox_{cand}_v{vi:04d}"
    lines = [f"module {name}(input [63:0] x, output [63:0] y);",
             "reg [63:0] y;", "always @(*) begin"]
    lines += ["    " + l.strip() for l in gen_r25._v_sbox16_stmts(tab, "x", "y")]
    lines += ["end", "endmodule"]
    vp = os.path.join(WDIR, f"{name}.v")
    with open(vp, "w") as f:
        f.write("\n".join(lines) + "\n")
    wd = os.path.join(WDIR, f"synth_{cand}_v{vi:04d}")
    os.makedirs(wd, exist_ok=True)
    err = None
    crit = cells = area = fanout = None
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "run_synth.py"), vp, name, wd],
            capture_output=True, text=True, timeout=SYNTH_TIMEOUT)
        out = r.stdout + r.stderr
        crit, cells, area = parse_result(out)
        if crit is None:
            err = f"no RESULT in output: {out[-500:]}"
        else:
            mapped = os.path.join(wd, "_dut", f"mapped_{name}.v")
            if os.path.exists(mapped):
                try:
                    fanout = max_fanout(mapped)
                except Exception as e:
                    err = f"fanout parse failed: {e}"
            else:
                err = "mapped netlist missing"
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(wd, ignore_errors=True)
        try:
            os.remove(vp)
        except OSError:
            pass
    return crit, cells, area, fanout, err


# ---- state ----
def blank_state():
    return {"candidates": {c: {"done": [], "best": None, "stop_reason": None}
                           for c in ORDER},
            "terminal": False}


def load_state():
    if os.path.exists(STATE):
        try:
            st = json.load(open(STATE))
            for c in ORDER:
                st["candidates"].setdefault(c, {"done": [], "best": None,
                                               "stop_reason": None})
            return st
        except Exception as e:
            log(f"state.json corrupt ({e}); starting fresh (old moved aside)")
            os.rename(STATE, STATE + ".corrupt")
    return blank_state()


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, STATE)


def heartbeat():
    subprocess.run([sys.executable, "/home/hatch/workspace/system/bin/workreg.py",
                    "heartbeat", "--id", "mix-round-25-followup"],
                   capture_output=True)


def converged(done):
    ok = [r for r in done if r.get("crit") is not None]
    if len(ok) < 1024 or len(ok) < 10:
        return False
    top = sorted(ok, key=lambda r: (r["crit"], r["cells"]))[:10]
    return top[-1]["crit"] - top[0]["crit"] <= 0.1 + 1e-9


def recompute_best(done):
    ok = [r for r in done if r.get("crit") is not None]
    return min(ok, key=lambda r: (r["crit"], r["cells"], r.get("fanout") or 0)
               ) if ok else None


def process_one(st, cand, vi):
    base = CANDS[cand]
    ip, op, c = variant_spec(vi)
    tab = build_table(base, ip, op, c)
    assert len(set(tab)) == 16, f"variant {vi} not bijective!"
    du, nl = du_nl(tab)
    crit = cells = area = fanout = err = None
    if du == 4 and nl == 4:
        crit, cells, area, fanout, err = synth_variant(cand, vi, tab)
    rec = {"vi": vi, "ip": ip, "op": op, "c": c,
           "table": "".join(f"{v:x}" for v in tab), "du": du, "nl": nl,
           "crit": crit, "cells": cells, "area": area, "fanout": fanout,
           "err": err}
    cs = st["candidates"][cand]
    cs["done"].append(rec)
    if crit is not None and crit < EARLY_STOP_CRIT:
        cs["stop_reason"] = (f"early-stop: variant vi={vi} hit {crit}u < "
                             f"{EARLY_STOP_CRIT}u")
    cs["best"] = recompute_best(cs["done"])
    if not cs["stop_reason"] and converged(cs["done"]):
        b = cs["best"]
        cs["stop_reason"] = (f"converged: {len(cs['done'])} done, top-10 within "
                             f"0.1u (best {b['crit']}u/{b['cells']}c)")
    return rec


def finalize(st):
    lines = ["", "## Variant sweep results (2026-10-05 follow-up)",
             "",
             "4096-variant affine sweep per base box "
             "(16 input bit-perms x 16 output bit-perms x 16 output XOR "
             "constants), standalone mapped delay via run_synth.py (pinned "
             "Yosys). Top-10 per base box by (crit, cells):",
             ""]
    for cand in ORDER:
        cs = st["candidates"][cand]
        lines.append(f"### {cand} — {cs['stop_reason']}")
        lines.append("")
        lines.append("| # | vi | pin | pout | c | table | crit | cells | area | "
                     "fanout |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        ok = [r for r in cs["done"] if r.get("crit") is not None]
        top = sorted(ok, key=lambda r: (r["crit"], r["cells"]))[:10]
        for i, r in enumerate(top, 1):
            lines.append(
                f"| {i} | {r['vi']} | {r['ip']:x} | "
                f"{r['op']:x} | {r['c']:x} | {r['table']} | "
                f"{r['crit']} | {r['cells']} | {r['area']:.0f} | "
                f"{r['fanout']} |")
        lines.append("")
    with open(TABLE, "a") as f:
        f.write("\n".join(lines) + "\n")
    st["terminal"] = True
    save_state(st)
    subprocess.run([sys.executable, "/home/hatch/workspace/system/bin/workreg.py",
                    "done", "--id", "mix-round-25-followup"], capture_output=True)
    bests = {c: st["candidates"][c]["best"] for c in ORDER}
    log("TERMINAL: sweep complete — top-10 per base box written to "
        "ROUND25_TABLE.md")
    for c, b in bests.items():
        if b:
            log(f"  {c}: best {b['crit']}u/{b['cells']}c/area={b['area']:.0f}/"
                f"fanout={b['fanout']} vi={b['vi']}")
    print("TERMINAL: sweep complete", flush=True)


def main():
    t0 = time.time()
    if not acquire_lock():
        print("another tick is running; exiting", flush=True)
        return 0
    try:
        st = load_state()
        if st.get("terminal"):
            print("sweep already terminal; nothing to do", flush=True)
            return 0
        target = next((c for c in ORDER
                       if not st["candidates"][c]["stop_reason"]), None)
        if target is None:
            finalize(st)
            return 0
        cs = st["candidates"][target]
        done_vi = {r["vi"] for r in cs["done"]}
        todo = [vi for vi in PROC_ORDER if vi not in done_vi]
        log(f"{target}: resuming with {len(cs['done'])} done, "
            f"{len(todo)} remaining")
        n_tick = 0
        for vi in todo:
            if time.time() - t0 > BUDGET_S:
                log(f"budget exhausted after {n_tick} variants this tick")
                break
            rec = process_one(st, target, vi)
            n_tick += 1
            if n_tick % 5 == 0:
                save_state(st)
                heartbeat()
            if n_tick % 25 == 0:
                b = cs["best"]
                log(f"{target}: tick+{n_tick}, total {len(cs['done'])}/4096, "
                    f"best={b['crit']}u/{b['cells']}c" if b
                    else f"{target}: tick+{n_tick}, no success yet")
            if cs["stop_reason"]:
                log(f"{target}: {cs['stop_reason']}")
                break
        save_state(st)
        heartbeat()
        b = cs["best"]
        log(f"tick done: {target} +{n_tick} variants, total "
            f"{len(cs['done'])}/4096" +
            (f", best {b['crit']}u/{b['cells']}c" if b else ""))
        # if this candidate just finished, check global terminal
        if all(st["candidates"][c]["stop_reason"] for c in ORDER):
            finalize(st)
        return 0
    finally:
        release_lock()


if __name__ == "__main__":
    sys.exit(main())
