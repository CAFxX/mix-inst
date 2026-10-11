#!/usr/bin/env python3
"""Staged fitness evaluation for GA candidates.

Stages (cheap kills first):
  build  -> gcc x3 (diffprof, gen, smallcrush)
  xcheck -> C-vs-Python 10k vectors (gate)
  A      -> S0 synthesis (s0_delay.py); kill if rc!=0, delay>93.15u,
            or dominated by the Pareto archive
  B      -> S1 screen; kill on rc!=0
  C      -> S2 differential; kill if repeats>=10 or max|z|>40 (structural)
  D      -> (archive entrants only) S3 x2 configs, S4, Q1

Every statistical death records a failure annotation:
  {stage, signal{...}, hypothesis, gene_pattern}
for the analytical-failure-analysis loop (see ga.py).
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

EXP = "/home/hatch/workspace/mix/exploration"
FB = os.path.join(EXP, "fast_battery")
GA = os.path.join(EXP, "ga")
sys.path.insert(0, GA)

S0_BAR = 93.15          # 0.9 * 103.5u multiplier reference
S2_ZMAX = 40.0          # structural kill (|z| spikes = broken design)
S2_REPEATS = 10
TU = os.path.expanduser("~/tools/testu01/install")
BLD = os.path.join(FB, "build")


def _run(cmd, timeout, cwd=None, env=None):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       cwd=cwd or EXP, env=env)
    return r.returncode, r.stdout, r.stderr


# ---------------------------------------------------------- concurrency

def foreign_heavy_count():
    """Live heavy-pipeline processes not belonging to the GA.

    Counts PROCESSES (not candidate names). Rationale (2026-10-03 incident):
    the old implementation extracted candidate names via r\\d{1,2}_... and
    counted distinct names -- silently missing rh_*, r22b_*, r22c_*, seed_*
    pipelines, so 4 heavies ran while the gate saw <2. Process counting can
    only overcount (one pipeline, one matching process in practice: yosys
    child for S0, diffprof_ for S2, s1_screen for S1, RNG_test for S3), and
    overcounting errs toward backing off -- the safe direction.
    """
    try:
        out = subprocess.run(["ps", "aux"], capture_output=True, text=True,
                             timeout=15).stdout
    except Exception:
        return 0
    n = 0
    for line in out.splitlines():
        if "ps aux" in line or "grep -E" in line:
            continue
        if "seed_" in line or "ga_g" in line:
            continue  # our own GA evaluations are not foreign
        if re.search(r"yosys|RNG_test|diffprof_|s1_screen|s0_delay|practrand|/sc_|testu01",
                     line):
            n += 1
    return n


def polite_wait(logfn=None):
    """Block until fewer than 2 foreign heavy pipelines are active."""
    while foreign_heavy_count() >= 2:
        if logfn:
            logfn("polite_wait: >=2 foreign heavy pipelines, sleeping 300s")
        time.sleep(300)


# ---------------------------------------------------------- build

def build(name, logfn=None):
    os.makedirs(BLD, exist_ok=True)
    cand_dir = os.path.join(FB, "candidates", name)
    meta = json.load(open(os.path.join(cand_dir, "meta.json")))
    golden = meta["goldens"][0]["out"]
    steps = [
        (["gcc", "-O2", "-o", f"{BLD}/diffprof_{name}",
          f"{FB}/src/s2_diffprof.c", f"{cand_dir}/impl.c", "-lm"], "diffprof"),
        (["gcc", "-O2", "-o", f"{BLD}/gen_{name}",
          f"{FB}/src/s3_gen.c", f"{cand_dir}/impl.c"], "gen"),
        (["gcc", "-O2", "-o", f"{BLD}/sc_{name}",
          f"{FB}/src/s4_smallcrush.c", f"{cand_dir}/impl.c",
          f"-DGOLDEN_OUT={golden}", f"-I{TU}/include", f"-L{TU}/lib",
          "-ltestu01", "-lprobdist", "-lmylib", "-lm"], "smallcrush"),
    ]
    for cmd, what in steps:
        rc, so, se = _run(cmd, 300)
        if rc != 0:
            if logfn:
                logfn(f"build {what} FAILED rc={rc}: {se[-500:]}")
            return False
    return True


def xcheck(name, outdir, logfn=None):
    os.makedirs(outdir, exist_ok=True)
    vec = os.path.join(outdir, "xcheck_vecs.txt")
    rc, so, se = _run(
        ["python3", f"{FB}/src/xcheck.py", name, f"{BLD}/diffprof_{name}",
         "10000", vec], 600)
    if logfn:
        logfn(f"xcheck rc={rc} {(so+se)[-300:]}")
    return rc == 0


# ---------------------------------------------------------- stages

def stage_A(name, outdir, logfn=None):
    """S0 synthesis. Returns (delay, cells, area) or None (killed)."""
    polite_wait(logfn)
    rc, so, se = _run(["python3", f"{FB}/src/s0_delay.py", name, outdir],
                      3600)
    try:
        d = json.load(open(os.path.join(outdir, "s0_result.json")))
    except Exception as e:
        if logfn:
            logfn(f"S0 no result json: {e}; rc={rc}")
        return None
    if logfn:
        logfn(f"S0 delay={d.get('delay_u')} cells={d.get('cells')} "
              f"area={d.get('area')} verdict={d.get('verdict')} rc={rc}")
    if rc != 0 or d.get("verdict") != "PASS":
        return None
    if d["delay_u"] > S0_BAR:
        if logfn:
            logfn(f"S0 killed: {d['delay_u']}u > {S0_BAR}u hard bar")
        return None
    return (float(d["delay_u"]), int(d["cells"]), int(d["area"]))


def stage_B(name, outdir, logfn=None):
    """S1 screen. Returns s1_result dict or None (killed)."""
    polite_wait(logfn)
    outdir = os.path.abspath(outdir)
    rc, so, se = _run(["python3", f"{FB}/src/s1_screen.py", name, outdir],
                      5400)
    try:
        d = json.load(open(os.path.join(outdir, "s1_result.json")))
    except Exception as e:
        if logfn:
            logfn(f"S1 no result json: {e}; rc={rc}")
        return None
    if logfn:
        logfn(f"S1 verdict={d.get('verdict')} rc={rc} "
              f"lin={len(d.get('lin_rejected', []))} "
              f"diff={len(d.get('diff_rejected', []))} "
              f"pb={len(d.get('pb_rejected', []))} rd={len(d.get('red_rejected', []))}")
    if rc != 0 or d.get("verdict") != "CAL_PASS":
        return d  # killed, but return the record for failure annotation
    return d


def stage_C(name, outdir, key="0x123456789abcdef0", logfn=None):
    """S2 differential. Returns dict or None (infra fail)."""
    polite_wait(logfn)
    out = os.path.join(outdir, "s2.out")
    rc, so, se = _run([f"{BLD}/diffprof_{name}", key, "22",
                       str(S2_REPEATS)], 1800)
    open(out, "w").write(so + se)
    m = re.search(r"^(PASS|KILL)[^\n]*max_repeats=(\d+)[^\n]*max\|z\|=([\d.]+)",
                  so, re.M)
    rec = {"rc": rc, "raw": so[-2000:]}
    if m:
        rec.update({"verdict": m.group(1), "max_repeats": int(m.group(2)),
                    "max_z": float(m.group(3))})
    # spike deltas for the failure annotation
    spikes = []
    for ln in so.split("\n"):
        mm = re.match(r"\s*(0x[0-9a-fA-F]+)\s+([\d.]+)\s+", ln)
        if mm and float(mm.group(2)) > S2_ZMAX:
            spikes.append((mm.group(1), float(mm.group(2))))
    rec["spikes"] = spikes
    if logfn:
        logfn(f"S2 verdict={rec.get('verdict')} max_repeats={rec.get('max_repeats')} "
              f"max_z={rec.get('max_z')} rc={rc} spikes={len(spikes)}")
    return rec


def s2_killed(rec):
    if rec is None or rec.get("verdict") != "PASS":
        return True
    if rec.get("max_repeats", 99) >= S2_REPEATS:
        return True
    if rec.get("max_z", 1e9) > S2_ZMAX:
        return True  # structural kill (notr5/drop4 class)
    return False


def stage_D(name, outdir, logfn=None):
    """S3 x2, S4, Q1 for archive entrants. Returns dict of results."""
    polite_wait(logfn)
    res = {}
    meta = json.load(open(os.path.join(FB, "candidates", name, "meta.json")))
    key1, key2 = meta["practrand_keys"]
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = f"{TU}/lib:" + env.get("LD_LIBRARY_PATH", "")
    # S3 config 1
    rc, so, se = _run(["bash", f"{FB}/src/s3_practrand.sh", name,
                       f"{BLD}/gen_{name}", os.path.join(outdir, "s3"),
                       key1, "1"], 7200)
    res["s3"] = (rc == 0)
    if logfn:
        logfn(f"S3 cfg1 rc={rc}")
    # S3 config 2 (strided)
    polite_wait(logfn)
    rc, so, se = _run(["bash", f"{FB}/src/s3_practrand.sh", f"{name}_strided",
                       f"{BLD}/gen_{name}", os.path.join(outdir, "s3b"),
                       key2, "0x9E3779B97F4A7C15"], 7200)
    res["s3b"] = (rc == 0)
    if logfn:
        logfn(f"S3 cfg2 rc={rc}")
    # S4
    polite_wait(logfn)
    rc, so, se = _run([f"{BLD}/sc_{name}", key1], 3600, env=env)
    res["s4"] = (rc == 0 and "All tests were passed" in so)
    if logfn:
        logfn(f"S4 rc={rc} passed={'All tests were passed' in so}")
    # Q1
    polite_wait(logfn)
    qdir = os.path.join(outdir, "q1")
    os.makedirs(qdir, exist_ok=True)
    rc, so, se = _run(["python3", f"{EXP}/round13/q1_sacbic.py", name, qdir],
                      3600)
    try:
        q = json.load(open(os.path.join(qdir, f"q1_{name}.json")))
        res["q1"] = q
        res["q1_ok"] = (q.get("sac_z5") == 0)
        if logfn:
            logfn(f"Q1 sac_z5={q.get('sac_z5')} bic={q.get('bic_maxcorr'):.5f}")
    except Exception as e:
        res["q1_ok"] = False
        if logfn:
            logfn(f"Q1 failed: {e}")
    res["all_ok"] = res["s3"] and res["s3b"] and res["s4"] and res["q1_ok"]
    return res


# ---------------------------------------------------------- failure annotation

def gene_pattern(genome):
    """Compact gene-pattern tags for the association table."""
    g = genome
    pat = []
    n = g["rounds"]
    for i, t in enumerate(g["tags"]):
        if "notr" in t or "fm" in t or "keyin" in t:
            pat.append(f"trunc-ish:{t}@r{i+1}")
    fams = {}
    for t in g["tags"]:
        fams[t] = fams.get(t, 0) + 1
    for t, c in sorted(fams.items()):
        pat.append(f"{t}x{c}")
    if g.get("pbox_where", "none") != "none":
        pat.append(f"pbox:{g['pbox_where']}/{g['pbox_perm']}")
    if g.get("const_where", "none") != "none":
        pat.append(f"const:{g['const_where']}/{g['const_fam']}")
    if g.get("mask", "none") != "none":
        pat.append(f"mask:{g['mask']}")
    pat.append(f"rounds={n}")
    return pat


def _spike_bits_class(spikes):
    """Classify S2 spike deltas: which input half do they hit?"""
    lo = hi = 0
    for d, _z in spikes:
        v = int(d, 16)
        if v >> 32:
            hi += 1
        else:
            lo += 1
    if hi and not lo:
        return "high-half-only(L)"
    if lo and not hi:
        return "low-half-only(R)"
    return "both-halves"


def hypothesize(stage, genome, signal):
    """Rule-based mechanistic hypothesis + suggested fix (labeled hypothesis).

    Returns (hypothesis_text, suggested_fix_op).
    suggested_fix_op is a guided-mutation op name (see ga.py) or None.
    """
    n = genome["rounds"]
    if stage == "S1":
        lin = len(signal.get("lin_rejected", []))
        diff = len(signal.get("diff_rejected", []))
        pb = len(signal.get("pb_rejected", []))
        rd = len(signal.get("red_rejected", []))
        if lin and lin >= diff:
            return (
                f"HYPOTHESIS: linear hull through the round linears "
                f"({lin} LIN rejections) — the (a,b) rotation pairs admit a "
                f"high-bias linear trail at {n}r.",
                "guided_linear")
        if diff:
            return (
                f"HYPOTHESIS: differential weakness in F ({diff} DIFF "
                f"rejections) — the nonlinear layer/chi offsets leak a "
                f"differential trail.",
                "guided_nonlinear")
        if pb or rd:
            return (
                f"HYPOTHESIS: marginal statistical blemish (PB rej={pb}, "
                f"RD rej={rd}) — possible round self-similarity/slide "
                f"structure; round constants break the symmetry.",
                "guided_const")
        return ("HYPOTHESIS: S1 FLAG without family detail — see s1_result.json.",
                None)
    if stage == "S2":
        z = signal.get("max_z", 0)
        rep = signal.get("max_repeats", 0)
        spikes = signal.get("spikes", [])
        where = _spike_bits_class(spikes)
        nsp = len(spikes)
        # NOTE: truncation tags are final-only by genome design (notr5/drop4
        # proved mid-round truncation broken), so a spike pattern here is a
        # mid-round diffusion collapse, not a truncation artifact.
        if z > S2_ZMAX and nsp >= 10:
            return (
                f"HYPOTHESIS: systematic single-bit differential spikes "
                f"({nsp} deltas, |z| up to {z:.0f}, {where}) — mid-round "
                f"diffusion collapse; S1's marginal screen is blind to this "
                f"class (formal repeat count={rep} may be low).",
                "guided_diffusion")
        if rep >= S2_REPEATS:
            return (
                f"HYPOTHESIS: {rep} repeats on a delta — round-count phase "
                f"transition ({n}r insufficient for this F strength).",
                "guided_rounds_up")
        return (f"HYPOTHESIS: S2 killed (verdict={signal.get('verdict')}).",
                None)
    if stage == "S3":
        return (
            "HYPOTHESIS: PractRand found residual structure — linearity or "
            "weak diffusion surviving 1GB; needs MORE nonlinearity, not more "
            "linear mixing.",
            "guided_nonlinear")
    if stage == "S4":
        return (
            "HYPOTHESIS: SmallCrush rejection — specific test in s4.out; "
            "usually differential/linear residue.",
            "guided_nonlinear")
    if stage == "Q1":
        sac = signal.get("sac_z5")
        bic = signal.get("bic_maxcorr")
        if sac:
            return (
                f"HYPOTHESIS: avalanche failure (sac_z5={sac}) — insufficient "
                f"bit diffusion across the {n} rounds.",
                "guided_diffusion")
        if bic and bic > 0.02:
            return (
                f"HYPOTHESIS: output-bit correlation (bic={bic:.3f}) — "
                f"unmixed final nonlinear layer (the known notr blemish "
                f"class); the y^rotl(y,m) final-mixing cure applies.",
                "guided_finalmix")
        return ("HYPOTHESIS: Q1 killed.", None)
    return ("no hypothesis", None)


def annotate(stage, genome, signal):
    hyp, fix = hypothesize(stage, genome, signal)
    return {
        "stage": stage,
        "signal": signal,
        "hypothesis": hyp,
        "suggested_fix": fix,
        "gene_pattern": gene_pattern(genome),
    }
