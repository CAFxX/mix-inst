# RISC-V `mix` Instruction — ISA Specification (Draft 0.1)

## 1. Instruction

```
mix rd, rs1, rs2
```

`rd ← MIX(rs1, rs2)`, where `rs1` is the value to be mixed ("Val") and
`rs2` is the per-invocation key ("key"). Intended primarily as a hash-map
finalizer: one dynamic invocation fully mixes `Val` with `key`.

## 2. Encoding (proposed)

R-type, `custom-0` major opcode (`0001011`), RV64 only:

```
 31        25 24   20 19   15 14 12 11    7 6      0
+------------+-------+-------+-----+-------+--------+
| 0000000    | rs2   | rs1   | 000 | rd    | 0001011 |
+------------+-------+-------+-----+-------+--------+
  funct7=0x00  key     val   f3=0
```

Assembly: `mix rd, rs1, rs2`. Compiler intrinsic (proposed):

```c
uint64_t __riscv_mix(uint64_t val, uint64_t key);   // emits `mix`
```

This uses the reserved custom-0 space; it is not proposed for
standardization in this form. Integrators must check for collisions with
other custom-0 extensions in the same project (the funct3/funct7 space
is shared between vendor extensions).

## 3. Semantics

Let `x` be a 64-bit state, `P` the PRESENT 64-bit bit-permutation
(bit `i` → bit `16·i mod 63` for `i < 63`; bit 63 fixed), `S` the
PRESENT 4-bit S-box applied to each nibble, and

```
rk[i] = ROTL64(key, 13·(i+1) mod 64) XOR RC[i],   i = 0..10
RC[i] = (i+1) · 0x9E3779B97F4A7C15 mod 2^64
```

Then:

```
x ← val XOR key
repeat i = 0..9:   x ← P(S(x XOR rk[i]))
rd ← x XOR rk[10]
```

Pure function of the two source registers. No architectural state is
read or written besides `rd`. Deterministic: same `(val, key)` always
yields the same `rd`, on every implementation.

For each fixed `key`, `MIX(·, key)` is a bijection (permutation) of the
`2^64` values: every round is a composition of XOR-with-constant
(bijection), a bijective 4-bit S-box (bijection), and a bit permutation
(bijection); the initial `val XOR key` and final whitening are likewise
bijections. This holds for all keys by structural induction over the
construction. As supporting empirical evidence, a structurally identical
16-bit instance was exhaustively checked for 7 keys (65536/65536 distinct
outputs each).

## 4. Architectural properties

- **XLEN**: 64 (RV64). The operation is defined on 64-bit words.
- **Exceptions**: none specific to `mix`. Raises illegal-instruction if
  the extension is not implemented/enabled.
- **Traps/interrupts**: instruction is atomic w.r.t. the hart's
  architectural state; no partial update is visible.
- **Memory**: does not access memory.
- **Privilege**: available at all privilege levels (unprivileged).
- **No side channels in the ISA model**: single-valued deterministic
  function; implementations must take care that physical side channels
  are out of scope for a non-cryptographic mixer (see §7).

## 5. Microarchitecture guidance

Reference implementation is fully combinational (no sequential state):

- 10 rounds × (64-bit XOR + 16 parallel 4-bit S-boxes + wiring
  permutation), plus input XOR and output whitening XOR.
- Rotations and the pLayer are pure wiring (zero active area).
- Round keys derive from `rs2` by rotation (wiring) + XOR with a hard
  constant.
- Intended to fit in a single execute-stage cycle alongside the integer
  multiplier; relative synthesis shows 1.26× the reference multiplier
  delay, so single-cycle fit at the multiplier's target frequency is not
  established — see §6 and the Sky130 P&R plan in [`verification_plan.md`](verification_plan.md).

