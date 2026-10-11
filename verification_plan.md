# Verification & Sky130 Place-and-Route Plan

## 1. What has been measured (this environment)

| Check | Method | Result |
|---|---|---|
| Bit-accuracy RTL vs Python model | Icarus Verilog, 3007 golden vectors (10 rd) + 500 (8 rd) | 100% match |
| Mapped-netlist vs Python model | Icarus + functional cell models, 300 random vectors | 300/300 match |
| Bijectivity per fixed key | Exhaustive on structurally identical 16-bit instance, 7 keys | 65536/65536 distinct each |
| Relative delay/area | Yosys 0.33 + ABC (`-fast`: strash, dretime, map) to unit-delay `mini.genlib`; critical path by longest-path analysis on mapped netlist | see §2 |
| Statistical quality | SAC/BIC/uniformity/sequence batteries vs SplitMix64, Murmur3 fmix64 | see TEST_REPORT.md |

## 2. Relative synthesis results (unit-delay teaching library — ratios only)

| Design | Cells | Area (unit) | Crit. path (unit) | vs mul64 delay | vs mul64 area |
|---|---|---|---|---|---|
| `mix` 10-round | 7614 | 23685 | 62.0 | 1.26× | 0.53× |
| `mix` 8-round | 6093 | 18965 | 50.4 | **1.02×** | 0.43× |
| 64×64 multiplier (Yosys `$mul`) | 17115 | 44548 | 49.2 | 1.00× | 1.00× |
| 64-bit Kogge-Stone adder (hand RTL) | 1407 | 3650 | 12.0 | 0.24× | 0.08× |
| 64-bit adder (Yosys `$add` → carry-lookahead techmap, not a ripple-carry) | 428 | 1253 | 19.0 | 0.39× | 0.03× |

Notes and caveats:
- Absolute numbers are meaningless (teaching library); only ratios are reported.
- ABC's default script (`dch` restructuring) was found to corrupt delay on
  prefix structures (KS adder measured 73.1 instead of 12.0); the `-fast`
  script preserves structure. Both flows agree on `mix` (61.8 vs 62.0),
  indicating a robust measurement.
- Yosys's `$mul`/`$add` are reference implementations, not production
  Booth/Wallace multipliers; a hand-optimized multiplier could be ~20%
  faster, which would move the 10-round ratio to ~1.5–1.6× (1.26/0.8). The Sky130 P&R
  comparison should use the best available multiplier, not just Yosys's.
- The "adder latency" requirement: a fast 64-bit adder (12.0) is ~4–5×
  faster than any adequate 64-bit mixer; the two timing requirements as
  literally stated are mutually exclusive. The multiplier requirement is
  the achievable one (see final report §"requirement reconciliation").

## 3. Sky130 P&R plan (not yet executed — no PDK in this environment)

1. Install SkyWater 130 PDK (`skywater-pdk`) + OpenLane2/OpenROAD flow.
2. Synthesize three designs with identical constraints/SDC:
   - `mix_spn10` (ROUNDS=10, the candidate; ROUNDS=8 was rejected on
     statistical grounds — see isa_spec.md §5),
   - best available 64×64 multiplier (Booth/Wallace, not Yosys `$mul`),
   - 64-bit Kogge-Stone adder (reference).
   Each wrapped identically (registered inputs/outputs or pure
   combinational with `set_max_delay`; same drive/load).
3. Run full OpenROAD flow: synthesis → floorplan → placement → CTS →
   routing; then OpenSTA timing.
4. Report, for each design: post-route worst negative slack / max
   combinational delay, cell area, wire length, power (vectorless).
5. Acceptance: `mix` post-route delay ≤ 1.1× multiplier post-route delay
   (margin for flow noise); area ≤ 1× multiplier. NOTE: relative mapping
   measures 1.26× — this criterion is already failed on paper with no
   remediation path stated. If P&R confirms ≈1.26×, disposition against the
   user's 1–2× envelope (within it, though above the nominal 1.0×
   'equivalent' target). If ≤1.1× is a hard gate, S-box delay
   re-optimization (item 6) is required first.
6. If `mix` misses timing: first try S-box re-optimization for delay
   (current equations minimize literals, not depth); do not silently cut
   rounds without re-running the statistical battery.

## 4. Statistical acceptance (already run — see test report)

- SAC mean |dev| ≤ 0.01, max |dev| ≤ 0.035 (value and key bits).
- BIC max |corr| ≤ 0.10.
- Sequential-input low-`m` chi-square |z| ≤ 4 for m ≤ 14.
- Sequence battery (raw/Lemire/mask/mod-y) on adversarial configs:
  zero *unexplained* flags at |z| > 4 (one 4.5σ flag investigated: not
  reproduced at 16× sample size, neighboring configs clean — classified
  as statistical fluctuation; see TEST_REPORT.md), and no worse than
  SplitMix64/Murmur3-fmix64 under identical conditions.

## 5. Outstanding verification

- [ ] Sky130 P&R (blocked on PDK/flow availability)
- [ ] Dieharder/PractRand on long streams (PractRand not installed here)
- [x] Independent peer review (4 reviews completed 2026-10-01: RTL, statistical
      methodology, cryptanalytic soundness, synthesis/ISA honesty — see
      `reviews/`; findings remediated below)
- [ ] Related-key differential spot-checks — re-scoped: the key schedule
      provides *no related-key resistance by design* (round constants cancel
      under seed differences: Δrk[i] = ROTL(Δkey, 13·(i+1))); acceptable because
      the seed is a public per-map value with no related-key oracle. Must never
      be used where related-key security is required.

## 6. Peer-review findings remediated (2026-10-01)

- RTL: no logic bugs; test-hygiene fixes applied — `tb_mix8.v` and
  `tb_golden.v` now FATAL on missing vector file (were vacuous passes) and
  print explicit PASS/FAIL verdicts; compiled sim binaries removed from tree.
- Stats methodology: exact null distributions (Lemire/mod preimage counts)
  independently verified correct by brute force on toy widths. Flag threshold
  now reported in p-values (|z|>4 is p≈0.01 at df=1, p≈6×10⁻⁵ at df=1023).
  Per-bit monobit screen added to the battery (`seq_battery` now returns a
  `perbit-max|z|` statistic); it found a small real transient bias in SPN-10
  bit 39 (δ≈0.002–0.004, key-dependent, sequential inputs only, washes out by
  N≈2²⁰; SplitMix64 shows the same phenomenon on bit 31) — disclosed in
  TEST_REPORT.md, no practical impact on the use case.
- Crypto: PRESENT S-box DDT/LAT verified (2⁻²/2⁻²); ≥20 active S-boxes over
  10 rounds ⇒ ≤2⁻⁴⁰ per-characteristic differential probability, ≤2⁻²⁰ linear
  correlation, key-independent. 14 of 55 round pairs admit exact-collision weak
  keys, but each class is 2–4 keys out of 2⁶⁴ (fraction ≤2⁻⁶²) — negligible.
- Synth/ISA: all six relative numbers reproduced exactly from archived
  netlists; `-fast` vs default flow discrepancy on the KS adder confirmed a
  genuine ABC `dch` behavior, fairly applied. isa_spec.md wording fixes
  applied (see F7–F9 items); "see test report" references repointed to
  TEST_REPORT.md.
