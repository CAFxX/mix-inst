# Direction 2: Bit-level Feistel (AND–XOR network)

**Goal (track-3, O133):** <10u, Fisher LIN+DIFF passing. No S-boxes: the only
nonlinear primitive is AND2, made bijective by XOR-ing it back Feistel-style.

**Status:** PROOF COMPLETE (this file). Build gated on proof — proof done, build proceeds.

---

## 1. The naive per-bit form is NOT proven — do not build it

The brief sketches `out[i] = in[i] XOR (in[(i+a)] AND in[(i+b)])` and claims it
is "an involution if the AND inputs don't include bit i". **That claim is false.**
Expanding two applications:

```
f(f(x))[i] = x[i] XOR (x[j] AND x[k]) XOR (f(x)[j] AND f(x)[k])
```

with `f(x)[j] = x[j] XOR (x[j+a] AND x[j+b]) ≠ x[j]` in general. The second-round
AND term does **not** cancel the first — the proof attempt in the brief dies at
exactly the line marked "wait, this needs care". Worse, the claim is not merely
unproven but **false**: width-8 exhaustive brute force (`d2_model.py naive 8 1 2`)
finds an explicit collision — `f(125) = f(163) = 99` (and `naive 8 1 3` gives
`f(94) = f(121) = 85`). The cyclic form is not injective, hence not bijective.
**Verdict on the naive form: refuted — do not build.**

## 2. The correct construction: alternating halves

Split the 64 bits by parity. Each half-round modifies one half using ANDs that
read **only the other half**, then XORs the result back.

**Half-round A** (even update), parameters a,b odd, key ka:
```
y[2i]   = x[2i] XOR (x[(2i+a) mod 64] AND x[(2i+b) mod 64]) XOR ka[2i]
y[2i+1] = x[2i+1]
```
**Half-round B** (odd update), parameters c,d odd, key kb:
```
z[2i]   = y[2i]
z[2i+1] = y[2i+1] XOR (y[(2i+1+c) mod 64] AND y[(2i+1+d) mod 64]) XOR kb[2i+1]
```
**Full round** R = B ∘ A. Key schedule: ka = K (even bits used), kb = rotl(K,13)
(odd bits used). Parity note: 64 is even, so `(even + odd) mod 64` is odd —
the AND taps of an even bit always land on odd bits (the untouched half), and
vice versa. This is load-bearing for the proof.

### Theorem (bijectivity)

Each half-round is a bijection — in fact an involution. Hence every full round,
and any composition of full rounds with fixed keys, is bijective.

*Proof.* Fix half-round A (B is identical with parities swapped). Let
M = {even indices} (modified), U = {odd indices} (untouched). For i ∈ M,

```
H(x)[i] = x[i] XOR F_i(x|_U) XOR ka[i],   F_i(w) = w[i+a] AND w[i+b],
```

where F_i reads only U-bits: i even and a,b odd imply i+a, i+b are odd mod 64.
For i ∈ U, H(x)[i] = x[i].

Invert: let y = H(x). For i ∈ U, x[i] = y[i] directly. For i ∈ M,

```
x[i] = y[i] XOR F_i(x|_U) XOR ka[i] = y[i] XOR F_i(y|_U) XOR ka[i],
```

because x|_U = y|_U. So the preimage x is uniquely determined by y — H is
injective, hence bijective on the finite set {0,1}^64. Moreover H is its own
inverse: for i ∈ U, H(H(x))[i] = x[i]; for i ∈ M,

```
H(H(x))[i] = H(x)[i] XOR F_i(H(x)|_U) XOR ka[i]
           = x[i] XOR F_i(x|_U) XOR ka[i] XOR F_i(x|_U) XOR ka[i]
           = x[i],
```

using H(x)|_U = x|_U. So H² = id. The key XOR is absorbed into the constant
ka[i] and changes nothing. ∎

*Corollary.* R = B ∘ A is bijective (composition of bijections). The cipher
x ↦ R^r(x) with any fixed key schedule is bijective. No S-box, no case analysis.

### Why this succeeds where MUX2 (O148) failed

O148's 4-stage MUX2 network died on a structural diffusion ceiling: a MUX2
`sel ? a : b` has **no linear feedthrough** — a select-bit flip propagates with
probability ≤ 1/2, giving ≤1.5×/stage confusion growth, 1.5⁴ ≈ 5-bit avalanche
ceiling. Here every output bit keeps a **guaranteed linear copy of its own
input bit** (`out[i] = in[i] XOR …`). The AND taps add nonlinear influence on
top of a feedthrough that can never vanish. This is the MUXD lesson (O148 §7:
"MUXD dodges LIN via its xor feedthrough") applied to a cheaper gate.

## 3. Influence analysis (derived before measuring)

Single-bit input flip, random background x, half-round A (even update):

- Flip at **even** bit 2j: y[2j] flips **always** (linear feedthrough). The two
  even bits 2j−a, 2j−b read 2j as an AND tap — each flips iff the *other* AND
  input is 1, probability 1/2 each. E[flipped] = 1 + 2·(1/2) = **2**.
