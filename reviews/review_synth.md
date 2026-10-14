# Peer Review: Synthesis Methodology & ISA-Spec Honesty

**Method:** read `mini.genlib`, [`analyze.py`](../synth/analyze.py), [`synth.ys`](../synth/synth.ys), [`synth_fast.ys`](../synth/synth_fast.ys) end to end; reproduced all six reported numbers from the archived netlists; built an independent alias-resolving longest-path analyzer (handles bit-ranges, selects, concatenations) and recomputed every critical path; traced critical paths gate-by-gate; functionally re-verified the three reported netlists with Icarus Verilog; reproduced the default-flow mix number (61.8) and the KS default-vs-fast discrepancy from the archived scripts; inspected Yosys's pre-ABC `$add` netlist; checked `yosys -h abc` for the `-fast` definition; web-searched custom-0 encoding conflicts.

## Verdicts

**Methodology: SOUND** for all reported numbers, with two latent (non-impacting) tool fragilities noted below.
**Plausibility: all six numbers verified** — delay, area, and ratios reproduce exactly; critical-path structures match first-principles expectations.
**Functional correctness of reported netlists: confirmed** — re-ran 300/300 (mix-10, the exact 62.0 netlist), 200/200 (KS adder), 200/200 (multiplier), 0 errors.
**ISA spec honesty: substantially honest**, with 3 wording fixes recommended. **[verification_plan.md](../verification_plan.md): 4 concrete errors** requiring fixes (one stale contradiction, two stale references, one mislabel).

## What I verified as correct

1. **Numbers reproduce exactly** from the archived netlists with [`analyze.py`](../synth/analyze.py): 62.0 / 50.4 / 49.2 / 19.0 / 73.1 / 12.0. Table arithmetic (1.26×, 0.53×, 1.02×, 0.43×, 0.24×, 0.08×) is correct.
2. **The `-fast` flow claim is real and fairly applied.** [`synth.ys`](../synth/synth.ys) vs [`synth_fast.ys`](../synth/synth_fast.ys) differ in exactly one line (`abc -genlib` → `abc -fast -genlib`). Yosys documents `-fast` as `strash; dretime; map` (no `dch`); the default script's `dch` area-restructuring destroying the KS prefix tree (73.1 vs 12.0, reproduced from archived scripts) is a known, genuine ABC behavior. All six designs used the identical `-fast` flow — apples-to-apples.
3. **"Both flows agree on mix (61.8 vs 62.0)"** — independently reproduced the default-flow 61.8. Robust.
4. **mix-10 netlist genuinely implements 10 rounds, unfolded.** Traced critical path: input-XOR(2.0) + 10×[XOR2(2.0) + S-box as NOR4→NAND3→NAND3 (1.4+1.2+1.2=3.8)] + output-XOR(2.0) = **62.0 exactly**, 42 gates. mix-8: 2.0+8×5.8+2.0 = 50.4 exactly. No constant-folding or truncation.
5. **Input→output dependency:** backwards reachability from outputs shows **zero orphan inputs** in all netlists — all 128 mix inputs affect outputs.
6. **KS adder 12.0** traces as NAND2(1.0) + 6×AOI21/OAI21(1.5) + XNOR2(2.0) = 12.0 — 6 prefix levels, plausible and functionally correct.
7. **No `$cells`, no non-genlib instances, no ZERO/ONE instances** in any netlist; no combinational loops.

## Latent tool issues in [`analyze.py`](../synth/analyze.py) (verified harmless here, should be hardened)

- It **silently ignores `assign` statements**. [`mapped_mix_spn10.v`](../synth/mapped_mix_spn10.v) has 42 (all dead `= 32'hxxxxxxxx` debug nets — confirmed unconsumed) and [`mapped_ks_fast.v`](../synth/mapped_ks_fast.v) has 15 **live aliases** (`g5[15:0] = carry[16:1]`, etc.). My full alias-resolving reimplementation gives **identical** critical paths for all six netlists, with zero consumed-but-undriven nets — so no reported number is corrupted. But on a netlist with assigns on the critical path, [`analyze.py`](../synth/analyze.py) would silently under-report. Recommend fixing the tool or documenting the assumption.
- Unknown cell types default to delay 1.0 (`delay.get(..., 1.0)`); never fires here (no such cells), but it's a silent-failure mode.

## Documentation errors — quote-and-fix

**F1. [verification_plan.md](../verification_plan.md) §2 table — factually wrong label.**
> "64-bit ripple adder (Yosys `$add`) | 428 | 1253 | 19.0"
A 64-bit ripple-carry adder cannot have a 12-gate / 19.0-unit critical path (true ripple ≈ 200 units). I inspected Yosys's pre-ABC netlist: it emits a **carry-lookahead** structure (block carries at bits 15/31/47, multi-level lookahead assigns). The 19.0 number is correctly measured; the "ripple" label is wrong.
**Fix:** "64-bit adder (Yosys `$add` → carry-lookahead techmap, not a ripple-carry)".

**F2. [verification_plan.md](../verification_plan.md) §3.2 — stale, contradicts the design decision.**
> "`mix_spn10` (ROUNDS=8, the candidate),"
8 rounds was rejected on statistical grounds; the candidate is 10 rounds.
**Fix:** "`mix_spn10` (ROUNDS=10, the candidate; ROUNDS=8 was rejected — see [isa_spec.md](../isa_spec.md) §5)".

