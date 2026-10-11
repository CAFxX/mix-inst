#!/usr/bin/env python3
"""GA main loop for the mix search.

(μ+λ) evolution, μ=20, λ=12; staged fitness (evaluate.py); Pareto archive on
(delay, cells, area); failure-annotated deaths + diagnosis-driven guided
mutation (30%) per Carlo's analytical-failure-analysis directive.

Usage:
  python3 ga/ga.py            # fresh start (seeds)
  python3 ga/ga.py --resume   # resume from ga/state/checkpoint.pkl

Stop: create ga/state/STOP, or 48h wall clock.
Runs detached: setsid nohup python3 ga/ga.py --resume > ga/run.log 2>&1 &
"""
import copy
import datetime
import json
import os
import pickle
import random
import sys
import time

EXP = "/home/hatch/workspace/mix/exploration"
GA = os.path.join(EXP, "ga")
sys.path.insert(0, GA)

from genome import (validate, random_genome, crossover, mutate, canonical,
                    fingerprint, FINAL_TAGS, GENERAL_TAGS, P64_PERMS,
                    P32_PERMS, CONST_FAM, MASK_VALS, LIN2, NL_FAM, FAM_TAGS,
                    LIN_PAIRS)  # noqa: E402
from gamodels import decode_np  # noqa: E402
from emit import emit_candidate  # noqa: E402
from seed import mine_archive, HAND_BUILT  # noqa: E402
import evaluate as EV  # noqa: E402

MU = 20
LAMBDA = 12
GUIDED_FRAC = 0.30
WALL_BUDGET_S = 48 * 3600
STATE = os.path.join(GA, "state")
os.makedirs(STATE, exist_ok=True)
os.makedirs(os.path.join(GA, "results"), exist_ok=True)
LOG = os.path.join(GA, "GA_LOG.md")


def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


# ---------------------------------------------------------- pareto utils

