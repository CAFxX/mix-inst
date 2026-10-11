#!/usr/bin/env python3
"""D11 fast screen: Hypothesis D11 (batch 14) — the two untested D11 axes.

Axis 1: shift+shift 2-term LIN class. LIN(z) = z ^ (z<<a) ^ (z<<b) /
  z ^ (z>>a) ^ (z>>b) / z ^ (z<<a) ^ (z>>b) on the D9-established S1-viable
  vehicle: 4r SCSC, Midori Sb0, CHI_A AND-chi, pba19, golden KS, full LIN
  on ALL rounds. D10 covered rot+shift (35/35 bijective screen-clean,
  cost-neutral vs floor); shift+shift is untested.
  Screen: bijectivity pre-filter (GF(2) rank of the 64x64 LIN map) ->
  D-screen on bijective ones -> keep bijective + D<50 multi-key.

Axis 2: SSSS Midori with co-designed WIDER rotation pairs (D10: (5,13) clean,
  (13,27) clean, (7,19) borderline, (1,2) dead). Try (13,37),(19,43),
  (27,37),(5,37),(7,43),(13,43) — same XOR count as D10 pairs, so cost
  floor identical; the question is diffusion quality at the borderline.
  Plus D10's best axis-1 terms (rot+shift) transplanted onto SSSS:
  lin=[("rotl",5),("shl",6)] (D=11 on SCSC) and [("rotl",13),("shr",6)]
  (D=12 on SCSC) — genuinely untested dynamics.

Committed positive control: DIAG_scsc_rasc20_513_all must reproduce D9's
  exact D0=20 before ANY new result is trusted (process rule from D9/D8).
"""
import os
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/directed_design")
import d10_screen as d10

DD = "/home/hatch/workspace/mix/exploration/directed_design"
CONTROL_D0 = 20  # D9 d9_screen.txt DIAG_scsc_rasc20_513_all exact value


def main():
    N = 4096 * 64
    V = d10.np.arange(N, dtype=d10.np.uint64)
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]
    outp = os.path.join(DD, "results", "d11_screen.txt")
    # resume support: never delete a results file that already holds
    # completed candidates — skip tags already present.
    done_tags = set()
    if os.path.exists(outp):
        with open(outp) as f:
            for line in f:
                if line.startswith(("AX1 ", "AX2 ")):
                    done_tags.add(line.split()[1])
        if done_tags:
            print(f"RESUME: skipping {len(done_tags)} completed candidates",
                  flush=True)

    def emit(ax, tag, d0, logp, dm, dp0, dp1, t):
        with open(outp, "a") as f:
            f.write(f"{ax} {tag} D0={d0} logp={logp:.1f} Dmulti={dm} "
                    f"dprobe0={dp0} dprobe1={dp1} t={t:.1f}s\n")
        print(f"{tag:34s} {d0:6d} {logp:6.1f} {dm:>22s} "
              f"{dp0:>8s} {dp1:>8s} {t:5.1f}s", flush=True)

    # ---- committed positive control (must reproduce D9 exactly) ----
    # on resume the control already passed; re-run only for a fresh file.
    with open(outp) as f:
        ctl_ok = any(l.startswith("CONTROL ") for l in f)
    if not ctl_ok:
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
        print("CONTROL OK — proceeding with D11 screens", flush=True)
    else:
        print("RESUME: committed control already passed on prior run", flush=True)

    # ---- Axis 1: shift+shift 2-term LIN enumeration ----
    print("=== Axis 1: shift+shift bijectivity pre-filter ===", flush=True)
    SHIFTS = [1, 2, 3, 4, 5, 6, 7]
    DIR_PAIRS = [("shl", "shl"), ("shr", "shr"), ("shl", "shr")]
    ax1_bij = []
    ax1_dead = []
    for a in SHIFTS:
        for b in SHIFTS:
            if a == b:
                continue
            for d1, d2 in DIR_PAIRS:
                terms = [(d1, a), (d2, b)]
                rk = d10.lin_rank(terms)
                if rk == 64:
                    ax1_bij.append((a, b, d1, d2))
                else:
                    ax1_dead.append((a, b, d1, d2, rk))
    total = len(SHIFTS) * (len(SHIFTS) - 1) * len(DIR_PAIRS)
    print(f"bijective: {len(ax1_bij)}/{total}", flush=True)
    with open(outp, "a") as f:
        f.write(f"# axis-1 bijectivity: {len(ax1_bij)}/{total} bijective\n")
        for a, b, d1, d2, rk in ax1_dead:
            f.write(f"# NOT bijective: {d1}{a}+{d2}{b} rank={rk}\n")
        for a, b, d1, d2 in ax1_bij:
            f.write(f"# bijective: {d1}{a}+{d2}{b}\n")
    for a, b, d1, d2, rk in ax1_dead:
        print(f"  NOT bijective: {d1}{a}+{d2}{b} rank={rk}", flush=True)

    print(f"{'candidate':34s} {'D0':>6s} {'logp':>6s} "
          f"{'Dmulti':>22s} {'dprobe0':>8s} {'dprobe1':>8s} {'t':>5s}",
          flush=True)
    for a, b, d1, d2 in ax1_bij:
        tag = f"ax1_ss_scsc_midori_{d1}{a}_{d2}{b}"
        if tag in done_tags:
            continue
        spec = d10.mk_spec(tag, "SCSC", d10.SBOX_M, d10.CHI_A, "and",
                           lin_terms=[(d1, a), (d2, b)], lin_mode="all",
                           desc=f"D11 axis-1: LIN=x^{d1}(x,{a})^{d2}(x,{b})")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("AX1", tag, d0, logp, dm, dp0, dp1, t)

    # ---- Axis 2: wider SSSS pairs + axis-1 best terms on SSSS ----
    print("=== Axis 2: wider SSSS pairs + transplanted rot+shift terms ===",
          flush=True)
    ax2_pairs = [(13, 37), (19, 43), (27, 37), (5, 37), (7, 43), (13, 43)]
    for a, b in ax2_pairs:
        tag = f"ax2_ssss_midori_{a}{b}"
        if tag in done_tags:
            continue
        spec = d10.mk_spec(tag, "SSSS", d10.SBOX_M, d10.CHI_A, "and",
                           rots=[a, b], lin_mode="all",
                           desc=f"D11 axis-2: SSSS pure-S-box, LIN({a},{b})")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("AX2", tag, d0, logp, dm, dp0, dp1, t)
    for tag, terms in [
        ("ax2_ssss_midori_r5_shl6", [("rotl", 5), ("shl", 6)]),
        ("ax2_ssss_midori_r13_shr6", [("rotl", 13), ("shr", 6)]),
    ]:
        if tag in done_tags:
            continue
        spec = d10.mk_spec(tag, "SSSS", d10.SBOX_M, d10.CHI_A, "and",
                           lin_terms=terms, lin_mode="all",
                           desc=f"D11 axis-2: SSSS with transplanted {terms}")
        d0, logp, dm, dp0, dp1, t = d10.screen_one(spec, V, keys)
        emit("AX2", tag, d0, logp, dm, dp0, dp1, t)

    print("wrote results/d11_screen.txt (incremental)")


if __name__ == "__main__":
    main()