- Flip at **odd** bit 2j+1: y[2j+1] unchanged; two even AND-slots flip w.p. 1/2
  each. E[flipped] = **1**.
- Mean per half-round: **1.5×**. Half-round B is symmetric (even flips → 1,
  odd flips → 2).

Full round R = B ∘ A. Even input flip: after A, e ≈ 2 even bits flipped
(1 guaranteed + 1 from slots), o = 0 odd. B leaves evens flipped (2) and each
flipped even fans to 2 odd AND-slots flipping w.p. 1/2 → +2 odds. E ≈ **4**.
Odd input flip: after A, e ≈ 1, o = 0; after B, 1 even stays + 1 odd from slots.
E ≈ **2**. **Mean per full round ≈ 3×** (pre-saturation): 1R ≈ 3, 2R ≈ 9,
3R ≈ 27 bits of 64.

Dependency cones: after 1R, even outputs see 3 input bits, odd outputs 7.
After 2R, cones reach ~7² ≈ 49 bits (minus overlap). Measured exactly in §5.

The 3×/round growth (vs 1.5×/stage for MUX2) comes from the feedthrough: flipped
even bits **survive** half-round B unchanged and fan out again, instead of
being re-gated with probability 1/2.

## 4. Cost model (pre-synth estimate)

Per half-round: 32× AND2 (1 gate level) + 32× XOR3 (in,key,tap-product — 1–2
levels). Full round ≈ 2×(AND2+XOR). By comparison: MUX2 layer = 2.0u (O138),
2-term linear = 4.0u (O147). Estimate: half-round ~1.5–2u, **full round ~3–4u
(target <5u)**, 2 full rounds ~6–8u (<10u gate for Fisher triage).

## 5. (a,b) offset study

Method: exact dependency cones (bitmask propagation) + sampled avalanche
(64 single-bit deltas × 1024 random x, vectorized) for odd (a,b), a≠b, after
1R and 2R (`d2_sweep.py`, `sweep1.json`). Metric: mean avalanche after 2R.