def dominates(a, b):
    """a dominates b on (delay, cells, area): <= all, < at least one."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def pareto_add(archive, name, point, record):
    """Insert into archive; return (added_bool, evicted_names)."""
    for n2, r2 in archive.items():
        if dominates(r2["point"], point):
            return False, []
    evicted = [n2 for n2, r2 in archive.items()
               if dominates(point, r2["point"])]
    for n2 in evicted:
        del archive[n2]
    archive[name] = dict(record, point=point)
    return True, evicted


def nondomination_rank(items):
    """items: list of (key, point|None). None point = dead (worst rank)."""
    n = len(items)
    rank = {}
    remaining = [k for k, p in items if p is not None]
    r = 0
    while remaining:
        front = [k for k in remaining
                 if not any(dominates(dict(items)[k2], dict(items)[k])
                            for k2 in remaining if k2 != k)]
        for k in front:
            rank[k] = r
        remaining = [k for k in remaining if k not in front]
        r += 1
    for k, p in items:
        if p is None:
            rank[k] = r  # dead: dominated by everyone
    return rank


def crowding(items, rank):
    """Crowding distance within each rank front (higher = more isolated)."""
    by_rank = {}
    pts = dict(items)
    for k, rk in rank.items():
        by_rank.setdefault(rk, []).append(k)
    dist = {k: 0.0 for k, _ in items}
    for rk, ks in by_rank.items():
        live = [k for k in ks if pts[k] is not None]
        if len(live) <= 2:
            for k in live:
                dist[k] = float("inf")
            continue
        for dim in range(3):
            s = sorted(live, key=lambda k: pts[k][dim])
            lo, hi = pts[s[0]][dim], pts[s[-1]][dim]
            span = hi - lo or 1.0
            dist[s[0]] = dist[s[-1]] = float("inf")
            for i in range(1, len(s) - 1):
                dist[s[i]] += (pts[s[i + 1]][dim] - pts[s[i - 1]][dim]) / span
    return dist


# ---------------------------------------------------------- guided mutation

def _set_final_tag(g, tag, r):
    g["tags"][g["rounds"] - 1] = tag


def guided_mutate(g, annotation, r):
    """Apply the annotation's suggested fix. Falls back to random mutate."""
    c = json.loads(json.dumps(g))
    op = (annotation or {}).get("suggested_fix")
    n = c["rounds"]
    try:
        if op == "guided_linear":
            # change a rotation pair on a random linear-bearing round
            cands = [i for i, t in enumerate(c["tags"]) if t in LIN2]
            i = r.choice(cands)
            fam = NL_FAM[c["tags"][i]]
            ab = r.choice([p for p in LIN_PAIRS if (fam, p) in FAM_TAGS
                           and FAM_TAGS[(fam, p)] != c["tags"][i]]
                          or [p for p in LIN_PAIRS if (fam, p) in FAM_TAGS])
            c["tags"][i] = FAM_TAGS[(fam, ab)]
        elif op == "guided_nonlinear":
            if c.get("mask", "none") == "none":
                c["mask"] = r.choice([m for m in MASK_VALS if m != "none"])
            else:
                # strengthen: swap chi offsets on a random chi round
                cands = [i for i, t in enumerate(c["tags"])
                         if t in ("chi_311", "chi32v_311", "chi32w_311",
                                  "chi_713")]
                if cands:
                    i = r.choice(cands)
                    alt = {"chi_311": ["chi32v_311", "chi32w_311"],
                           "chi32v_311": ["chi_311", "chi32w_311"],
                           "chi32w_311": ["chi_311", "chi32v_311"],
                           "chi_713": ["chi_311"]}[c["tags"][i]]
                    c["tags"][i] = r.choice(alt)
                else:
                    c["mask"] = r.choice([m for m in MASK_VALS if m != "none"])
        elif op == "guided_const":
            c["const_where"] = "round_F"
            c["const_fam"] = r.choice(CONST_FAM)
        elif op == "guided_untruncate":
            # restore the dropped linear: final notr/fm -> lin counterpart
            t = c["tags"][n - 1]
            back = {"chi_notr": "chi_311", "chi32v_notr": "chi32v_311",
                    "chi32w_notr": "chi32w_311", "s1_notr": "s1_311",
                    "ps_notr": "ps_311"}
            if t in back:
                _set_final_tag(c, back[t], r)
            else:
                _set_final_tag(c, "chi_311", r)
        elif op == "guided_diffusion":
            choice = r.random()
            if choice < 0.4 and c.get("pbox_where") != "between64":
                c["pbox_where"] = "between64"
                c["pbox_perm"] = r.choice(P64_PERMS)
            elif choice < 0.7:
                cands = [i for i, t in enumerate(c["tags"]) if t in LIN2]
                i = r.choice(cands)
                fam = NL_FAM[c["tags"][i]]
                ab = r.choice([p for p in LIN_PAIRS if (fam, p) in FAM_TAGS])
                c["tags"][i] = FAM_TAGS[(fam, ab)]
            else:
                if c.get("mask", "none") == "none":
                    c["mask"] = r.choice([m for m in MASK_VALS if m != "none"])
        elif op == "guided_rounds_up":
            if n < 7:
                i = r.randrange(n - 1)
                c["tags"].insert(n - 1, c["tags"][i])
                c["rounds"] = n + 1
        elif op == "guided_finalmix":
            _set_final_tag(c, r.choice(["chi_fm07", "chi_fm11", "chi_fm311"]), r)
        else:
            return mutate(c, rng=r)
    except (IndexError, ValueError, KeyError):
        return mutate(c, rng=r)
    try:
        validate(c)
        return c
    except ValueError:
        return mutate(json.loads(json.dumps(g)), rng=r)


# ---------------------------------------------------------- state

def checkpoint_path():
    return os.path.join(STATE, "checkpoint.pkl")


def save_checkpoint(st):
    tmp = checkpoint_path() + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(st, f)
    os.replace(tmp, checkpoint_path())


