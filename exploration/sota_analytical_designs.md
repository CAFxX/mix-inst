# Analytical SOTA Design Note — Wide & Latency-Aware Constructions for RV64 `mix`

**Date:** 2026-10-03. **Author:** analytical subagent (reference-text pass, complements the web survey).
**Context:** `~/workspace/mix/exploration/`. Frontier: 6-round Feistel (S1/chi), best 37.0u where
the 64×64 multiplier is 103.5u. Hard constraints: delay ≲ 37u, no 64-bit multiplies (~40u each),
no long adder chains, ~4000–5000 cells, cheap key injection (XOR/rotations), bijective per fixed
key. Statistical bar: S1 screen, S2 differentials, PractRand 1GB, SmallCrush, SAC, BIC.
This note does depth arithmetic in our own measured units instead of guessing.

## §1 — Calibration: our unit-delay model, measured not guessed

### 1.1 The unit model (from `synth/mini.genlib`, used by the authorized `run_synth.py`)

| Cell | Delay (u) |
|---|---|
| INV, BUF, NAND2, NOR2 | 1.0 |
| AND2, OR2, AOI21, OAI21 | 1.5 |
| AND3/OR3, NAND3/NOR3 | 1.7 / 1.2 |
| **XOR2, XNOR2, MUX2** | **2.0** |

Critical path = sum of pin delays along the longest path (dual-analyzer agreement required).
Note the load-bearing fact: **one XOR2 level costs 2u**, not 1u. Estimates elsewhere in this
project that assumed ~1u/XOR-level are optimistic by ~2× on XOR-heavy paths.

### 1.2 Measured layer delays (pinned Yosys 0.69, `run_synth.py`, dual-analyzer agreement)

