# Track-2 SBOX8 hand-optimization lane — status

**Workreg:** `track2-sbox8-handopt` (active) · **Dir:** `sbox_screen/handopt/`
**Goal:** composite-field hand-optimized circuits for top-5 AFF8 boxes
(AFF8_06/03/00/12/02), then 8-bit SPN bundler (2R/3R), S0 < 18.6u,
XCHECK, S1→S4 battery, Q1. Pre-registered fallback: COST-CLOSED with O-number.

## 2026-10-12 ~09:45 CEST — setup + affine recovery (DONE)
- Workreg entry `track2-sbox8-handopt` registered; heartbeat active.
- Fetched `gen_sbox8_pool.py` from CAFxX/fanout (public, read-only) →
  `gen_sbox8_pool_ref.py` (kept for provenance).
- `recover_affine.py`: replayed the seeded RNG (0x5B08); recovered
  (m1,c1,m2,c2) for all 16 AFF8 boxes; replayed tables match the GHA
  harvest `ranked_sbox8_pool_20261012.json` **16/16 byte-identical**.
  → `affine_maps.json`.
- `comp8.py`: composite-field S-box generator.
  - GF(2^4) = GF(2)[w]/(w^4+w+1); GF(2^8) = GF(2^4)[t]/(t^2+t+lam).
  - Isomorphism delta found computationally (minpoly search); the
    relation delta(a.b)==cmul(delta(a),delta(b)) is verified over all
    65536 pairs per (lam,beta).
  - Pool affines FUSED with delta/delta^-1 into single 8x8 pre/post maps.
  - **Correction logged:** 0x11B is irreducible but NOT primitive
    (roots have order 51, not 255) — an order-255 pre-filter in the
    isomorphism search was wrong; minpoly test alone is exact.
  - Model check: emitted circuit == harvest table 256/256 AND ==
    pool definition 256/256 (independent re-evaluation).

## Next
1. `comp8.py search` → pick (lam, beta) minimizing affine XOR depth.
2. Emit composite inversion cores per lam; S0 via pinned run_synth.py;
   pick best core.
3. Emit top-5 full boxes; iverilog testbench check (true RTL, 256/256);
   S0 each; target well under 8u/box.
4. 8-bit SPN bundler (2R/3R, keyed, §5 chassis); S0 < 18.6u bar.
5. S0-eligible → XCHECK (10k) → fast_battery S1→S4 → Q1 (sac_z5=0).
6. Verdict → PARETO or COST-CLOSED (O-number in VERDICT_SCOPE.md).

## 2026-10-12 ~10:15 CEST — TERMINAL VERDICT: O129 COST-CLOSED
- Composite-field: **core 23.0u, full AFF8_06 box 25.1u** (pinned flow;
  iverilog 256/256 vs harvest). Tower's sequential mul4→inv4→mul4 is
  XOR-deep under XOR2=2.0u. 9x smaller than case form, 2.4x slower.
- Controls (pinned flow): AFF8_06 case **10.7u**; pure inversion **10.4u**.
  ABC's crit path = 9 fast gates, zero XOR2 on-path.
- **O129**: per-box floor ~10.4u → 2-round SPN ≥ 20.8u > 18.6u bar.
  8-bit SPN line COST-CLOSED (pre-registered honest negative).
  Bundler not built (lower bound decides S0).
- Open lead → hybrid track: 8-bit box as single hetero stage (no owner).
- Ledger + VERDICT_SCOPE.md updated. Workreg → done.

## Numbers (final)
| circuit | crit | cells | note |
|---|---|---|---|
| AFF8_06 case form (GHA) | 10.4u | ~4000 | screen baseline |
| AFF8_06 case form (local pinned) | 10.7u | 499 | reproduced |
| pure GF inv8 case form | 10.4u | 479 | nonlinear core floor |
| composite core v1 (behavioral) | 23.0u | 393 | lam=0x8 |
| composite AFF8_06 v2 (AND/XOR) | 25.1u | 457 | lam=0xc, 58 AND + 129 XOR |