def load_checkpoint():
    with open(checkpoint_path(), "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------- evaluation driver

def evaluate_individual(name, genome, st, archive_s, archive_q):
    """Full staged evaluation. Returns (point|None, annotation|None).

    point: (delay, cells, area) once S0 passes.
    annotation: failure record if the individual died statistically.
    Stage-A discard only if dominated by BOTH archives (a candidate that
    could extend Frontier Q survives even when S-dominated).
    """
    outdir = os.path.join(GA, "results", name)
    os.makedirs(outdir, exist_ok=True)

    def lf(m):
        log(f"  [{name}] {m}")

    # emit
    try:
        emit_candidate(name, genome)
    except Exception as e:
        lf(f"EMIT failed: {e}")
        return None, EV.annotate("emit", genome, {"error": str(e)})

    # model fingerprint (dedupe was done pre-emit; recompute for the record)
    # build + xcheck
    if not EV.build(name, lf):
        return None, EV.annotate("build", genome, {"error": "gcc failed"})
    if not EV.xcheck(name, outdir, lf):
        return None, EV.annotate("xcheck", genome,
                                 {"error": "C-vs-Python mismatch"})

    # Stage A: S0
    pt = EV.stage_A(name, outdir, lf)
    if pt is None:
        return None, EV.annotate("S0", genome, {"error": "synth/bar fail"})
    # archive domination (Stage-A discard): only if dominated by BOTH
    s_dom = any(dominates(r["point"], pt) for r in archive_s.values())
    q_dom = any(dominates(r["point"], pt) for r in archive_q.values())
    if s_dom and q_dom:
        lf(f"Stage-A discard: dominated by both archives")
        return pt, EV.annotate("S0-dom", genome,
                               {"point": pt, "note": "dominated by archives"})

    # Stage B: S1
    s1 = EV.stage_B(name, outdir, lf)
    if s1 is None or s1.get("verdict") != "CAL_PASS":
        sig = {"error": "no s1 record"} if s1 is None else {
            "lin_rejected": s1.get("lin_rejected", []),
            "diff_rejected": s1.get("diff_rejected", []),
            "pb_rejected": s1.get("pb_rejected", []),
            "red_rejected": s1.get("red_rejected", []),
            "verdict": s1.get("verdict")}
        return pt, EV.annotate("S1", genome, sig)

    # Stage C: S2
    s2 = EV.stage_C(name, outdir, logfn=lf)
    if EV.s2_killed(s2):
        return pt, EV.annotate("S2", genome, {
            "verdict": s2.get("verdict"), "max_repeats": s2.get("max_repeats"),
            "max_z": s2.get("max_z"), "spikes": s2.get("spikes", [])})

    # Archive entry (provisional) -> Stage D if it entered either archive
    in_s, ev_s = (False, [])
    in_q, ev_q = (False, [])
    if not s_dom:
        in_s, ev_s = pareto_add(archive_s, name, pt, {
            "genome": copy.deepcopy(genome), "stage": "S2",
            "full_battery": False, "source": "ga"})
    if not q_dom:
        in_q, ev_q = pareto_add(archive_q, name, pt, {
            "genome": copy.deepcopy(genome), "stage": "S2",
            "full_battery": False, "source": "ga", "bic": None})
    if in_s:
        lf(f"ARCHIVE-S ENTER (provisional): {pt} evicted={ev_s}")
    if in_q:
        lf(f"ARCHIVE-Q ENTER (provisional): {pt} evicted={ev_q}")
    if not (in_s or in_q):
        lf(f"S2 survivor, dominated in both archives (no Stage D)")
        return pt, None

    dres = EV.stage_D(name, outdir, lf)
    if not dres["all_ok"]:
        for arch in (archive_s, archive_q):
            arch.pop(name, None)
        stage = next((s for s in ("s3", "s3b", "s4")
                      if not dres.get(s)), "Q1")
        sig = {"s3": dres.get("s3"), "s3b": dres.get("s3b"),
               "s4": dres.get("s4"),
               "sac_z5": (dres.get("q1") or {}).get("sac_z5"),
               "bic_maxcorr": (dres.get("q1") or {}).get("bic_maxcorr")}
        lf(f"ARCHIVE EVICT: Stage D failed at {stage}")
        return pt, EV.annotate(stage, genome, sig)
    bic = dres["q1"]["bic_maxcorr"]
    for arch, entered in ((archive_s, in_s), (archive_q, in_q)):
        if name in arch:
            arch[name]["full_battery"] = True
            arch[name]["stage"] = "S4+Q1"
            arch[name]["bic"] = bic
            arch[name]["sac_z5"] = dres["q1"]["sac_z5"]
    # Q membership requires the bic gate; evict from Q if it fails it
    if in_q and (bic is None or bic > 0.02):
        archive_q.pop(name, None)
        lf(f"ARCHIVE-Q EVICT: bic={bic} > 0.02")
        in_q = False
    if in_s or in_q:
        lf(f"ARCHIVE CONFIRMED: {pt} bic={bic:.5f} "
           f"S={'in' if in_s else 'out'} Q={'in' if in_q else 'out'}")
    # frontier candidacy flags (human verifies before PARETO.md)
    flags = []
    if in_s:
        flags.append("FRONTIER-S-CANDIDATE")
    if in_q:
        flags.append("FRONTIER-Q-CANDIDATE")
    if flags:
        lf("*** " + " ".join(flags) + f" {name} {pt} bic={bic:.5f} ***")
    return pt, None


# ---------------------------------------------------------- main loop

def fresh_state():
    archive_raw = mine_archive()
    archive_s, archive_q = {}, {}
    for name, rec in archive_raw.items():
        pt = (rec["delay"], rec["cells"], rec["area"])
        pareto_add(archive_s, name, pt, rec)
        if rec.get("bic") is not None and rec["bic"] <= 0.02:
            pareto_add(archive_q, name, pt, rec)
    # population: expressible seeds + hand-builts + random fill
    pop = []
    for name, rec in archive_raw.items():
        if rec["genome"] is not None:
            pop.append({"name": f"seed_{name}", "genome": rec["genome"],
                        "point": (rec["delay"], rec["cells"], rec["area"]),
                        "seed": True, "evaluated": True})
    for hb_name, g in HAND_BUILT.items():
        pop.append({"name": f"seed_{hb_name}", "genome": copy.deepcopy(g),
                    "point": None, "seed": True, "evaluated": False})
    r = random.Random(0x6A)
    while len(pop) < MU:
        pop.append({"name": f"seed_rnd{len(pop)}",
                    "genome": random_genome(r), "point": None, "seed": True,
                    "evaluated": False})
    pop = pop[:MU]
    return {
        "generation": 0,
        "population": pop,
        "archive": archive_s,      # Frontier S: Pareto on (delay,cells,area)
        "archive_q": archive_q,    # Frontier Q: Pareto on (delay,cells,area)
                                   # among bic<=0.02 members
        "fingerprints": set(),
        "failures": [],          # failure annotations (analytical loop)
        "assoc": {},             # (failure_mode, gene_sig) -> count
        "rng_state": r.getstate(),
        "t0": time.time(),
        "evals": 0,
        "deaths": 0,
    }


def model_fingerprint(genome):
    import numpy as np
    rng = np.random.default_rng(0xF1)
    V = rng.integers(0, 2 ** 64, size=64, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    out = decode_np(genome)(V, K).tobytes()
    return fingerprint(genome, out)


def offspring_name(st):
    st["evals"] += 1
    return f"ga_g{st['generation']:02d}_{st['evals']:03d}"


def tournament(pool, rank, dist, r, k=2):
    cands = r.sample(pool, k)
    cands.sort(key=lambda c: (rank[c["name"]], -dist[c["name"]]))
    return cands[0]


def update_assoc(st, annotation):
    """Failure-mode -> gene-pattern association counts."""
    stage = annotation["stage"]
    for gp in annotation["gene_pattern"]:
        key = (stage, gp)
        st["assoc"][key] = st["assoc"].get(key, 0) + 1


def run_generation(st):
    r = random.Random()
    r.setstate(st["rng_state"])
    pop = st["population"]
    archive_s = st["archive"]
    archive_q = st["archive_q"]

    items = [(c["name"], c["point"]) for c in pop]
    rank = nondomination_rank(items)
    dist = crowding(items, rank)

    children = []
    for _ in range(LAMBDA):
        p1 = tournament(pop, rank, dist, r)
        p2 = tournament(pop, rank, dist, r)
        if r.random() < GUIDED_FRAC and st["failures"]:
            # guided: pick a recent death and apply its targeted fix
            ann = r.choice(st["failures"][-25:])
            parent_genome = ann.get("genome") or p1["genome"]
            child = guided_mutate(parent_genome, ann, r)
            maker = f"guided({ann['stage']}:{ann['suggested_fix']})"
        elif r.random() < 0.5:
            child = crossover(p1["genome"], p2["genome"], r)
            maker = "crossover"
        else:
            child = mutate(r.choice([p1, p2])["genome"], rng=r)
            maker = "mutate"
        # dedupe by model equivalence
        try:
            fp = model_fingerprint(child)
        except Exception:
            continue
        if fp in st["fingerprints"]:
            continue
        st["fingerprints"].add(fp)
        children.append((child, maker))

    for child, maker in children:
        name = offspring_name(st)
        log(f"gen {st['generation']}: evaluating {name} via {maker} "
            f"{canonical(child)[:120]}...")
        pt, annotation = evaluate_individual(name, child, st, archive_s,
                                             archive_q)
        ind = {"name": name, "genome": child, "point": pt, "seed": False,
               "evaluated": True}
        pop.append(ind)
        if annotation is not None and annotation["stage"] not in (
                "emit", "build", "xcheck", "S0", "S0-dom"):
            annotation["genome"] = copy.deepcopy(child)
            annotation["name"] = name
            st["failures"].append(annotation)
            st["deaths"] += 1
            update_assoc(st, annotation)
            log(f"  death @{annotation['stage']}: {annotation['hypothesis'][:150]}")
        save_checkpoint(st)

    # (μ+λ) truncation
    items = [(c["name"], c["point"]) for c in pop]
    rank = nondomination_rank(items)
    dist = crowding(items, rank)
    pop.sort(key=lambda c: (rank[c["name"]], -dist[c["name"]]))
    st["population"] = pop[:MU]
    st["rng_state"] = r.getstate()
    st["generation"] += 1

    # generation summary
    log(f"--- gen {st['generation']} done: pop={len(st['population'])} "
        f"archiveS={len(archive_s)} archiveQ={len(archive_q)} "
        f"evals={st['evals']} deaths={st['deaths']}")
    for aname, rec in sorted(archive_s.items(),
                             key=lambda kv: kv[1]["point"][0])[:6]:
        log(f"    archS {rec['point'][0]:.1f}u {rec['point'][1]}c "
            f"{rec['point'][2]}a bic={rec.get('bic')} [{aname}]")
    for aname, rec in sorted(archive_q.items(),
                             key=lambda kv: kv[1]["point"][0])[:6]:
        log(f"    archQ {rec['point'][0]:.1f}u {rec['point'][1]}c "
            f"{rec['point'][2]}a bic={rec.get('bic')} [{aname}]")
    # association table snapshot (top entries)
    top = sorted(st["assoc"].items(), key=lambda kv: -kv[1])[:6]
    for (stage, gp), cnt in top:
        log(f"    assoc [{stage}] {gp}: x{cnt}")
    save_checkpoint(st)


def initial_sweep(st):
    """Evaluate every gen-0 population member not yet evaluated
    (hand-builts + random fills) through the full staged pipeline.
    Idempotent: skips members already evaluated."""
    for c in st["population"]:
        if c.get("evaluated"):
            continue
        log(f"gen 0: evaluating seed {c['name']} "
            f"{canonical(c['genome'])[:120]}...")
        pt, annotation = evaluate_individual(c["name"], c["genome"], st,
                                             st["archive"], st["archive_q"])
        c["point"] = pt
        c["evaluated"] = True
        if annotation is not None and annotation["stage"] not in (
                "emit", "build", "xcheck", "S0", "S0-dom"):
            annotation["genome"] = copy.deepcopy(c["genome"])
            annotation["name"] = c["name"]
            st["failures"].append(annotation)
            st["deaths"] += 1
            update_assoc(st, annotation)
            log(f"  death @{annotation['stage']}: {annotation['hypothesis'][:150]}")
        try:
            st["fingerprints"].add(model_fingerprint(c["genome"]))
        except Exception:
            pass
        save_checkpoint(st)


def main():
    resume = "--resume" in sys.argv
    if resume and os.path.exists(os.path.join(STATE, "checkpoint.pkl")):
        st = load_checkpoint()
        # migrate pre-dual-archive checkpoints: rebuild archive_q from the
        # FULL mined seed set (the S archive alone lost the bic<=0.02 seeds
        # to 3-axis domination)
        if not st.get("archive_q"):
            from seed import mine_archive as _mine
            st["archive_q"] = {}
            for name, rec in _mine().items():
                if rec.get("bic") is not None and rec["bic"] <= 0.02:
                    pareto_add(st["archive_q"], name,
                               (rec["delay"], rec["cells"], rec["area"]), rec)
            log(f"migrated checkpoint: rebuilt archive_q "
                f"({len(st['archive_q'])} members) from mined seeds")
        log(f"resumed at gen {st['generation']} evals={st['evals']} "
            f"archiveS={len(st['archive'])} archiveQ={len(st['archive_q'])}")
        for c in st["population"]:
            c.setdefault("evaluated", c.get("point") is not None)
        initial_sweep(st)  # pick up any unevaluated members (idempotent)
        save_checkpoint(st)
    else:
        st = fresh_state()
        log(f"GA start: pop={len(st['population'])} "
            f"archiveS={len(st['archive'])} archiveQ={len(st['archive_q'])} "
            f"(seed-parsed, no re-synthesis)")
        save_checkpoint(st)
        initial_sweep(st)
        save_checkpoint(st)

    while True:
        if os.path.exists(os.path.join(STATE, "STOP")):
            log("STOP file present — exiting cleanly")
            break
        if time.time() - st["t0"] > WALL_BUDGET_S:
            log("48h wall budget exhausted — exiting")
            break
        try:
            run_generation(st)
        except Exception as e:
            log(f"generation {st['generation']} crashed: {e!r} — checkpoint kept")
            import traceback
            log(traceback.format_exc()[-2000:])
            time.sleep(60)


if __name__ == "__main__":
    if not os.path.exists(LOG):
        with open(LOG, "w") as f:
            f.write("# GA log — analytical failure analysis + evolution\n\n")
            f.write("Append-only. Frontier-candidacy flags are NOT PARETO.md "
                    "edits; the human coordinator verifies from raw logs.\n\n")
    main()