**Round count rationale.** 8 rounds meets the delay target most closely
(1.02× the reference multiplier in relative synthesis) but fails the
statistical requirement: on sequential inputs the Lemire-X=10 projection
(decile uniformity of the output's high bits) shows z-scores up to +69
across keys, growing with sample size — a genuine diffusion failure that
SplitMix64 and Murmur3-fmix64 do not exhibit. 9 rounds still fails
(z = +29.6 at N=2^20 on the worst key, growing ∝√N). 10 rounds is the
smallest count clean on the full reduction battery and all adversarial
configs (|z| ≤ 2.8 on Lemire/mask/mod-y, no growth with N).
Known limitation: per-bit screening finds small key-dependent single-bit
biases on *raw sequential* inputs at 10 rounds (~20% of keys show some
bit with |z|>4 at N=2^18, δ≈0.004; undetectable after any reduction —
all Lemire/mask/mod-y tests pass). SplitMix64 exhibits the same class of
phenomenon (bit 31, δ≈0.0033). 12 rounds is clean on the same screen
(0/32 flags) at ≈1.51× multiplier delay. See [TEST_REPORT.md](TEST_REPORT.md) §4.

Area/delay budget: 1–2× a full-width 64-bit multiplier (user requirement).

## 6. Measured implementation characteristics

Relative synthesis, Yosys 0.33 + ABC (`-fast`: strash/dretime/map, which
preserves prefix-adder structure that the default script destroys) mapped
to a unit-delay teaching cell library. **Ratios only** — absolute Sky130
numbers require P&R with the real PDK (see [`verification_plan.md`](verification_plan.md)).

| Design | Cells | Unit-gate area | Crit. path (unit) | Delay vs ref mul | Area vs ref mul |
|---|---:|---:|---:|---:|---:|
| `mix` 10-round (this spec) | 7614 | 23685 | 62.0 | **1.26×** | 0.53× |
| `mix` 8-round (rejected) | 6093 | 18965 | 50.4 | 1.02× | 0.43× |
| 64×64→64 multiplier (Yosys `$mul` ref) | 17115 | 44548 | 49.2 | 1.00× | 1.00× |
| 64-bit Kogge-Stone adder (hand RTL) | 1407 | 3650 | 12.0 | 0.24× | 0.08× |

Caveats:

- The reference multiplier is Yosys's `$mul`, not a hand-optimized
  Booth/Wallace tree; a production multiplier may be ~20% faster, which
  would move the 10-round ratio toward ~1.5×. The Sky130 comparison must
  use the best available multiplier.
- A fast 64-bit adder is ~4–5× faster than any adequate 64-bit mixer
  (12.0 vs 50–62 unit delays). The "no higher than an adder" and
  "equivalent to a full multiplier" timing requirements are mutually
  exclusive as literally stated; only the multiplier target is achievable
  with acceptable statistics (see final report §"Requirement
  reconciliation"). The 10-round design misses the 1.0× multiplier mark
  by 26% in this relative mapping — within the user's 1–2× area/power
  envelope but above the nominal delay target; Sky130 P&R will determine
  the real ratio.

Full place-and-route on SkyWater 130 (OpenLane/OpenROAD) is required
before any absolute delay claim; the flow and acceptance criteria are
documented in [`verification_plan.md`](verification_plan.md).

## 7. Security scope (non-goals)

`mix` is a **hash-map finalizer**, not a cryptographic primitive:

- The key schedule provides *no related-key resistance by design*: round
  constants cancel under seed differences, so Δrk[i] = ROTL(Δkey, 13·(i+1))
  is fully attacker-controlled. This is acceptable because the seed is a
  public per-map value with no related-key oracle; the design must never
  be used where related-key security is required.
- No claim is made about preimage resistance, collision resistance, or
  PRF security under adversarially chosen keys.
- Statistical quality was measured with SAC/BIC/uniformity batteries and
  sequence tests under raw, Lemire, mask, and mod-`y` reductions, using
  exact null distributions (preimage counts, not uniform-bin
  approximations), versus SplitMix64 and Murmur3-fmix64 under identical
  conditions (see [TEST_REPORT.md](TEST_REPORT.md)). These are empirical, finite-sample
  measurements — not proofs of universal guarantees. Notably, 8-round
  and 9-round variants were rejected on measured statistical grounds;
  "ideal SAC/BIC/differential uniformity for all keys" is not claimed.

## 8. Software model

Bit-accurate reference: `workspace/mix/spn.py` (`mix_spn_scalar`,
`mix_spn_vec`). RTL: `workspace/mix/rtl/mix_spn10.v`, verified against
3007 golden vectors from the Python model (Icarus Verilog, 3007/3007 pass).

---

*Draft 0.1 — 2026-10-01. Pending: Sky130 P&R with the real PDK (relative
numbers only so far); peer review completed 2026-10-01 (see [`reviews/`](reviews/)).*