Each module below exposes one candidate layer input→output so S0 measures the layer itself.
Source: `/tmp/cal_layers.v` (kept with this note's evidence).

| # | Layer | Measured | Notes |
|---|---|---:|---|
| 1 | S1 4-bit S-box layer (16×, our workhorse) | **3.7u** | 262 cells/64-bit |
| 2 | Blink/Rasoolzadeh class-1 depth-3.5 4-bit S-box | **3.4u** | single nibble; S=[1,0,9,3,8,5,e,7,4,2,c,b,a,f,6,d] |
| 3 | chi64 `y_i=x_i⊕(~x_{i+1}·x_{i+2})` | **3.5u** | complement costs ~0.5u vs complement-free |
| 4 | χχ_64 proxy (χ_31∥χ_33, Eurocrypt'25 ChiChi core, λ omitted) | **3.0u** | bijective (both odd); λ adds ≤1 XOR level on 4 bits |
| 5 | Ascon 5-bit S-box (NIST SP 800-232 Table 6) | **6.2u** | single S-box; 68% deeper than S1 |
| 6 | Gimli SP-box (96-bit column, spec Algorithm 1) | **9.6u** | sequential x→y→z dependencies are real |
| 7 | 64-bit linear `x⊕rotl(x,3)⊕rotl(x,11)` (2 XOR levels) | **4.0u** | = 2×2u, as the model predicts |
| 8 | Keyed-SPN stage: 16×S1(nibble⊕key) + transpose perm | **5.7u** | key XOR inside; perm is free wiring |
| 9 | Blink-style SPN round: 16×BS(nibble⊕k) + Midori MDS + key + nibble perm | **8.6u** | |
| 10 | S1 SPN round: 16×S1(nibble⊕k) + (3,11) linear | **8.1u** | |
| 11 | EM round: chi64 + (3,11) linear | **6.7u** | abc fuses ~0.8u vs naive sum |
| 12 | UFN expansion F: 16→48 bit (4×S1 + expand + key) | **6.2u** | |
| 13 | One r9-style Feistel round `L^lin(S1(R))^rk` | **7.7u** | 6.83u effective in the 6-round chain (cross-round merging saves ~0.9u/round) |
| 14 | One correct-LM round `d=L⊕R; t=chi32(d⊕rk); (R⊕t, d)` | **5.5u** | no linear layer in F |

### 1.3 Bijectivity checks (GF(2) rank, load-bearing for any non-Feistel chassis)

Feistel F's need not be bijective — but SPN, Even-Mansour, and Beneš-style constructions do.

| Map (64-bit) | Rank | Verdict |
|---|---|---|
| `x⊕rotl(x,3)⊕rotl(x,11)` | 64 | bijective ✓ |
| `x⊕rotl(x,1)⊕rotl(x,2)`, `(5,17)`, `(7,13)` variants | 64 | bijective ✓ |
| Midori almost-MDS 4×4 (nibble matrix) | 4 | bijective ✓ |
| S1, Blink S-box (table inspection) | perm | bijective ✓ |
| chi64 (even width) | — | **NOT bijective** (χ_n bijective iff n odd) — fine inside Feistel F, fatal for EM/SPN |
| χχ_64 (χ_31∥χ_33) | — | bijective by Belkheyar et al. Thm 4 (m=32 even) ✓ |

### 1.4 Depth-efficiency: delay per input bit covered by the nonlinear layer

| Layer | Depth | Neighborhood | u per bit |
|---|---|---|---|
| χχ_64 | 3.0u | 3-bit | **1.00** |
| Blink 4-bit S-box | 3.4u | 4-bit | 0.85 |
| S1 4-bit S-box | 3.7u | 4-bit | 0.93 |
| chi64 | 3.5u | 3-bit | 1.17 |
| Ascon 5-bit S-box | 6.2u | 5-bit | **1.24 (worst)** |

**Reading:** 4-bit S-boxes are the sweet spot in our flow. The Ascon 5-bit S-box is the worst
trade (68% deeper for 25% wider) — "bigger S-box" is not a latency strategy here. χχ_64 is the
shallowest *bijective* whole-state option and beats our chi64 by 0.5u precisely because it drops
the complement.

---

## §2 — Per-reference analysis (depth / diffusion / keying arithmetic)

### 2.1 Ascon-p (NIST SP 800-232; Dobraunig et al.)

Round = pC (const XOR, ~free) ∘ pS (64 parallel 5-bit S-boxes) ∘ pL (`x_i⊕(x_i>>>r1)⊕(x_i>>>r2)`).
Measured: S-box **6.2u** + linear 4.0u ≈ **10.2u/round**. Ascon needs 6–8 rounds (p^b) for its
margin; 6 rounds ≈ 61u ≫ 37u. Even a 3-round reduced variant (≈31u) loses the cryptanalysis
backing that justifies Ascon in the first place, and at 3 rounds we are no longer "using Ascon"
but "using an expensive S-box" — and §1.4 shows the 5-bit S-box is depth-inefficient anyway.
**Verdict: killed by arithmetic. Do not build.** (Agrees with the web survey's negative result;
this is the independent measurement behind it.)

### 2.2 Xoodoo (Daemen et al.; "Xoodoo cookbook")

Round (384-bit, 4×3×32): θ (`P←A0+A1+A2; E←P≪+P≪; Ay←Ay+E` = 4 XOR levels ≈ 8u in our units),
ρ (free), ι (const), χ (3-bit, depth ~2 ≈ 3u), ρ (free). ≈ **11u/round** on its native geometry.
Xoodoo needs 12 rounds (6 in Xoofff with reduced claims). A 64-bit adaptation needs a new
plane geometry (e.g. 4×2×8) whose diffusion must be re-validated from scratch, and θ's 4-XOR
tree is less efficient than our 2-XOR linears. 6 adapted rounds ≈ 60u+; a 3-round hack ≈ 33u
with no security argument. **Verdict: killed — worse per-round than our chi+linear (6.7u),
and the geometry redesign is unvalidated work.** (Agrees with survey.)

### 2.3 Gimli (Bernstein et al.)

SP-box per 96-bit column: `x≪24; y≪9; x←x⊕(z≪1)⊕((y∧z)≪2); y←y⊕x⊕((x∨z)≪1);
z←z⊕y⊕((x∧y)≪3); swap(x,z)`. The sequential dependencies (y needs new x, z needs new y)
are inherent — **measured 9.6u per SP-box**. 8 rounds ≈ 77u ≫ 37u.
*Discrepancy note:* the web survey estimated "8-round core ≈ 16–20 logic levels ≈ 25–30u"
(citing 47 levels/24 rounds unrolled). That does **not** reproduce in our flow: one SP-box
alone is 9.6u, so 8 rounds ≈ 77u. The survey's figure likely refers to a different metric or
a reduced variant; until its source is produced, the direct measurement stands.
**Verdict: killed by measurement. Do not build EM-over-Gimli** (the survey's rank-2 lead
is rejected on this arithmetic).

### 2.4 Forkciphers — ForkAES/ForkSkinny (Andreeva et al., ePrint 2019/1004)

Iterate-fork-iterate: input → shared-prefix rounds → fork into two states → two independent
suffix permutations → **two** output blocks. The entire performance win of the primitive is
"two outputs for ~1.5× the cost of one". We need exactly one 64-bit output; the fork buys
nothing and the shared-prefix/suffix split adds key-schedule and control complexity.
**Verdict: structural mismatch, killed.** (Agrees with survey.)

### 2.5 THF / Blink-64a (Wang et al., ToSC 2025 = ePrint 2025/1314, the THF paper)

The paper's unrolled @45nm table (already in `sota_leads.md`): SPEEDY-6-192 2.54ns,
PRINCE 2.63ns, MANTIS 3.28ns, QARMA-64 3.44ns, Midori64 4.69ns; Blink-64a core 2.92ns
(~11% slower than PRINCE). Blink-64a = 5-round SPN: depth-3.5 involutory 4-bit S-box +
Midori 4×4 almost-MDS (XOR depth 2) + cell permutation + key XOR + round constant, round
keys by **slicing a long master key (zero key-schedule logic)**.
*Correction to the survey's estimate:* the survey's "≈6.5–7u/SPN round → 5 rounds ≈ 35u"
assumes ~1u per XOR level. In our flow (XOR2 = 2u) a Blink round measures **8.6u**, so the
literal 5-round Blink-64a = **43u ≫ 37u — killed as specified**. The salvageable variants:
(a) 4-round Blink-style = 4×8.6 = **34.4u** ✓ (loses the paper's 5-round security claim;
our statistical bar is the judge); (b) 5 rounds with a cheaper linear. The key-slicing idea
transfers cleanly: our 64-bit key can supply round keys as `rotl64(k, c·i)` (free) —
zero-logic key schedule is already what our affine schedule approximates.
**Verdict: literal Blink-64a killed by measurement; 4-round variant is a live candidate
(§3.4), ranked below the S1-based wide SPN which is cheaper per round (8.1u).**

### 2.6 Unbalanced Feistel (Schneier–Kelsey 1996; Khufu/Khafre family)

Target-heavy 48:16: round = `T ← T ⊕ F(S)` (F: 16→48, measured **6.2u**) + 16-bit rotation
(free). Per round ≈ 6.2 + 2.0 (48-bit XOR) = **8.2u**. One full pass (every bit sourced once)
= 4 rounds = 32.8u — but one pass is a priori S2-marginal (each bit mixed through the narrow
F exactly once; our balanced 5-rounders died at S2 with *more* mixing than this). A safe
6–8 rounds = 49–66u ≫ 37u. Depth per F-input-bit: 8.2/16 = 0.51 vs balanced Feistel's
6.83/32 = 0.21 — **balanced wins on depth efficiency**; the "narrow F can be stronger"
argument doesn't materialize because our F is already shallow.
40:24 split is worse (wider F ≈ 7.7u, 9.7u/round). **Verdict: killed by arithmetic.**
(Agrees with survey; the numbers are the new evidence.)

### 2.7 Keyed Beneš / switching networks (Waksman; Beneš)

Two hard facts: (1) A 2×2 switch cannot be nonlinear *and* bijective — AGL(2,2) already
contains all 24 2-bit permutations, so any bijective 2-bit "S-box" is affine. Keyed 2-bit
switches are therefore linear in the data (for fixed key) and contribute only routing.
(2) 64-bit Beneš needs 11 stages × 32 switches; MUX2 = 2u ⇒ **22u for the switching alone**,
leaving ~15u for nonlinearity.
The "nonlinear keyed Beneš" consequently collapses to one of two honest designs:
(i) MUX stages (keyed routing) interleaved with bijective nonlinear layers (χχ_64, 3.0u):
11×2 + 3×3 = **31u** — but the linear part is mere wire permutation (branch number 2),
so this is a 3-nonlinear-layer SPN with weak diffusion, high S2 risk (§3.5 analyzes the
buildable version); (ii) keyed 4-bit S-boxes on Beneš wiring = a keyed SPN, which is §3.3.
**Verdict: no free lunch — the Beneš wiring is a (good) fixed permutation; the design
problem reduces to ordinary SPN depth/round tradeoffs, analyzed in §3.3/§3.5.**

### 2.8 ChiChi (Belkheyar et al., Eurocrypt'25; Andreoli et al. generalizations)

χχ_{2m} = intertwined χ_{m-1}∥χ_{m+1} ⊕ λ(x), **bijective for m even** (Thm 4); degree 2;
differential/linear profile of χ_{m-1}∥χ_{m+1}. For n=64 (m=32): χ_31∥χ_33 + 4-bit λ
correction. Measured proxy (λ omitted): **3.0u** — shallower than our chi64 (3.5u, the
complement costs 0.5u) and *bijective*, which chi64 is not. This is the single most
important primitive finding of this pass: **a bijective chi-class whole-state layer cheaper
than our non-bijective chi**. It unlocks Even-Mansour (§3.2) and any SPN/Beneš chassis,
which were previously blocked on the even-width chi bijectivity problem.
*Caveat:* proxy omits λ (≤1 XOR level on 4 bits); reconstruct exactly from the paper
before tapeout-grade claims. For S0–S4 screening the proxy is representative.
**Verdict: live — the bijective-layer slot in §3.2/§3.5.**

### 2.9 Correct Lai–Massey (cf. our round-13 degenerate attempt)

Round-13's naive LM preserved `D = L⊕R` across rounds (every F saw the same input).
The fix is a true orthomorphism: `(L',R') = σ(L⊕t, R⊕t)` with `σ(a,b) = (b, a⊕b)`
(verify: `σ(x)⊕x = (a⊕b, a)`, a permutation, so σ is an orthomorphism; inverse:
given `(L',R')`, `d = R'`, `t = F(d⊕rk)`, `R = L'⊕t`, `L = R'⊕t` ✓ bijective).
Round: `d = L⊕R; t = chi32(d⊕rk); (L',R') = (R⊕t, d)` — **measured 5.5u/round**,
5 rounds ≈ 27.5u. Per-round cost ≈ Feistel (F+~2 XOR vs F+~1 XOR) with faster per-round
mixing (full state through F every round). *Tension with the survey:* it lists LM as "buys
nothing" (no true orthomorphisms on 2^n blocks). The orthomorphism above is valid for the
XOR group — the survey's claim appears aimed at Z_{2^n}-addition LM; I keep the candidate
on the strength of the direct measurement, flagged as contested. Statistical risk: HIGH —
no linear layer in F; chi-only diffusion. **Verdict: live but speculative (§3.5);
S2 DIFF is the 10-minute falsifier.**

### 2.10 WIDE-128 internal state (Carlo's directive 1b)

Expansion is free — the instruction already has 128 input bits `(val, key)`. Wide rounds
are depth-efficient (parallel S-boxes: same depth at 128 as at 64 bits, ~2× diffusion/round).
**The killer is bijectivity of the 128→64 output projection** (hard requirement #1):
for a 128-bit permutation P, `val ↦ first64(P(val, k'))` is a 64→64 map that is *almost
surely not injective* for random P (birthday: 2^64 values into 2^64 bins collide with
probability ≈ 1−e^{−2^63} ≈ 1). Injectivity must be *designed and proved*, not hoped for.
Surviving patterns: (i) outer 64-bit Feistel with 128-bit-internal F — F need not be
bijective, but F sits on the serial critical path: expand (free) + 1 wide round (7.7u) +
compress (2u) ≈ 10u vs current 6.8u F ⇒ **killed: 6×10 = 60u**; (ii) 128-bit EM/SPN with a
*proved* injective half-projection — open design work, no candidate today.
**Verdict: analyzed and killed for round 22; the projection-bijectivity argument is the
durable lesson (revisit only with a proved-injective construction).**

### 2.11 Parallel branches vs serial chains (Carlo's directive 2a)

Measured depths: S1 3.7u, chi 3.5u, lin64 4.0u, XOR-combine 2.0u/level.
- Serial S1→chi→lin: 3.7+3.5+4.0 = **11.2u**
- 2-way parallel (parsplit-style): max(3.7,3.5)+2.0+4.0 = **9.7u** (saves 1.5u; validated statistically by r15)
- 4-way parallel: 3.7+4.0(combine tree)+4.0 = **11.7u** — *worse* than 2-way; the combine tree eats the savings.
**Rule: 2-way parallelism is the sweet spot; beyond it, XOR-combine depth dominates.**
This generalizes parsplit and bounds the hybridization track's parallel-F experiments.

---

## §3 — Concrete candidate specifications (structurally different from Feistel-6)

Notation: `rk_i = rotl64(k, 13·(i+1)) ⊕ ((i+1)·0x9E3779B97F4A7C15)` (our validated affine
schedule; 1 XOR level, parallel — not on the val critical path). All delays are estimates
from §1 measurements; single-round probes are pessimistic by ~0.5–1u/round vs chained
designs (cf. §1.2 #13).

### Candidate A — Wide SPN-4 (S1 + (3,11) linear) ★

```
x_0 = v
for i = 0..3:  x_{i+1} = L( S16( x_i ⊕ rk_i ) )
out = x_4
S16 = 16 parallel S1 4-bit S-boxes (bijective ✓)
L(x) = x ⊕ rotl64(x,3) ⊕ rotl64(x,11)  (bijective ✓, §1.3)
```
- Depth: 4 × 8.1u (measured round probe) ≈ **32.4u** (chained likely ~30u). ✓
- Area: ≈ 4 × 920 ≈ 3,700 cells ✓
- Diffusion: after S+L, each output bit ← ~12 input bits (3 nibbles); full 64-bit dependency after 2 rounds; rounds 3–4 are margin.
- Bijective per fixed key ✓ (S1 perm, L bijective, key XORs).
- Statistical risk: MEDIUM — 4-round SPN differentials (S2) and linear approximations (S1 LIN) are the known-thin spots; AES needs 4 rounds for full diffusion and we have exactly that.
- Falsification order: S2 DIFF (minutes) → S1 screen → S3. If S2 spikes, try SPN-5 (40.5u, over budget — likely killed) or add the fm-style final mixing.
- Variant: SPN-3 (23u) as the aggressive probe — expect S2 to kill it; the kill localizes the round-count threshold the way round 17 did for Feistel.

### Candidate B — Even-Mansour over χχ (EM-χχ-4) ★

```
P(x) = R_3(R_2(R_1(R_0(x)))),  R_i(x) = L( χχ_64( x ) )
E_k(m) = P( m ⊕ k ) ⊕ k        (single-key EM; two-key variant: P(m⊕k1)⊕k2)
χχ_64 = χ_31 ∥ χ_33 (+ λ corrections, §2.8); L = (3,11) linear
```
- Depth: 4 × ~6.5u + 2×2u (key XORs) ≈ **30u**. ✓ Key schedule cost = 0 (key used directly).
- Bijective ✓ (χχ bijective, L bijective — this is what unlocks EM; chi64 would fail here).
- Why EM: all 37u go to the public permutation; keying is two XORs. Orthogonal to every Feistel key-schedule experiment so far.
- Statistical risk: MEDIUM-HIGH — χχ is a 2025 primitive; its differential profile (≡ χ_31∥χ_33) is good on paper, but 4 rounds is thin and EM's single-key form has known related-key structure (irrelevant to our fixed-key bar, but note it).
- Falsification order: S2 DIFF → S1 → S3. Cheapest kill: S2 in minutes.
- Variant B2 (aggressive): replace L with a free rotation: `R_i(x) = rotl64(χχ_64(x), r_i)` — 6 rounds ≈ 6×3.0+4 = **22u**. Diffusion per round is weaker (3-bit local + reposition; full dependency needs 4 rounds: 3^4=81>64), so 6 rounds is the margin play. High risk, absurdly cheap — one S2 run.

### Candidate C — Keyed SPN-6 (S-box + permutation, no linear layer)

```
x_0 = v
for i = 0..5:  x_{i+1} = Π( S16( x_i ⊕ rk_i ) )
out = x_6
S16 = 16 parallel S1 keyed nibbles; Π = transpose wiring: new nibble j takes
bit b from old nibble (j+4b) mod 16  (free; each S-box's outputs spread to 4
distinct next-round S-boxes)
```
- Depth: 6 × 5.7u (measured stage probe) ≈ **34.2u** ✓ (5 stages = 28.5u variant).
- Bijective ✓. Key schedule: 384 key bits via rotations (1 XOR level, key→output path ≈ 35.2u ✓).
- The tradeoff vs A: no linear layer (saves 4u/round) but needs 6 rounds vs 4 (per-round diffusion 4 bits vs 12 bits). Different statistical profile — worth having both.
- Statistical risk: MEDIUM — 6-round keyed SPN with branch-4-equivalent diffusion; S2/S1 decide.
- Falsification order: S2 → S1 → S3.

### Candidate D — Correct Lai–Massey, 5 rounds (chi, no linear)

```
d_0 = L_0 ⊕ R_0   (input split v = (L_0, R_0))
for i = 0..4:  t_i = chi32( d_i ⊕ rk32_i );  (L_{i+1}, R_{i+1}) = (R_i ⊕ t_i, d_i)
out = (L_5, R_5)
```
Inverse: `d_i = R_{i+1}`, `t_i = F(d_i⊕rk)`, `R_i = L_{i+1}⊕t_i`, `L_i = R_{i+1}⊕t_i` ✓ bijective.
- Depth: 5 × 5.5u ≈ **27.5u** ✓ (chained likely ~25u).
- Full state passes through F every round (faster mixing/round than Feistel); the price is no linear layer.
- Statistical risk: HIGH — chi-only, no linear; S2 DIFF may spike exactly like the notr5/drop4 kills.
- Falsification order: S2 DIFF first (10 minutes). If it passes S2, it becomes very interesting (27u with full battery would dominate on delay).
- Note: survey contests LM ("no true orthomorphisms on 2^n blocks"); the σ above is valid for the XOR group — the measurement is the new evidence. Rank accordingly.

### Candidate E — Keyed Beneš-MUX + χχ interleave

```
for i = 0..10:  x = MUXstage_i(x, sw_i)      # 32 keyed 2x2 switches, Beneš wiring
                 if i mod 3 == 2: x = χχ_64(x)
out = x
sw_i = 32 switch bits from rotl64(k, c·i)    # 352 bits total
```
- Depth: 11×2u + 3×3.0u ≈ **31u** ✓. Bijective ✓ (MUX = wire perm for fixed key; χχ bijective).
- Honest assessment: the MUX stages are *linear* in the data — this is a 3-nonlinear-layer SPN whose "linear layers" are wire permutations (branch number 2). Differentially thin; S2 is likely to kill it. Its only virtue over C is novelty + the keyed routing (irrelevant to fixed-key stats).
- Statistical risk: HIGH. Falsification: S2.
- Rank: lowest of the five; build only if A–C all die at S2 (it tests whether keyed-routing + sparse nonlinearity can pass at all).

---

## §4 — Ranked build recommendation for round 22

| Priority | Candidate | Predicted | Why first |
|---|---|---|---|
| **1** | **A — Wide SPN-4 (S1+(3,11))** | ~30–32u | Best-understood parts (S1, (3,11) both validated), full-width diffusion, bijective, fits with headroom. The single most likely chassis change to beat Feistel-6. |
| **2** | **B — EM-χχ-4** | ~30u | Zero key-schedule cost, bijective chi-class layer *cheaper* than our chi (3.0u < 3.5u), orthogonal keying. B2 (rot-only, 22u) rides along for one S2 run. |
| **3** | **C — Keyed SPN-6** | ~34u | No-linear-layer SPN is a genuinely different statistical profile; if A's linear turns out to be the S2 problem, C is the fallback. |

Build D (correct-LM-5) as a cheap speculative fourth (one S2 run decides; 27u would be a breakthrough).
Build E only if A–C all fail S2.

**Explicitly not recommended:** literal Blink-64a (43u measured, §2.5), Gimli anything (77u/8r, §2.3),
Ascon-p (61u/6r, §2.1), Xoodoo (θ too deep, §2.2), forkciphers (structural mismatch, §2.4),
unbalanced Feistel (49u+ safe, §2.6), 128-bit internal state (projection bijectivity, §2.10),
4-way parallelism (combine-tree dominated, §2.11), Ascon-5 S-box anywhere (depth-inefficient, §1.4).

**Method notes for the builders:** (1) single-round probes read ~0.5–1u/round pessimistic vs
chained designs — re-measure full chains at S0; (2) χχ_64 must be reconstructed exactly from
Belkheyar et al. (proxy omits λ) before any claim beyond screening; (3) every candidate gets
the standard pipeline (xcheck → rtlcheck → S0 → S1 → S2(|z|) → S3 → S4 → Q1); (4) S2 DIFF is
the cheapest falsifier for all five — run it before any PractRand time.
