#!/usr/bin/env python3
"""Tweaking sweep runner: staged probes with diagnosis-driven prioritization.

Per probe: build -> xcheck(1k) -> rtlcheck(300) -> S0 -> [window] S1+S2
           -> [Pareto win] full battery (S3x2/S4) + Q1.
Checkpoint: work/sweep_results.json (resumable). Priority queue: base order by
neighborhood promise; analytical diagnoses boost pending probes; every boost
is logged (the "diagnosis -> next probe" column).
"""
import json
import os
import re
import subprocess
import sys
import time

EXP = "/home/hatch/workspace/mix/exploration"
RTW = os.path.join(EXP, "round_tweak")
WORK = os.path.join(RTW, "work")
FB = os.path.join(EXP, "fast_battery")
CANDDIR = os.path.join(FB, "candidates")
sys.path.insert(0, RTW)
sys.path.insert(0, EXP)

os.environ["PATH"] = (os.path.expanduser("~/tools/micromamba-root/envs/sky130/bin")
                      + ":" + os.path.expanduser("~/tools/micromamba-root/bin")
                      + ":" + os.environ["PATH"])

RESULTS = os.path.join(WORK, "sweep_results.json")
DIAGLOG = os.path.join(WORK, "diagnoses.jsonl")

# Analysis kills (proven dead without synthesis; recorded, not probed).
# Z2 single-rotation: L(x)=x^rotl(x,a) is singular for EVERY a because
# 1+t^a is always divisible by (1+t) and t^32+1=(t+1)^32 in char 2, so
# L(0xFFFFFFFF)=0 (2-to-1). No P-box can repair a singular linear layer.
# Empirical confirmation: rtw_pb_rev_a03 S1 LIN rej=10/DIFF rej=10, |z|=233775.
ANALYSIS_KILLED = {
    "rtw_pb_rev_a07": "Z2 single-rot singular (proof)",
    "rtw_pb_rev_a11": "Z2 single-rot singular (proof)",
    "rtw_pb_byteswap_a03": "Z2 single-rot singular (proof)",
    "rtw_pb_byteswap_a07": "Z2 single-rot singular (proof)",
    "rtw_pb_byteswap_a11": "Z2 single-rot singular (proof)",
    "rtw_pb_nibperm_a03": "Z2 single-rot singular (proof)",
    "rtw_pb_nibperm_a07": "Z2 single-rot singular (proof)",
    "rtw_pb_nibperm_a11": "Z2 single-rot singular (proof)",
}

PARENTS = {
    "chioff13all": {"delay": 37.0, "cells": 4357, "area": 12511},
    "chioff31": {"delay": 37.5, "cells": 3863, "area": 11199},
    "fm07": {"delay": 38.8, "cells": 5053, "area": 14320},
    # 2026-10-11: ab0408 (rtw_lin_ab0408, N1) is the sweep's fastest probe:
    # 35.7u/3,970/11,453, S1 CAL_PASS, full battery PASS (S3/S4 rc=0),
    # Q1-killed only (sac_z5=12, bic=0.255 — unmixed-final-chi class).
    "ab0408": {"delay": 35.7, "cells": 3970, "area": 11453},
}
# Frontier-Q Feistel prize bar for the N8 fm-cure axis: beat r21b_3rot_ns_fm311
# (38.3u), the current fastest bic-clean Feistel point.
FQ_FEISTEL_BAR = 38.3
# neighborhoods whose battery is Q1-gated (bic<=0.02 required): N3 (fm on the
# old parents) and N8 (fm cures on the ab0408 chassis).
FQ_NBS = {"N3", "N8"}
# neighborhood -> (parent key, s1s2_window, battery_rule)
NB_CONF = {
    "N8": ("ab0408", 2.0, "fq_speed"),   # fm cure costs +0.9-1.9u (O22)
    "N9": ("chioff13all", 0.3, "pareto_any"),  # pbox x pair combos
    "N10": ("ab0408", 0.3, "strict_delay"),    # rc tweaks on fastest chassis
    "N1": ("chioff13all", 0.3, "strict_delay"),
    "N2": ("chioff13all", 0.3, "strict_delay"),   # 31-base handled per-probe
    "N3": ("fm07", 0.5, "fq_speed"),
    "N4": ("chioff13all", 0.3, "strict_delay"),
    "N5": ("chioff13all", 0.3, "strict_delay"),
    "N7": ("chioff13all", 1.0, "n7_oddterm"),  # S1/S2 if <=38u OR <=3800 cells
    "Z1": ("chioff13all", 0.1, "strict_delay"),
    "Z2": ("chioff13all", 0.3, "pareto_any"),
    "Z2b": ("chioff13all", 0.3, "pareto_any"),
    "Z3": ("chioff13all", 0.1, "strict_delay"),
    "Z4": ("chioff13all", 0.3, "strict_delay"),
}
NB_ORDER = {"N8": 0, "N9": 1, "N10": 2, "Z2b": 3, "N7": 4, "N3": 5, "N1": 6,
            "N2": 7, "N5": 8, "Z4": 9, "N4": 10, "Z1": 11, "Z3": 12, "Z2": 13}
