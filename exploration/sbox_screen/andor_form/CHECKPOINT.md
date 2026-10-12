# track2-andor-form CHECKPOINT

**Lane:** ANDOR form WITH LINEAR BYPASS TAP (O141 re-test trigger)
**Dir:** `~/workspace/mix/exploration/sbox_screen/andor_form/`
**Seed:** 0xB805 · **Workreg:** track2-andor-form · **Tag:** track2/andor-form
**Status 2026-10-12 ~13:55 CEST:** TERMINAL — VERDICT O144 RECORDED.
Pilot COMPLETE 0/36 KEEP (11:28:32Z, raw-adjudicated from pilot.log:
inner_kills=36 fisher_kills=0). K1 fired: form change KILLED at the
primary gate. O144 row in VERDICT_SCOPE.md (O-number claimed at write
time: ledger top O143, O142 reserved for batch-62 S0). Mechanism:
bypass tap does NOT fix the ceiling (B/H3 4.4k ≈ old-form H3 7.0k);
uniformity+nonlinearity axis moves the needle (Y/H3 bent 306 vs B/H3
4396, ~14x) but stays inner-FLAG'd 0/36; H3 >> H1 every family.
Re-test trigger (narrow): co-designed change addressing Y's residual
inner-DIFF-SEQ FLAG signature, never more Y draws; or a stronger
per-bit nonlinear function class. No 4-gate bar (no keeps). No GHA.
LEADS_LEDGER.md updated (lead closed). Workreg track2-andor-form → done.
Lane closed; no further action.

## Completed
1. DESIGN.md pre-registered (220 lines): families B (ANDORB = x^f^x_e, f
   verbatim), X (ANDORX = x^g2^x_e, g2 = f^NOR4 balanced wt8 NL4 uniform
   1/2), Y (ANDORY = x^g4^x_e, g4 = (p&q)^(r&s)^p bent NL6 max|W|4).
   L = x_{i+e}, e distinct fifth tap — justified vs L=x_i (vacuous) and
   L=x_{i+a} (no spread widening). Falsifiable theses: >=1 B/H3
   inner-PASS; B/H3 maxworst|z| < 1000 (old-form H3 best 7.0k).
2. t8_andor_form_screen.py: selftest PASS (3x50 bit-exact vs scalar,
   500/500 draw gates, H1/H3 shape, inner smoke).
3. Calibration ALL PASS: CALIB-1 (z=3.3 exact), 2a (MU5-324 keep),
   2b (linear-4 reject), 5a (t6_b59_47 inner PASS), 6 (O131-verbatim draw
   inner-REJECT), 7 (draw gates), 8 (avalanche: old 2.50 / B 3.50 /
   X 4.00 / Y 4.00 / MUXD 3.50 + B bypass determinism exact),
   9 (truth tables: f wt7 NL5, g2 wt8 NL4, g4 wt6 NL6).
4. Sign fix (2026-10-12): rotl(x,e)[i] = x[(i-e) mod 64] so the bypass
   flips output bit j+e, not j-e — CALIB-8 caught it (det=False),
   fixed in harness + DESIGN.md. Mechanism unaffected.

## Next
- run_pilot.sh (cleared-flag backoff wrapper) -> workreg register ->
  setsid agentwork-launch.sh --nice 19 --tag track2/andor-form ->
  36-draw pilot -> pilot.log, pilot_keeps.jsonl, heartbeat.txt.
- On keeps >= 1: 4-gate bar (gate4 precedent). On 0/36: terminal
  O-verdict (claim O-number at write time from ledger top = O141).

## How to resume after VM death
- If pilot.log exists and shows "KEEP (inner_kills=...)" terminal line:
  adjudicate from raw log (never from drafts).
- If pilot died mid-run: re-run run_pilot.sh (backoff-gated); the pilot
  is deterministic per seed but NOT checkpointed per-draw — a re-run
  restarts from draw 0. (Draws are cheap: ~36 x (inner+fisher).)
- workreg: `workreg.py heartbeat --id track2-andor-form` while alive;
  `workreg.py done --id track2-andor-form` at terminal verdict.