**F3. [verification_plan.md](../verification_plan.md) §2 caveat — stale reference.**
> "which would move the 8-round ratio to ~1.2×"
**Fix:** "which would move the 10-round ratio to ~1.5–1.6× (1.26/0.8)".

**F4. [verification_plan.md](../verification_plan.md) §3.5 — acceptance criterion inconsistent with measurement.**
> "Acceptance: `mix` post-route delay ≤ 1.1× multiplier post-route delay (margin for flow noise); area ≤ 1× multiplier."
Relative mapping measures **1.26×** — this criterion is already failed on paper with no remediation path stated.
**Fix:** append "Relative mapping measures 1.26×; if P&R confirms ≈1.26×, disposition against the user's 1–2× envelope (within it, though above the nominal 1.0× 'equivalent' target). If ≤1.1× is a hard gate, S-box delay re-optimization (item 6) is required first."

**F5. [verification_plan.md](../verification_plan.md) §4 — acceptance overstates the battery outcome.**
> "zero flags at |z| > 4"
The battery produced one flag (SPN-10, stride-big, mask-m=1, z=+4.49), later investigated.
**Fix:** "zero *unexplained* flags at |z| > 4 (one 4.5σ flag investigated: not reproduced at 16× sample size, neighboring configs clean — classified as statistical fluctuation; see test log)."

**F6. Dangling references.** "see test report" appears in [isa_spec.md](../isa_spec.md) §5, §7 and [verification_plan.md](../verification_plan.md) §1, §4, but **no test-report file exists** (evidence lives in [`tests_final.log`](../tests_final.log) / [`tests_adversarial.log`](../tests_adversarial.log)).
**Fix:** create [`TEST_REPORT.md`](../TEST_REPORT.md) consolidating results, or repoint all four references to the logs.

**F7. [isa_spec.md](../isa_spec.md) §5 — slightly rosy given §6's own 1.26×.**
> "Intended to fit in a single execute-stage cycle, like an integer multiplier."
A 1.26×-slower unit does not fit the multiplier's cycle.
**Fix:** "Intended to fit in a single execute-stage cycle alongside the integer multiplier; relative synthesis shows 1.26× the reference multiplier delay, so single-cycle fit at the multiplier's target frequency is not established — see §6 and the Sky130 P&R plan."

**F8. [isa_spec.md](../isa_spec.md) footer — stale.**
> "Pending: measured synthesis numbers, Sky130 P&R, independent peer review."
§6 now contains the (relative) synthesis numbers.
**Fix:** "Pending: Sky130 P&R with the real PDK (relative numbers only so far), independent peer review."

**F9 (minor). [isa_spec.md](../isa_spec.md) §5** — "(|z| ≤ 2.8, no growth with N)" omits the 4.49σ flag; suggest appending "; one 4.5σ flag in the main battery did not reproduce at 16× sample size — see test report."

## Requirements-coverage assessment (user asked for (a) multiplier-equivalent delay, (b) ≤ adder latency, (c) Sky130 P&R measurement)

- (a): **honestly reported as 1.26×, i.e., not met at nominal 1.0×** — the spec says so explicitly ("misses the 1.0× multiplier mark by 26%"). Within the user's 1–2× envelope. No inflation found.
- (b): **honestly reported as mutually exclusive with (a)** — "The 'no higher than an adder' and 'equivalent to a full multiplier' timing requirements are mutually exclusive as literally stated" (12.0 vs 62.0 units). Correct and prominent. (Note: the adder numbers themselves are sound; only the "ripple" label in the plan is wrong per F1.)
- (c): **honestly reported as not done** — "Full place-and-route on SkyWater 130 … is required before any absolute delay claim." The unit-delay ratios are never presented as nanoseconds. No inflation found.

## Encoding check (custom-0, funct7=0000000, funct3=000)

Legitimate use of the vendor-custom space: the RISC-V spec reserves custom-0/1/2/3 against future standardization, so **no standard extension can ever conflict**. Within custom-0, collisions between *vendor* extensions are possible (e.g., OpenVM uses custom-0/funct3=000 for its `terminate`; PULP's Spatz docs explicitly warn to check project-local custom-0 usage before choosing funct3/funct7). The spec's "This uses the reserved custom-0 space; it is not proposed for standardization in this form" is accurate and reasonably prominent as a standalone paragraph. **Suggestion:** add one sentence — "Integrators must check for collisions with other custom-0 extensions in the same project (funct3/funct7 space is shared)." No change needed to the encoding itself.

## Out of scope (not audited here)

RTL correctness beyond the mapped netlist, the Python statistical battery, S-box equation minimization, and the 3007-vector RTL testbench (I re-verified only the mapped-netlist 300-vector check). The archived workflow shows signs of exploratory messiness (a `sed` ordering bug in [`s_ksf.ys`](../synth/s_ksf.ys), an intermediate mislabeled copy step) — I traced the full timeline and confirmed the **final artifacts are correct**, but the scripts would benefit from a clean, single-pass regeneration flow before the P&R stage.