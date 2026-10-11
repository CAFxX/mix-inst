#!/usr/bin/env python3
"""D12 fast screen: Hypothesis D12 (batch 15) — FEWER, STRONGER ROUNDS.

D12 decision (2026-10-10, track-4 supervisor incarnation G): the 4-round
directed family has CONVERGED — D10 and D11 both bottomed at ~27.0-27.1u,
and the improvements went into DIFF-quality understanding (shl-only LIN
structurally dead, narrow-wide SSSS balance, transplant failures), not
delay. The cost driver is structural: 4 S-box rounds on the critical
path, and no within-round LIN choice removes it. dd14's best 4r LIN rep
(shl2_shr6, 27.7u) is S2-clean but dominated; both wider-SSSS reps were
S1-FLAG killed (screen-fidelity gap on the SSSS axis, now ledgered).

D12 widens instead of stopping: attack the structural cost driver with
a 3-round SCSC vehicle (pattern "SCS"), keeping everything else from the
D11 vehicle (Midori Sb0, CHI_A AND-chi, pba19, golden KS, full LIN on ALL
rounds). At ~3/4 of the 4r cost this projects to ~20.3u — at the
frontier. The open question is purely diffusion quality: the screen + S1
will answer it. NOTE: D10 killed 3r only on the pure-S-box SSSS template
(D=4096) — that verdict is SCOPED to SSSS, not carried to SCSC.

Co-design, not transplant: every LIN class that was clean on 4r is
RE-SCREENED on the 3r vehicle (rot+shift, shr+shr, shl+shr). The shl+shl
class is EXCLUDED from the search (D11: 34/34 structurally DIFF-dead on
4r SCSC with a mechanism conjecture) but 6 shl+shl combos run as NEGATIVE
CONTROLS on the 3r vehicle — if any comes back clean, the mechanism is
falsified and the class re-opens.

Positive control: the 4r DIAG_scsc_rasc20_513_all must reproduce D9's
exact D0=20 before ANY new result is trusted (machinery validation —
there is no historical 3r control; stated honestly, not faked).
"""
import os
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/directed_design")
import d10_screen as d10

DD = "/home/hatch/workspace/mix/exploration/directed_design"
CONTROL_D0 = 20  # D9 d9_screen.txt DIAG_scsc_rasc20_513_all exact value
PATTERN_3R = "SCS"