**Result: tap geometry is nearly FLAT.** All 132 pairs give av2 ∈ [3.13, 4.37];
all but the degenerate (1,33)/(33,1) cluster at 4.37±0.01. The (a,b) choice is
not the lever — same lesson as O141 ("tap geometry is NOT the binding
constraint"). Representative: (3,13): av1=2.44, av2=4.37, cone2 mean 12.5.

The real lever is **ANDs per bit** (proof still holds: F_i = XOR of ANDs still
reads only the untouched half, half-round still an involution — verified
empirically, `d2_sweep2.py`):

| form | taps | av1 | av2 | av3 |
|------|------|-----|-----|-----|
| 1-AND | (3,13) | 2.44 | 4.37 | — |
| 2-AND | (3,5,17,21) | 4.63 | 14.37 | 25.89 |
| 2-AND | (7,17,29,33) | 4.62 | 14.35 | — |
| 2-AND | (1,3,5,7) clustered | 4.20 | 8.72 | — |
| 3-AND | (3,11,17,27,9,31) | 7.31 | 23.66 | — |

495 4-tap sets swept (`sweep2.json`): spread taps win (14.2–14.4), clustered
taps lose (8.7). Chosen: **2-AND, taps (3,5,17,21)** symmetric A/B.
Per-round growth ≈ 3.1× (vs 1.8× for 1-AND, vs 1.5×/stage for MUX2/O148).

## 6. Structural differential analysis (the quality ceiling)

The XOR feedthrough — load-bearing for bijectivity — creates a structural
truncated differential. For input delta 2^k, output bit k inherits the linear
term through every half-round; the nonlinear part rarely cancels it:

`d2_probe.py`: P(output bit k flips | input delta 2^k), 4096 random x:

| rounds (2-AND) | max P | mean P |
|---|---|---|
| 2 | 1.000 | 0.854 |
| 3 | 0.729 | 0.624 |
| 4 | 0.568 | 0.522 |
| 5 | 0.523 | 0.503 |

At 2R, even k gives P=1.00 **provably**: round-2 half-A's AND taps read only
odd bits of the round-1 output, and under an even-k input delta no odd bit of
the round-1 output ever flips (half-A is identity on odds; half-B's nonlinear
terms read only even bits whose nonlinear parts tap odd input bits ≠ k) — so
the nonlinear term is delta-invariant and the linear x[k] term flips alone.
The low-8-bit difference chi2 z-scores at 2R are 27,000–517,000 (need |z|≲5).

The bias decays ~3–4×/round but only reaches the Fisher noise floor (|P−0.5|
≲ 0.01) at **~6 full rounds**. Mechanism verdict: the half-split construction
has a **fundamental feedthrough↔differential-bias tradeoff** — bijectivity
demands the linear term, the linear term creates the truncated differential,
and washing it out needs ~6 rounds. At ~3–4u per 2-AND full round (to be
measured), that is ~20u: **cost-quality incompatible under the <10u bar**.
More ANDs/bit (3-AND: 2R max still 1.00) or different taps do not change the
mechanism — only the decay constant.

## 7. S0 synthesis

Verilog generated by `gen_d2.py` with **literal bit indices** (no rotl-direction
ambiguity, same discipline as V3's gen_v3.py): `d2_1r_1a.v` (1R 1-AND),
`d2_1r_2a.v` (1R 2-AND, taps (3,5,17,21)), `d2_2r_2a.v` (2R 2-AND). XCHECK:
generated RTL evaluated as a Boolean circuit in Python matches the model
300/300 on all three files (`xcheck_vlog.py`).

**S0 not measured — persistent backoff.** Box load held 15–19 (≥12 backoff
threshold) for the full work session; the standing order forbids dispatching
synth under backoff. Cost anchor from the sibling D4 lane (O149, measured via
`run_synth.py`): a 1-AND bit-Feistel stage = **3.5u** ("2.0x/3.5u"). The 2-AND
full round here (2 ANDs + XOR5 per bit per half-round vs 1 AND + XOR3) scales
to ≈4.5–5.5u/round (estimate, labeled as such — not a measurement).

**Cost-quality arithmetic (the verdict's cost leg):** §6 shows ~6 full rounds
are needed to wash the self-flip bias to the Fisher noise floor. 6 rounds ×
≈5u/round ≈ 30u — 3× over the <10u bar. Even at an implausible 1.67u/round
(6×1.67 = 10), each half-round would need <0.83u for a 2-gate-level
(AND2→XOR) 64-bit stage — less than half the cheapest measured comparable
stage (MUX2 layer, 2.0u, O138). The budget cannot accommodate the rounds the
quality bar demands, under any plausible per-round cost.

## 8. Fisher triage

The verbatim `screen_lin_diff` run was gated on 2R S0 <10u and blocked by the
same backoff. Instead, `d2_probe.py` computes the screen's **exact DIFF
statistic** (low-8-bit chi2 on deduped (x, x⊕2^k) pairs, k=0..17 — identical
computation to `diff_cell_logps`) on the 2R-2AND model:

| k | low-8 chi2 z |
|---|---|
| 0 | 391,756 |
| 1 | 142,219 |
| 2 | 517,267 |
| 3 | 165,543 |
| 4 | 231,104 |
| 5 | 27,728 |
| 6 | 175,127 |
| 7 | 79,329 |

(PASS needs |z| ≲ 5; the Holm-Bonferroni bar is ~5σ.) The failure is not
marginal — it is five orders of magnitude beyond the threshold, driven by the
§6 probability-1 truncated differential (even k: difference bit k always set).
No multi-key averaging or Fisher-combining changes a 27,000σ signal; the
verbatim screen cannot pass. The sibling O149 lane independently measured
DIFF worst|z| 6.6e5–1.48e6 on its (naive-form) bit-Feistel stage — same
catastrophe, same order of magnitude.

## 9. Verdict — TERMINAL (O150)

**Direction 2 (standalone bit-level Feistel) is TERMINAL for sub-10u track-3:
cost-quality incompatible with a structural mechanism.**

1. **Bijectivity: proven** for the alternating-halves construction (each
   half-round is an involution; §2). The brief's naive per-bit form is
   **refuted**: not merely unproven — width-8 exhaustive search finds explicit
   collisions (`f(125)=f(163)=99` for a=1,b=2; `f(94)=f(121)=85` for a=1,b=3).
   Never build the naive form.
2. **Diffusion tuning is exhausted:** 132 (a,b) pairs swept — avalanche flat at
   4.37 (1-AND); ANDs/bit is the only lever (2-AND: 14.37 @2R; 3-AND: 23.66
   @2R; 495 4-tap sets swept, spread taps win).
3. **Killing mechanism — feedthrough↔differential-bias tradeoff:** the XOR
   feedthrough that makes the construction bijective (and gives it 3.1×/round
   growth vs MUX2's 1.5×) creates a structural truncated differential:
   input delta 2^k → output bit k flips with P=1.00 for every even k at ≤2R
   (**proven**, §6; confirmed 1.0000 exact on 3 tap sets), 0.70–0.85 for odd k.
   The bias decays only ~3–4×/round → ~6 full rounds needed for the Fisher
   noise floor → ≈30u vs the <10u budget.
4. **Scope:** kills the standalone alternating-halves bit-Feistel (1/2/3-AND
   per bit, any odd tap sets) as a sub-10u track-3 cipher. The mechanism is
   family-wide: any half-split F leaves the linear x[i] term, which gives the
   P=1 self-flip after the first touching half-round. NOT killed: the
   construction as a cheap bijective nonlinear *component* (proof stands);
   use at >10u budgets (~6+ rounds would likely pass Fisher — untested);
   the 2.0u MUX2 gate (O138).
5. **Relation to O149:** sibling D4's "bit-Feistel" was the *naive* form
   (`x ^ (rotl(x,a) & rotl(x,b))`) — the refuted one — used as a diffusion
   stage after MUX2. O149's kill stands on its own measurements; note its
   Option C function is not provably bijective (general refutation in §1).

Re-test trigger: a bijective nonlinear with a sub-1u feedthrough-free
mechanism (the half-split proof *requires* the linear x[i] term, so this
means a different bijectivity construction), or a synthesis path changing
cost/round by >3×.
