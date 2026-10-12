# Direction 4: Fix the 9.4u MUX2 (O148)

## The O148 design (what we're fixing)

4-stage network of 64 parallel MUX2 cells per stage (from `../middepth/v3_mux2x4/`):

```
stage: y_j = mux(sel_j, a_j, b_j),  sel_j = rotl(x,s)[j], a_j = rotl(x,p1)[j], b_j = rotl(x,p2)[j]
y_j = (sel_j & a_j) | (~sel_j & b_j) = b_j + sel_j*(a_j + b_j)   (degree-2 Boolean)
```

Base schedule `(s,p1,p2)`: `[(0,7,29), (13,31,53), (5,19,43), (11,23,47)]`.
Key whitening `x^K` in, `^ rotl(K,13)` out (battery convention).
S0: 9.4u (1408 cells), UNDER the 10u bar. Fisher: LIN D=4096/4096, DIFF worst|z|~1e6 — catastrophic.
Select logic is **already input-dependent** (`sel_j` = a rotated input bit), so Option B's
"fixed select" premise does not apply; what remains is "different wiring".

## Influence analysis — WHY it fails

### 1. DIFF: the counting bound (wiring-independent, from O148)

Each MUX2 has 3 input slots. A single-bit input flip propagates through a slot w.p. <= 1/2
(data flip needs sel=1/0; sel flip needs a!=b). Each input bit feeds exactly 3 slots per
stage (one per role, rotations are permutations), so E[output flips] = 3 x 1/2 = **1.5x/stage**
for ANY wiring — slots are conserved. 1.5^4 ~= 5 bits avalanche (measured 4.2).
The DIFF gate needs the low-8 output-difference bits ~uniform, which needs each low bit
flipping w.p. ~= 1/2, i.e. ~32-bit avalanche. 5 << 32. No rotation/wiring pattern changes this.

### 2. LIN: affine degeneration (new — the precise mechanism)

The LIN gate builds 64x64 matrices from 64 CONSECUTIVE outputs. Because the battery
whitens as `x = V ^ K` with `V` consecutive, **every LIN block varies only input bits 0-5**
(all 64 patterns); bits 6+ are constant within a block (verified from `lin_diff.py`).

Per MUX2, at most 3 input bits are read. For the base rotation schedule the 3 inputs are
spread so that **at most one is a varying low bit** (the other two are high-bit constants
over the block). A MUX2 with <= 1 varying input degenerates:

- sel varies, a=b=const -> constant (if a==b) or affine wire
- sel const, one data bit varies -> affine (`c*a + const`)
- all const -> constant

Hence after stage 1, ALL 64 bits are AFFINE functions of the 6 low input bits (measured:
stage-1 outputs for x in [0,64) are 0 or copies of input bits 0-5). By induction — the
rotation schedule keeps "at most one varying input per MUX" at every stage — **all 4
stages stay affine in the 6 varying bits**. 64 affine functions of 6 variables span
dimension <= 7. Measured rank: 6-7 for 1, 2, 3 AND 4 stages (all keys). The gate needs
rank >= 62; D=4096/4096 always. This is not "weak diffusion" — it is structural collapse
to an affine subspace.

### 3. The degree bound (what LIN actually requires)

Over 6 varying variables, the space of degree-<=d Boolean functions has dimension
sum_{i=0}^{d} C(6,i): d=1 -> 7, d=2 -> 22, d=3 -> 42, d=4 -> 57, d=5 -> 63, d=6 -> 64.
**Rank >= 62 requires the outputs to have degree >= 5 in the 6 varying bits.**
A non-degenerate MUX2 stage at most doubles degree (sel*a term), so we need >= 3 stages
of *consistently non-degenerate* MUX2 (every MUX combining >= 2 varying bits, every
stage) just to reach degree 8. Random wirings don't satisfy this (~19% of MUXes are
non-degenerate at stage 2 for random rotations; the rest stay affine) — which is why
all ~20 V3 wiring variants failed. It is a wiring *discipline*, not a wiring *draw*.

### 4. Rank invariance (why Option A cannot fix LIN)

The LIN gate measures rank of the row space of 64 consecutive outputs. If L is an
invertible linear map, rank{L(rows)} = rank{rows} — row-space dimension is preserved
exactly. A bijective linear diffusion stage therefore leaves D=4096 **unchanged**.
A non-bijective linear stage can only *decrease* rank. **No linear post-stage (2-term,
3-term, any (r1,r2)) can fix the LIN failure.** The 3-term XOR of Option A multiplies
the DIFF growth by 3x (1.5^3 x 3 ~= 10 bits avalanche) but 10 << 32, so DIFF stays
FLAG too. Option A is structurally dead on both families; we verify empirically below.

### 5. Option B (better select) — dead

Select is already input-dependent (`rotl(x,s)`). "Different wiring" cannot beat the
counting bound (1.5x/stage, wiring-independent) nor the affine degeneration (needs the
degree-doubling discipline, which is a redesign, not a wiring tweak — V3's ~20 variants
prove the point). Making the select *nonlinear* (e.g. AND of 2 bits, Direction-1 style)
breaks the degeneration (select becomes quadratic) but costs AND(1.5u)+MUX(2.0u)=3.5u
per stage -> 4 stages = 14u, over budget. Dead within <10u.

### 6. Option C (bit-Feistel diffusion) — the only one that *can* touch LIN

`out[i] = in[i] ^ (in[j] & in[k])` is nonlinear, so rank invariance doesn't apply, and it
gives 2.0x/stage growth (feedthrough 1 + 2 AND-slots x 1/2). But: 3-stage MUX2 with the
base wiring is affine-degenerate (degree 1 in the LIN bits); the bit-Feistel lifts it
only to degree 2 (dim 22 < 62). **Option C as specified still fails LIN by the degree
bound.** It would need the non-degenerate MUX2 wiring (degree 8) underneath, which is
the redesign discussed in section 3.