STATS_CAP = {"N1": 5, "N3": 8, "Z4": 6, "N7": 20, "N8": 32, "N9": 3,
             "N10": 3}  # max S1+S2 near-misses per nb


def log(msg):
    print(f"[sweep {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def heavy_count():
    out = subprocess.run(["ps", "aux"], capture_output=True,
                         text=True).stdout
    n = 0
    for line in out.splitlines():
        if re.search(r"yosys|RNG_test|s1_screen|diffprof|run_fast_battery",
                     line) and "ps aux" not in line:
            # don't count our own python driver
            if "sweep.py" in line:
                continue
            n += 1
    return n


def backoff():
    while True:
        n = heavy_count()
        if n < 2:
            return
        log(f"backoff: {n} heavy pipelines active, sleeping 300s")
        time.sleep(300)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def build_cand(name):
    d = os.path.join(CANDDIR, name)
    out = os.path.join(WORK, "build", f"dp_{name}")
    os.makedirs(os.path.join(WORK, "build"), exist_ok=True)
    r = run(["gcc", "-O2", "-o", out, f"{FB}/src/s2_diffprof.c",
             f"{d}/impl.c", "-lm"])
    return r.returncode == 0, r.stderr[-500:] if r.returncode else ""


def xcheck(name, nvec):
    d = os.path.join(CANDDIR, name)
    binary = os.path.join(WORK, "build", f"dp_{name}")
    vecf = os.path.join(WORK, f"{name}.vecs")
    try:
        r = run([sys.executable, f"{FB}/src/xcheck.py", name, binary,
                 str(nvec), vecf], cwd=EXP, timeout=600)
    except subprocess.TimeoutExpired:
        # A hung xcheck must NEVER kill the sweep. Fail closed.
        subprocess.run(["pkill", "-f", f"xcheck.py.*{name}"],
                       capture_output=True, timeout=10)
        return False, f"XCHECK TIMEOUT after 600s for {name}"
    ok = r.returncode == 0 and "PASS" in r.stdout
    return ok, (r.stdout + r.stderr)[-300:]


def rtlcheck(name):
    d = os.path.join(CANDDIR, name)
    wd = os.path.join(WORK, "rtlcheck", name)
    try:
        r = run([sys.executable, f"{EXP}/check_rtl.py",
                 f"round_tweak.models.rtweak_cands.{name}",
                 f"{d}/rtl.v", name, wd, "300"], cwd=EXP, timeout=600)
    except subprocess.TimeoutExpired:
        # A hung rtlcheck must NEVER kill the sweep. Fail closed.
        subprocess.run(["pkill", "-f", f"check_rtl.py.*{name}"],
                       capture_output=True, timeout=10)
        return False, f"RTLCHECK TIMEOUT after 600s for {name}"
    ok = "PASS" in r.stdout
    return ok, (r.stdout + r.stderr)[-300:]


def s0_probe(name):
    from run_synth import synth_one
    d = os.path.join(CANDDIR, name)
    wd = os.path.join(WORK, "s0", name)
    try:
        r = synth_one(f"{d}/rtl.v", name, wd)
        return {"delay": round(r["crit"], 1), "cells": r["cells"],
                "area": round(r["area"], 0)}
    except Exception as e:
        return {"error": str(e)[-300:]}


def s1_screen(name):
    outd = os.path.join(WORK, "s1", name)  # absolute outdir (lesson)
    os.makedirs(outd, exist_ok=True)
    try:
        r = run([sys.executable, f"{FB}/src/s1_screen.py", name, outd],
                cwd=EXP, timeout=1800)
    except subprocess.TimeoutExpired:
        # A hung S1 screen must NEVER kill the sweep (2026-10-08: an
        # unhandled TimeoutExpired took the whole sweep down). Kill any
        # leftover child, record a loud timeout marker, fail closed.
        subprocess.run(["pkill", "-f", f"s1_screen.py.*{name}"],
                       capture_output=True, timeout=10)
        lp = os.path.join(outd, "s1_stdout.log")
        open(lp, "w").write(f"S1 TIMEOUT after 1800s for {name}\n")
        return lp, S1_TIMEOUT_RC
    lp = os.path.join(outd, "s1_stdout.log")
    open(lp, "w").write(r.stdout + r.stderr)
    return lp, r.returncode


def parse_s1(logp):
    rec = {"verdict": "UNKNOWN", "lin_rej": -1, "diff_rej": -1,
           "pb_rej": -1, "rd_rej": -1, "worst_z": 0.0, "worst_D": 0}
    try:
        t = open(logp).read()
    except OSError:
        return rec
    m = re.search(r"verdict:\s*(\w+)", t)
    if m:
        rec["verdict"] = m.group(1)
    m = re.search(r"LIN:\s*(\w+)\s*\(rej=(\d+)\)\s*DIFF:\s*(\w+)\s*\(rej=(\d+)\)", t)
    if m:
        rec["lin_rej"] = int(m.group(2))
        rec["diff_rej"] = int(m.group(4))
    m = re.search(r"marginal[^:]*:\s*PB rej=(\d+)\s*RD rej=(\d+)", t)
    if m:
        rec["pb_rej"] = int(m.group(1))
        rec["rd_rej"] = int(m.group(2))
    for z in re.findall(r"worst\|z\|=([\d.]+)", t):
        rec["worst_z"] = max(rec["worst_z"], float(z))
    for dd in re.findall(r"D=(\d+)/4096", t):
        rec["worst_D"] = max(rec["worst_D"], int(dd))
    return rec


S2_TIMEOUT_RC = 99  # sentinel: S2 binary hung past the 2400s timeout
S1_TIMEOUT_RC = 98  # sentinel: S1 screen hung past the 1800s timeout

def s2_run(name):
    meta = json.load(open(os.path.join(CANDDIR, name, "meta.json")))
    key = meta["practrand_keys"][0]
    kill = open(f"{FB}/ref/s2_kill_repeats.txt").read().strip()
    binary = os.path.join(WORK, "build", f"dp_{name}")
    outp = os.path.join(WORK, f"s2_{name}.log")
    try:
        r = run([binary, key, "22", kill], timeout=2400)
    except subprocess.TimeoutExpired:
        # A hung S2 binary must NEVER kill the sweep (2026-10-08: an
        # unhandled TimeoutExpired took the whole sweep down). Kill any
        # leftover child, record a loud timeout marker, fail closed.
        subprocess.run(["pkill", "-f", f"dp_{name}"],
                       capture_output=True, timeout=10)
        open(outp, "w").write(f"S2 TIMEOUT after 2400s for {name}\n")
        return outp, S2_TIMEOUT_RC
    open(outp, "w").write(r.stdout + r.stderr)
    return outp, r.returncode


def parse_s2(outp):
    rec = {"repeats_max": 0, "zmax": 0.0, "spikes": []}
    try:
        t = open(outp).read()
    except OSError:
        return rec
    for m in re.finditer(r"0x([0-9a-f]{16})\s+([\d.]+)\s+[\d.]+\s+(\d+)", t):
        delta, z, rep = m.group(1), float(m.group(2)), int(m.group(3))
        rec["repeats_max"] = max(rec["repeats_max"], rep)
        rec["zmax"] = max(rec["zmax"], z)
        if z > 15:
            rec["spikes"].append((delta, z))
    rec["spikes"].sort(key=lambda x: -x[1])
    return rec


def q1_run(name):
    outd = os.path.join(WORK, "q1")
    os.makedirs(outd, exist_ok=True)
    r = run([sys.executable, f"{EXP}/round13/q1_sacbic.py", name, outd],
            cwd=EXP, timeout=1200)
    jp = os.path.join(outd, f"q1_{name}.json")
    try:
        d = json.load(open(jp))
        return {"sac_z5": d.get("sac_z5"), "bic": d.get("bic_maxcorr")}
    except OSError:
        return {"error": (r.stdout + r.stderr)[-300:]}


def battery(name):
    r = run(["bash", f"{FB}/run_fast_battery.sh", name], cwd=EXP,
            timeout=14400)
    lp = f"{FB}/results/{name}/battery.log"
    try:
        t = open(lp).read()
        s3 = "verdict: PASS" in t
        s4 = "All tests were passed" in t
    except OSError:
        s3 = s4 = False
    return {"rc": r.returncode, "s3": s3, "s4": s4}

# ---------------- analytical failure analysis ----------------
def bit_range_of_spikes(spikes):
    bits = set()
    for delta, z in spikes:
        v = int(delta, 16)
        b = 0
        while v:
            if v & 1:
                bits.add(b)
            v >>= 1
            b += 1
    return sorted(bits)


def diagnose(rec):
    """Return (signal, hypothesis, boosts) for a probe with stats done.
    boosts: list of (nb_name, reason, amount). nb_name matches a queue
    item's "nb" (e.g. "N2"); pending probes in that neighborhood get
    prio -= amount*100 and a "name:reason" tag in boosted_by."""
    name, nb = rec["name"], rec["nb"]
    boosts = []
    s1 = rec.get("s1") or {}
    s2 = rec.get("s2") or {}
    parts, hyps = [], []

    if s2.get("spikes"):
        sp = s2["spikes"][:8]
        bits = bit_range_of_spikes(sp)
        parts.append(f"S2 spikes |z|>15 on {len(s2['spikes'])} deltas; "
                     f"worst {sp[0][0]}={sp[0][1]:.0f}; bits {bits[:12]}")
        if len(s2["spikes"]) >= 20:
            hyps.append("STRUCTURAL differential weakness across many deltas "
                        "— the construction under-diffuses; do not chase "
                        "neighbors in this direction")
        elif bits and max(bits) - min(bits) <= 16:
            hyps.append(f"LOCALIZED diffusion weakness on input bits "
                        f"{min(bits)}-{max(bits)}: the linear/chi structure "
                        f"fails to spread these bits; neighbors with "
                        f"different chi offsets or pbox placement should fix it")
            boosts.append(("N2", f"S2-localized weakness bits "
                           f"{min(bits)}-{max(bits)}", 3))
            boosts.append(("Z2", "pbox changes bit adjacency", 3))
        else:
            hyps.append("scattered differential spikes — likely weak "
                        "avalanche in specific rounds, not a clean subspace")
    if s1.get("lin_rej", 0) > 0:
        parts.append(f"S1 LIN rej={s1['lin_rej']} worst_D={s1['worst_D']}")
        hyps.append("linear characteristic weakness: the rotation set's "
                    "generated group has a small-order invariant subspace; "
                    "pairs with larger max rotation / co-prime spread break it")
        boosts.append(("N1", "LIN rej: try larger-spread pairs", 4))
    if s1.get("diff_rej", 0) > 0 or s1.get("worst_z", 0) > 6:
        parts.append(f"S1 DIFF rej={s1.get('diff_rej')} "
                     f"worst|z|={s1.get('worst_z'):.1f}")
        hyps.append("differential weakness at S1 scale: chi-offset choice "
                    "under-diffuses; different offsets should fix it")
        boosts.append(("N2", "DIFF weakness: try other chi offsets", 4))
    if s1.get("verdict") not in ("CAL_PASS", "UNKNOWN", None) and not parts:
        parts.append(f"S1 verdict={s1.get('verdict')}")
        hyps.append("non-LIN/DIFF S1 failure (PB/RD) — see log")
    return ("; ".join(parts) if parts else "no statistical failure",
            " | ".join(hyps) if hyps else "—", boosts)


def save_diagnosis(rec, signal, hypothesis, boosts):
    entry = {"name": rec["name"], "nb": rec["nb"], "signal": signal,
             "hypothesis": hypothesis,
             "boosts": [(b[0], b[1], b[2]) for b in boosts]}
    with open(DIAGLOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def apply_boosts(queue, name, boosts):
    """Reprioritize pending probes from diagnose() boosts.

    boosts: list of (nb_name, reason, amount). Every queued probe whose
    "nb" equals nb_name gets prio -= amount*100 and one "name:reason"
    tag in boosted_by (deduped per probe: a second boost from the same
    probe to the same neighborhood still cuts prio, but logs one tag).
    Mutates queue-item dict fields only (safe while main() iterates the
    list); main() re-sorts before popping the next probe.
    """
    for b in boosts:
        # Defensive: skip malformed boost entries instead of crashing the sweep.
        # (A malformed entry once killed the sweep silently 26 times.)
        if not isinstance(b, (list, tuple)) or len(b) != 3:
            continue
        nb_name, reason, amt = b
        tag = f"{name}:{reason[:40]}"
        for qq in queue:
            if qq["nb"] == nb_name:
                qq["prio"] -= amt * 100
                if not any(x.startswith(name + ":")
                           for x in qq["boosted_by"]):
                    qq["boosted_by"].append(tag)


# ---------------- promotion ----------------
def pareto_win_delay(name, rec, nb):
    s0 = rec["s0"]
    if nb == "N3":
        return s0["delay"] < PARENTS["fm07"]["delay"]
    if nb == "N8":
        # fm-cure axis: the prize is beating the fastest bic-clean Feistel
        # point (r21b_3rot_ns_fm311, 38.3u); slower cures are dominated.
        return s0["delay"] < FQ_FEISTEL_BAR
    pkey = "chioff31" if (nb == "N2" and name.endswith("_31")) else NB_CONF[nb][0]
    return s0["delay"] < PARENTS[pkey]["delay"]


def pareto_win_any(name, rec, nb):
    s0 = rec["s0"]
    pkey = "chioff31" if (nb == "N2" and name.endswith("_31")) else NB_CONF[nb][0]
    p = PARENTS[pkey]
    d = (s0["delay"] < p["delay"] or
         (s0["delay"] <= p["delay"] and s0["cells"] < p["cells"]
          and s0["area"] < p["area"]))
    if nb == "N3":
        d = d or s0["delay"] < PARENTS["fm07"]["delay"]
    return d


def in_stats_window(name, rec, nb):
    s0 = rec["s0"]
    if nb == "N7":
        # odd-term axis: S1/S2 for S0-promising (<=38u OR <=3800 cells)
        return s0["delay"] <= 38.0 or s0["cells"] <= 3800
    pkey = "chioff31" if (nb == "N2" and name.endswith("_31")) else NB_CONF[nb][0]
    if nb == "N3":
        pkey = "fm07"
    return s0["delay"] <= PARENTS[pkey]["delay"] + NB_CONF[nb][1]


def nb_rule_win(name, rec, nb):
    """The promotion gate actually used in main(): pareto_any/n7_oddterm
    neighborhoods promote on any-axis wins, everything else needs a strict
    delay win."""
    rule = NB_CONF[nb][2]
    if rule in ("pareto_any", "n7_oddterm"):
        return pareto_win_any(name, rec, nb)
    return pareto_win_delay(name, rec, nb)


# ---------------- main loop ----------------
def is_winner_rec(rec):
    """Sweep winner rule: full battery PASS (S3+S4) and Q1 sac_z5=0."""
    b = rec.get("battery") or {}
    q = rec.get("q1") or {}
    return (b.get("rc") == 0 and b.get("s3") and b.get("s4")
            and q.get("sac_z5") == 0)


def write_winners_file(results):
    """Persist the winner list to disk (2026-10-11 fix: the in-memory
    `winners` list was wiped on every restart, so the final
    'SWEEP COMPLETE: winners=[]' line was wrong — 4 winners declared in
    the log were lost from the summary)."""
    names = sorted(n for n, r in results.items() if r.get("winner"))
    with open(os.path.join(WORK, "winners.txt"), "w") as f:
        f.write("\n".join(names) + ("\n" if names else ""))
    return names


def load_results():
    if os.path.exists(RESULTS):
        return json.load(open(RESULTS))
    return {}


def save_results(res):
    tmp = RESULTS + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1)
    os.replace(tmp, RESULTS)


def probe_terminal(rec):
    """A checkpointed probe needs no further work."""
    if not rec.get("s0") or "error" in rec.get("s0", {}):
        return True
    if "analysis_kill" in rec or "battery" in rec or "promote_skipped" in rec:
        return True
    name, nb = rec["name"], rec["nb"]
    # 2026-10-08: S1 timeout is terminal — re-probing a candidate that
    # hangs S1 wastes hours (rtw_fm24_31 was probed 11x). Fail closed.
    s1 = rec.get("s1")
    if s1 and s1.get("timeout"):
        return True
    s2 = rec.get("s2")
    if s2 and not s2.get("timeout"):
        # 2026-10-08: an S2 that ran to a scientific verdict (pass or kill)
        # is done — re-running S0+S1+S2 on every restart was burning ~20 min
        # per candidate (23 such re-probes queued on the 2026-10-08 restart).
        # Pareto wins still need their battery/promotion pass, so they stay
        # non-terminal unless the battery already completed on disk.
        if not pareto_win_any(name, rec, nb):
            return True
        if battery_done(name):
            return True
        # 2026-10-09: pareto_win_any is the LAX any-axis test, but promotion
        # uses the nb's own rule (strict_delay for N1/N2/N4/N5/Z1/Z3/Z4).
        # A candidate that wins the lax test but can never win its nb rule
        # is unpromotable — its S1+S2 verdict is final. Re-probing it on
        # every restart burned ~10 min/restart forever
        # (rtw_lin_ab0103/ab0203/rk09 looped identically 5+ times).
        if not nb_rule_win(name, rec, nb):
            return True
    # win or stats-window probes need their later stages
    if pareto_win_any(name, rec, nb):
        return False
    if in_stats_window(name, rec, nb):
        return False
    return True


def battery_done(name):
    lp = f"{FB}/results/{name}/battery.log"
    if not os.path.exists(lp):
        return False
    t = open(lp).read()
    # BATTERY-PASS = completed successfully; BATTERY-FAIL = completed with failure.
    # (Do NOT match bare "FAIL" — S3 logs "no FAIL" on passing stages.)
    return "BATTERY-PASS" in t or "BATTERY-FAIL" in t


def main():
    import fcntl
    import gen_tweak
    # Exclusive instance lock (2026-10-08): two concurrent sweep.py processes
    # share the work dirs, checkpoint and log and corrupt each other's state.
    # The 5-min watchdog cron and the 30-min status task's "restart if dead"
    # step raced and ran two sweeps on the same candidate for ~30 min.
    # Fail fast when the lock is held; the OS releases it on crash/exit.
    _lockf = open(os.path.join(WORK, "sweep.lock"), "w")
    try:
        fcntl.flock(_lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("sweep.py: another instance holds the lock; exiting",
              flush=True)
        sys.exit(2)
    results = load_results()
    # Backfill winner flags for records that already meet the winner rule
    # (e.g. from incarnations before the persistence fix) and rewrite the
    # on-disk list, so it survives restarts.
    for n, r in results.items():
        if is_winner_rec(r) and not r.get("winner"):
            r["winner"] = True
            log(f"backfill WINNER flag: {n}")
    write_winners_file(results)
    save_results(results)
    specs = [(n, s, d, nb) for n, s, d, nb in gen_tweak.enumerate_specs()]
    log(f"{len(specs)} specs; {len(results)} already probed")
    # priority queue
    queue = []
    for idx, (name, spec, desc, nb) in enumerate(specs):
        if name in results and probe_terminal(results[name]):
            continue
        if name in ANALYSIS_KILLED:
            results[name] = {"name": name, "nb": nb, "desc": desc,
                             "analysis_kill": ANALYSIS_KILLED[name]}
            continue
        queue.append({"name": name, "spec": spec, "desc": desc, "nb": nb,
                      "prio": NB_ORDER[nb] * 10000 + idx, "boosted_by": []})
    save_results(results)
    stats_used = {nb: 0 for nb in NB_CONF}
    winners = []

    while queue:
        queue.sort(key=lambda q: q["prio"])
        q = queue.pop(0)
        name, nb = q["name"], q["nb"]
        rec = results.get(name, {"name": name, "nb": nb, "desc": q["desc"]})
        log(f"PROBE {name} [{nb}] prio={q['prio']} boosted_by={q['boosted_by']}")

        # --- build + correctness ---
        ok, err = build_cand(name)
        if not ok:
            rec["build"] = f"FAIL {err}"
            results[name] = rec
            save_results(results)
            continue
        ok, out = xcheck(name, 1000)
        rec["xcheck1k"] = ok
        if not ok:
            rec["xcheck_err"] = out
            results[name] = rec
            save_results(results)
            log(f"  XCHECK FAIL {name}"); continue
        ok, out = rtlcheck(name)
        rec["rtlcheck"] = ok
        if not ok:
            rec["rtlcheck_err"] = out
            results[name] = rec
            save_results(results)
            log(f"  RTLCHECK FAIL {name}"); continue

        # --- S0 ---
        backoff()
        rec["s0"] = s0_probe(name)
        results[name] = rec
        save_results(results)
        if "error" in rec["s0"]:
            log(f"  S0 ERROR {name}")
            continue
        s0 = rec["s0"]
        log(f"  S0 {name}: {s0['delay']}u / {s0['cells']} / {s0['area']:.0f}")

        # --- stats window? ---
        do_stats = in_stats_window(name, rec, nb)
        cap = STATS_CAP.get(nb, 3)
        if do_stats and stats_used[nb] >= cap and not pareto_win_delay(name, rec, nb):
            do_stats = False
            rec["stats_skipped"] = f"cap {cap} reached"
        if do_stats:
            stats_used[nb] += 1
            backoff()
            lp, rc = s1_screen(name)
            if rc == S1_TIMEOUT_RC:
                # S1 hung: not a pass, not a scientific kill — unknown.
                # Fail closed: checkpoint, log loudly, move to next probe.
                rec["s1"] = {"timeout": True, "verdict": "UNKNOWN",
                             "lin_rej": 0, "diff_rej": 0, "log": lp}
                results[name] = rec
                save_results(results)
                log(f"  *** S1 TIMEOUT {name}: screen hung >1800s, skipped "
                    f"(fail closed, no promotion)")
                continue
            rec["s1"] = parse_s1(lp)
            rec["s1"]["log"] = lp
            log(f"  S1 {name}: {rec['s1']['verdict']} "
                f"lin_rej={rec['s1']['lin_rej']} diff_rej={rec['s1']['diff_rej']}")
            backoff()
            outp, rc = s2_run(name)
            if rc == S2_TIMEOUT_RC:
                # S2 hung: not a pass, not a scientific kill — unknown.
                # Fail closed: checkpoint, log loudly, move to next probe.
                rec["s2"] = {"timeout": True, "repeats_max": 0, "zmax": 0.0,
                             "spikes": [], "log": outp}
                results[name] = rec
                save_results(results)
                log(f"  *** S2 TIMEOUT {name}: binary hung >2400s, skipped "
                    f"(fail closed, no promotion)")
                continue
            rec["s2"] = parse_s2(outp)
            rec["s2"]["log"] = outp
            log(f"  S2 {name}: repeats_max={rec['s2']['repeats_max']} "
                f"zmax={rec['s2']['zmax']:.1f} spikes={len(rec['s2']['spikes'])}")
            results[name] = rec
            save_results(results)
            # analytical failure analysis -> reprioritize
            # A per-probe exception must never kill the whole sweep:
            # the probe's stats are already checkpointed above, so log
            # loudly, skip reprioritization (fail closed), and move on.
            try:
                sig, hyp, boosts = diagnose(rec)
            except Exception as e:
                log(f"  DIAGNOSIS-ERROR {name}: {type(e).__name__}: {e}")
                continue
            if sig != "no statistical failure":
                entry = save_diagnosis(rec, sig, hyp, boosts)
                log(f"  DIAGNOSIS {name}: {sig[:100]}")
                try:
                    apply_boosts(queue, name, boosts)
                except Exception as e:
                    log(f"  BOOST-ERROR {name}: {type(e).__name__}: {e}")
                rec["diagnosis"] = entry

        # --- battery? ---
        rule = NB_CONF[nb][2]
        win = (pareto_win_any(name, rec, nb) if rule in ("pareto_any", "n7_oddterm")
               else pareto_win_delay(name, rec, nb))
        s1v = (rec.get("s1") or {}).get("verdict")
        if win and s1v in ("FLAG", "CAL_FLAG"):
            log(f"  NO-PROMOTE {name}: sweep S1 verdict={s1v}")
            rec["promote_skipped"] = f"S1 {s1v}"
            win = False
        if win and not battery_done(name):
            log(f"  PROMOTE {name} -> full battery")
            rec["xcheck10k"] = xcheck(name, 10000)[0]
            backoff()
            if nb in FQ_NBS:
                # Frontier-Q rule: Q1 gates the battery (bic<=0.02 required)
                rec["q1"] = q1_run(name)
                log(f"  Q1 {name}: {rec['q1']}")
            if nb not in FQ_NBS or (rec["q1"].get("bic") is not None
                                    and rec["q1"]["bic"] <= 0.02):
                rec["battery"] = battery(name)
                if nb not in FQ_NBS:
                    rec["q1"] = q1_run(name)
            else:
                rec["battery"] = {"skipped": "Q1 bic>0.02"}
            results[name] = rec
            save_results(results)
            blog = rec["battery"]
            log(f"  BATTERY {name}: rc={blog['rc']} s3={blog['s3']} "
                f"s4={blog['s4']} q1={rec['q1']}")
            if is_winner_rec(rec):
                winners.append(name)
                rec["winner"] = True  # persist: in-memory list dies on restart
                log(f"  *** WINNER {name} ***")
        elif win:
            log(f"  PROMOTE-SKIP {name}: battery already done")
            winners.append(name)
        results[name] = rec
        save_results(results)

    final_winners = write_winners_file(results)
    log(f"SWEEP COMPLETE: {len(results)} probed, winners={final_winners}")


if __name__ == "__main__":
    main()