def main():
    N = 4096 * 64
    V = d10.np.arange(N, dtype=d10.np.uint64)
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]
    outp = os.path.join(DD, "results", "d12_screen.txt")
    # resume support: skip tags already present.
    done_tags = set()
    if os.path.exists(outp):
        with open(outp) as f:
            for line in f:
                if line.startswith(("AXA ", "AXB ", "AXC ", "NEG ")):
                    done_tags.add(line.split()[1])
        if done_tags:
            print(f"RESUME: skipping {len(done_tags)} completed candidates",
                  flush=True)

    def emit(ax, tag, d0, logp, dm, dp0, dp1, t):
        with open(outp, "a") as f:
            f.write(f"{ax} {tag} D0={d0} logp={logp:.1f} Dmulti={dm} "
                    f"dprobe0={dp0} dprobe1={dp1} t={t:.1f}s\n")
        print(f"{tag:36s} {d0:6d} {logp:6.1f} {dm:>22s} "
              f"{dp0:>8s} {dp1:>8s} {t:5.1f}s", flush=True)

    # ---- committed positive control: 4r DIAG, machinery validation ----
    ctl_seen = False
    if os.path.exists(outp):
        with open(outp) as f:
            ctl_seen = any(l.startswith("CONTROL ") for l in f)
    if not ctl_seen:
        ctl = d10.mk_spec("DIAG_scsc_rasc20_513_all", "SCSC", d10.SBOX_R,
                          d10.CHI_A, "and", rots=[5, 13], lin_mode="all")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(ctl, V, keys)
        print(f"CONTROL {ctl['name']}: D0={d0} (expect {CONTROL_D0})",
              flush=True)
        if d0 != CONTROL_D0:
            print(f"FATAL: positive control FAILED (D0={d0} != {CONTROL_D0}); "
                  f"screen untrustworthy, aborting.", flush=True)
            sys.exit(2)
        emit("CONTROL", ctl["name"], d0, logp, dm, dp0, dp1, t)
        print("CONTROL OK — machinery valid; proceeding with D12 3r screens",
              flush=True)
    else:
        print("RESUME: committed control already passed on prior run",
              flush=True)

    def scs(tag, terms, desc):
        return d10.mk_spec(tag, PATTERN_3R, d10.SBOX_M, d10.CHI_A, "and",
                           lin_terms=terms, lin_mode="all", desc=desc)

    def prefilter(combos):
        bij, dead = [], []
        for terms in combos:
            if d10.lin_rank(terms) == 64:
                bij.append(terms)
            else:
                dead.append(terms)
        return bij, dead

    print(f"{'candidate':36s} {'D0':>6s} {'logp':>6s} "
          f"{'Dmulti':>22s} {'dprobe0':>8s} {'dprobe1':>8s} {'t':>5s}",
          flush=True)

    # ---- Axis A: rot+shift 2-term LIN (D10's 98-combo set, re-screened) --
    print("=== Axis A: rot+shift 2-term LIN on 3r SCSC ===", flush=True)
    axa = [[("rotl", a), (d_, b)]
           for a in [1, 2, 5, 7, 13, 19, 27]
           for b in [1, 2, 3, 4, 5, 6, 7]
           for d_ in ["shl", "shr"]]
    axa_bij, axa_dead = prefilter(axa)
    print(f"bijective: {len(axa_bij)}/{len(axa)}", flush=True)
    with open(outp, "a") as f:
        f.write(f"# axis-A bijectivity: {len(axa_bij)}/{len(axa)} bijective\n")
        for t_ in axa_dead:
            f.write(f"# NOT bijective: {t_}\n")
    for terms in axa_bij:
        (k1, a), (k2, b) = terms
        tag = f"d12a_scs_midori_r{a}_{k2}{b}"
        if tag in done_tags:
            continue
        spec = scs(tag, terms,
                   f"D12 axis-A: 3r SCSC, LIN=x^rotl(x,{a})^({k2}{b})")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("AXA", tag, d0, logp, dm, dp0, dp1, t)

    # ---- Axis B: shr+shr 2-term LIN ----
    print("=== Axis B: shr+shr 2-term LIN on 3r SCSC ===", flush=True)
    SH = [1, 2, 3, 4, 5, 6, 7]
    axb = [[("shr", a), ("shr", b)] for a in SH for b in SH if a != b]
    axb_bij, axb_dead = prefilter(axb)
    print(f"bijective: {len(axb_bij)}/{len(axb)}", flush=True)
    with open(outp, "a") as f:
        f.write(f"# axis-B bijectivity: {len(axb_bij)}/{len(axb)} bijective\n")
        for t_ in axb_dead:
            f.write(f"# NOT bijective: {t_}\n")
    for terms in axb_bij:
        (_, a), (_, b) = terms
        tag = f"d12b_scs_midori_shr{a}_shr{b}"
        if tag in done_tags:
            continue
        spec = scs(tag, terms,
                   f"D12 axis-B: 3r SCSC, LIN=x^(x>>{a})^(x>>{b})")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("AXB", tag, d0, logp, dm, dp0, dp1, t)

    # ---- Axis C: shl+shr 2-term LIN ----
    print("=== Axis C: shl+shr 2-term LIN on 3r SCSC ===", flush=True)
    axc = [[("shl", a), ("shr", b)] for a in SH for b in SH if a != b]
    axc_bij, axc_dead = prefilter(axc)
    print(f"bijective: {len(axc_bij)}/{len(axc)}", flush=True)
    with open(outp, "a") as f:
        f.write(f"# axis-C bijectivity: {len(axc_bij)}/{len(axc)} bijective\n")
        for t_ in axc_dead:
            f.write(f"# NOT bijective: {t_}\n")
    for terms in axc_bij:
        (_, a), (_, b) = terms
        tag = f"d12c_scs_midori_shl{a}_shr{b}"
        if tag in done_tags:
            continue
        spec = scs(tag, terms,
                   f"D12 axis-C: 3r SCSC, LIN=x^(x<<{a})^(x>>{b})")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("AXC", tag, d0, logp, dm, dp0, dp1, t)

    # ---- Negative controls: shl+shl (expect DIFF-death per D11) ----
    print("=== Negative controls: shl+shl on 3r SCSC (expect DIFF-death) ===",
          flush=True)
    for a, b in [(1, 2), (1, 6), (2, 5), (3, 7), (4, 6), (5, 7)]:
        terms = [("shl", a), ("shl", b)]
        assert d10.lin_rank(terms) == 64, f"neg control {a},{b} not bijective"
        tag = f"d12neg_scs_midori_shl{a}_shl{b}"
        if tag in done_tags:
            continue
        spec = scs(tag, terms,
                   f"D12 NEG: 3r SCSC shl+shl — expect DIFF-death (D11 rule)")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("NEG", tag, d0, logp, dm, dp0, dp1, t)

    print("wrote results/d12_screen.txt (incremental)")


if __name__ == "__main__":
    main()