## Predicted verdicts (to be confirmed by measurement)

| Option | S0 (est) | LIN | DIFF | Reason |
|---|---|---|---|---|
| A: 3xMUX2 + 3-term XOR | ~9u | D=4096 FLAG | FLAG | rank invariance; 10-bit avalanche |
| B: rewired 4xMUX2 | 9.4u | D=4096 FLAG | FLAG | counting bound; degeneration |
| C: 3xMUX2 + bit-Feistel | ~9.9u | FLAG (deg<=2) | FLAG | degree bound; 7-bit avalanche |

## Measurements

### Avalanche (64 deltas x 4096 xs, key 0x9E3779B97F4A7C15; mean/min/max)

| Design | Avalanche | vs prediction |
|---|---|---|
| O148 base (4-stage MUX2) | 4.2 bits (V3 measured) | 1.5^4 = 5.1 |
| A: 3-stage MUX2 + 3-term XOR (r1=11,r2=23) | **8.78 / 8.54 / 9.00** | 1.5^3 x 3 = 10.1 |
| A: 3-stage MUX2 + 3-term XOR (r1=7,r2=29) | **7.41 / 7.25 / 7.60** | 1.5^3 x 3 = 10.1 |
| C: 3-stage MUX2 + bit-Feistel (a=11,b=23) | **5.94 / 5.78 / 6.12** | 1.5^3 x 2 = 6.75 |
| C: 3-stage MUX2 + bit-Feistel (a=7,b=29) | **5.63 / 5.49 / 5.79** | 1.5^3 x 2 = 6.75 |

All far below the ~32 bits the DIFF gate needs (each low output bit must flip w.p. ~= 1/2
for the low-8 histogram to look uniform). Growth predictions confirmed within collisions.

### Fisher triage (screen_lin_diff verbatim, 10 keys, N=2^18)

| Design | LIN | DIFF | Verdict |
|---|---|---|---|
| A: 3-stage MUX2 + 3-term XOR (r1=11,r2=23) | D=4096/4096 all keys, nrej=10 | worst\|z\| 597,797–1,480,000, nrej=10 | **FLAG/FLAG** |
| C: 3-stage MUX2 + bit-Feistel (a=11,b=23) | D=4096/4096 all keys, nrej=10 | worst\|z\| 656,199–1,480,000, nrej=10 | **FLAG/FLAG** |

Option A confirms **rank invariance**: LIN D is 4096/4096, identical to the no-diffusion
base — the linear stage changed nothing (as proven). DIFF improved from ~1.4e6 to ~6e5
in the best key but remains astronomically far from pass (need |z| ~ O(1)).
Option C confirms the **degree bound**: the nonlinear bit-Feistel lifts degree 1 -> 2,
but quadratics span only 22 dims << 62, so D stays 4096/4096.

### S0 (run_synth.py, ref mul64 103.5u, XCHECK analyze.py==analyze2.py)

| Design | cells | area | crit | Verdict |
|---|---|---|---|---|
| O148 base (4-stage MUX2) | 1408 | 4672 | **9.4u** | cost-eligible |
| A: 3-stage MUX2 + 3-term XOR | 1408 | 4544 | **10.2u** | **OVER 10u** — the 3-term XOR diffusion costs 2 XOR levels (~2.8u), not the estimated 2u |
| C: 3-stage MUX2 + bit-Feistel | 1536 | 4864 | **9.4u** | cost-eligible but Fisher-dead (see above) |

Option A is cost-ineligible (10.2u > 10u strict) AND Fisher-dead. Option C is
cost-eligible (9.4u) but Fisher-dead. Both fail; Option B is dead by analysis
(counting bound is wiring-independent; select already input-dependent; nonlinear
select costs 3.5u/stage). The impossibility argument (§Impossibility) shows no
MUX2/XOR wiring can pass Fisher in <10u.

## Impossibility argument (first-principles, wiring-independent)

In <10u delay there are at most 4 MUX2/XOR levels (4-stage MUX2 = 9.4u measured).
Let n_m = #MUX2 stages, n_x = #XOR levels, n_m + n_x <= 4.

- **LIN needs degree >= 5** in the 6 varying bits (Section 3): degree-<=4 functions span
  only 57 dimensions, so rank <= 57 <= 61 always -> D=4096 -> FLAG. Degree-doubling
  needs n_m >= 3 *non-degenerate* stages (1->2->4->8).
- **DIFF needs ~32x growth** (Section 1): max growth = 1.5^n_m x 2^n_x
  (MUX2 = 1.5x/stage counting bound; XOR level at most doubles fanout).
- n_m=3, n_x<=1: growth <= 1.5^3 x 2 = 6.75 << 32. FAIL.
- n_m=4, n_x=0:  growth = 5.06 << 32. FAIL.
- n_m<=2: degree <= 4 -> LIN FAIL.

**No (n_m, n_x) with n_m + n_x <= 4 satisfies both. The MUX2/XOR gate set cannot pass
Fisher in <10u, regardless of wiring, select logic, or diffusion-stage placement.**
The 2.0u MUX2's 1.5x/stage is the best nonlinear growth-per-delay available
(bit-Feistel is 2.0x per 3.5u = worse per delay); XOR's 2x/level is linear and cannot
fix LIN (rank invariance). Breaking this needs a new primitive: <=2u nonlinear with
>2x/stage growth, or a sub-1u feedthrough.
