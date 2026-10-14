All measurements are in hand (24-key sweep: max|z|=2.91, zero flags). Compiling the final audit report.

---

# Peer Review: Cryptographic Soundness of the PRESENT-style SPN Mixer

**Method:** independent Python reimplementation from the S-box table only; DDT/LAT computed by brute force; branch number derived analytically and checked; key-schedule linear algebra solved via GF(2) Gaussian elimination; 24-key empirical sweep at 10 rounds (MSB bias, sequential inputs, N=2¹⁶); literature cross-check (PRESENT designers' bounds, Bonn lecture notes). I reviewed [`~/workspace/mix/spn.py`](../spn.py) and [`~/workspace/mix/isa_spec.md`](../isa_spec.md) §§3,5,7.

## 1. S-box analysis — computed from scratch (item 1)

S-box `S = [C,5,6,B,9,0,A,D,3,E,F,8,4,7,1,2]`, verified bijective (16 distinct outputs), no fixed points.

| Property | Measured | Published PRESENT value | Match |
|---|---|---|---|
| DDT max (Δin≠0) | **4/16 = 2⁻²** (24 entries attain it) | 2⁻² | ✓ |
| LAT max |bias| | **4/16 = 2⁻²** (36 entries at ±4) | 2⁻² | ✓ |
| Linear probability (max) | (2·2⁻²)² = **2⁻²** | 2⁻² | ✓ |
| Differential uniformity | 4 (optimal for bijective 4-bit S-box) | 4 | ✓ |
| Coordinate algebraic degrees | 2, 3, 3, 3 | 2,3,3,3 | ✓ |

The code comment in [`spn.py`](../spn.py) ("differential uniformity 4 (optimal for 4b), max linear bias 4/16") is **correct**.

## 2. Active-S-box bounds and what they buy (item 2)

- **Branch number of the pLayer w.r.t. nibble activity is exactly 2** (derived analytically: a bit-permutation maps a single set bit to a single set bit, so `wt(x)+wt(P(x)) = 2` is attainable, e.g. `x=1`). Naive wide-trail would give only ≥10 active S-boxes over 10 rounds.
- **Stronger, literature-backed bound applies:** the PRESENT designers proved **≥10 active S-boxes per 5 rounds** for differential characteristics ("any differential characteristic over 25 rounds must have at least 5×10 = 50 active S-boxes"; independently confirmed in Bonn lecture notes: "any five round differential characteristic in PRESENT must contain at least ten active sboxes"). The argument depends only on the S-box layer + pLayer, which are bit-identical here, and round-key XOR does not affect differences. Tiling two 5-round windows:
  - **Differential:** ≥20 active S-boxes over 10 rounds → any single characteristic has probability ≤ **(2⁻²)²⁰ = 2⁻⁴⁰**, for every fixed key.
  - **Linear:** same counting applies to masks → correlation ≤ **(2⁻¹)²⁰ = 2⁻²⁰** (bias ≤ 2⁻²¹) per characteristic. (Designers' own bound: bias ≤ 2⁻⁴³ over 28 rounds — consistent.)
- **What this rules out:** any differential/linear distinguisher or key-recovery-style attack requiring < ~2⁴⁰ data/work. For a hash-table finalizer this is far beyond any practical threat.
- **What this does NOT rule out** (must stay in the report): (a) the linear/differential **hull** exceeding the best single characteristic — the bounds are per-characteristic; (b) statistical biases detectable with 2²⁶–2⁴⁰ samples (we tested to 2²²); (c) structural effects of the key schedule or the `val⊕key` input whitening, which the characteristic model doesn't capture; (d) anything about 8/9 rounds — empirically broken, and the bounds never promised otherwise (at 8 rounds the bound allows characteristics up to 2⁻³², yet we *measured* Δp≈2⁻⁵·⁹ — proof the bounds are not predictive of statistical behavior at low round counts).

## 3. Key schedule audit (item 3)

`rk[i] = ROTL64(key, 13·(i+1) mod 64) ⊕ RC[i]`, `RC[i]=(i+1)·0x9E3779B97F4A7C15 mod 2⁶⁴`, `i=0..10`.

- **Structured keys** (0, all-ones, alternating, period-8, 0xDEADBEEFDEADBEEF): **no round-key collisions**; minimum pairwise Hamming distance 20–25/64 (healthy; random expectation 32).
- **Exact-collision weak keys:** for 14 of 55 round pairs `(i,j)`, there *exist* keys with `rk[i]=rk[j]` (solved `ROTL(y,d)⊕y = RC[i]⊕RC[j]` over GF(2) — linear system, checked consistency per pair). Each such class contains only **2–4 keys out of 2⁶⁴** (fraction ≤ 2⁻⁶²). Negligible for a non-cryptographic mixer; worth one sentence in the report, not a redesign.
- **Related-key resistance: none, by construction.** Round constants cancel: `Δrk[i] = ROTL(Δkey, 13·(i+1))`. A single-bit seed difference produces single-bit round-key differences at attacker-known positions `[13,26,39,52,1,14,27,40,53,2,15]`. This is fine *only* because the seed is a public per-map value with no related-key oracle — the spec must say "no related-key resistance by design" rather than "not analyzed."
- **Key-dependent statistics:** the 8-round failure mode (key=0 fails catastrophically, key=0xDEADBEEFDEADBEEF passes) is the signature of a **key-dependent linear/differential effect** — at 8 rounds the construction still "remembers" key structure. Consequence: at 10 rounds, "clean on K keys tested" is weaker evidence than the raw test count suggests, because an untested key could in principle be an outlier. My 24-random-key sweep at 10 rounds (MSB bias, sequential inputs, N=2¹⁶) gives max|z|=2.91, mean 1.09, zero flags — combined with the parent's 7 worst-case keys, ~31 distinct keys are clean. **Recommendation:** run ≥100 keys through the single cheapest discriminating test (MSB/LSB monobit on sequential inputs, N=2¹⁶, ~15 s per 24 keys) as a final gate before sign-off.

## 4. Round margin: 10 is adequate, not luxurious (item 4)

- Measured attenuation 9→10 rounds: worst observed bias went from Δp≈2⁻⁶·¹ (detectable, z=+29.6 at N=2²⁰, growing ∝√N) to undetectable at N=2²² — **>16× attenuation in one round**.
- If per-round attenuation stays ~4–16×, the residual bias at 10 rounds sits at or just below the N=2²² detection floor (≈2⁻¹⁰). Statistical margin is therefore **about one round of attenuation** — thin against a *hypothetical* determined statistical tester with N≈2²⁶, but the worst-case linear characteristic bound (bias ≤2⁻²¹, detectable only at N≈2⁴⁴) says no *characteristic-driven* bias can be near the floor. The honest summary: **large margin against practical exploitation (2⁴⁰ work), modest margin against statistical detection.**
- **What the sharp 8→9→10 transition suggests:** the dominant bias mechanism is a specific high-bias effect (consistent with a linear/differential hull concentrated in few rounds) whose attenuation-per-round crosses the detection threshold between rounds 9 and 10 — the classic "knee" of an SPN reaching sufficient active S-boxes. It does **not** suggest gradual, well-modeled attenuation; therefore "11 rounds would be safer" is plausible but unquantified, and the 10-round choice rests on **empirical testing, not on a proven bound**. Do not present 10 as theoretically derived.
- 9 rounds is definitively excluded (bias grows with N — a real defect, not a fluke). 8 rounds is excluded (MSB fraction 0.483, χ² z=+212).

## 5. Sentence-by-sentence claim review (item 5)

**[`isa_spec.md`](../isa_spec.md) §7 (Security scope):**
1. "`mix` is a **hash-map finalizer**, not a cryptographic primitive" — **PASS**.
2. "The key schedule … is chosen for hardware simplicity, not related-key resistance. Related-key differentials were not analyzed to cryptographic standards." — **WEAK PASS, reword.** "Not analyzed" understates a known-by-construction property. Replace with: *"The key schedule provides no related-key resistance by design: round constants cancel under seed differences, so Δrk[i] = ROTL(Δkey, 13·(i+1)) is fully attacker-controlled. This is acceptable because the seed is a public per-map value with no related-key oracle; the design must never be used where related-key security is required."*
3. "No claim is made about preimage resistance, collision resistance, or PRF security under adversarially chosen keys." — **PASS**.
4. Statistical-quality paragraph ("empirical, finite-sample measurements — not proofs of universal guarantees") — **PASS**. This is exactly the right framing; keep it verbatim in the final report.
5. "'ideal SAC/BIC/differential uniformity for all keys' is not claimed" — **PASS**.

**[`isa_spec.md`](../isa_spec.md) §3 (bijectivity):** "This holds for all keys by structural induction over the construction." — **PASS with nit:** replace "by structural induction" with "because each stage is a bijection and composition of bijections is a bijection." The 16-bit exhaustive check is correctly labeled supporting evidence. The claim itself is a valid proof.

**[`spn.py`](../spn.py) header:** "Full-cycle uniformity is therefore EXACT." — **PASS** (iterating all 2⁶⁴ inputs yields each output exactly once — true and legitimately claimed).

**Final-report requirements that must be explicitly scoped down** (for the parent's limitations section):
- *"Ideal SAC/BIC/uniformity/diffusion/nonlinearity/differential uniformity"* → **FAIL as stated.** Replace with: "Measured SAC mean |dev| ≤ 0.0063, BIC max|corr| ≤ 0.05, uniformity χ² |z| ≤ 1.1 (m≤14), all within noise of SplitMix64/Murmur3-fmix64 on identical tests. 'Ideal' is not claimed; several of these properties cannot simultaneously be literally ideal for a 64-bit permutation."
- *"Strictly not worse than any common software mixing functions"* → **FAIL as stated.** Replace with: "On the fixed comparison set {SplitMix64, Murmur3 fmix64} and the fixed battery in [`tests_final.py`](../tests_final.py), SPN-10 is no worse within statistical noise on every metric, and substantially better on BIC (0.044 vs 0.97/1.00 — both baselines have structural differential correlations from their final xorshifts). One exception: Murmur's value-SAC max|dev| (0.02686) is nominally better than SPN-10's (0.02783); the difference is inside sampling noise (σ≈0.0078)."
- *"For every key/value combination … arbitrary key, I, j"* → **FAIL as stated.** Replace with: "Tested on ~40 distinct keys, 6 input-structure families (sequential, strided, high-bits-only, random), N up to 2²² (4M samples), under raw/Lemire/mask/mod-y reductions with exact null distributions. Finite testing cannot certify all 2⁶⁴ keys × all strides; the claim is empirical coverage, not universality."
- *"Latency no higher than an adder"* → **FAIL as stated** (mutually exclusive with the multiplier target; a Kogge-Stone adder is ~4–5× faster than any adequate mixer). The report must carry the reconciliation: multiplier target is the achievable one.

## 6. Adversary capabilities — explicit (item 6)

Threat model: attacker knows the algorithm and the public per-map seed, controls hash-table input values (`val`), wants hash-DoS (many collisions) or prediction advantages. There is no secret.

**An adversary CAN:**
- Evaluate the mixer arbitrarily (it's public) and brute-force bucket collisions at the **generic rate** — ~y/2 evaluations per targeted mod-y bucket collision, ~2³² for a 50% 32-bit collision. No shortcut is known; bijectivity means full-output collisions are impossible.
- Exploit the trivial related-seed structure — but seeds are public, so this yields nothing beyond what the public seed already gives.
- In principle, distinguish the mixer from random with ~2⁴⁰ chosen pairs **if** the worst-case characteristic bounds are tight and exploitable — not practical, and no such distinguisher is known.

**It CANNOT be claimed that an adversary CANNOT:**
- Find *statistical* biases with >2²⁶ samples — the characteristic bounds don't preclude a large linear hull; "no bias detected at N≤2²² over ~40 keys" is the precise claim, not "no bias exists."
- Invert the permutation faster than generic 2⁶⁴ preimage search — no inversion shortcut is known, but "no shortcut is known" ≠ "proven hard" (it's not a one-way function by design; it's a public permutation).

**Bottom line:** the design is sound *for its stated purpose*. The cryptanalytic bounds (2⁻⁴⁰ differential / 2⁻²⁰ linear correlation per characteristic, key-independent) plus the empirical battery (10 rounds clean where 8/9 fail, baselines beaten on BIC) justify shipping **10 rounds** as a hash-map finalizer. The spec's §7 is already honest; apply the two rewordings above, keep the finite-sample disclaimer prominent in the final report, run the recommended ≥100-key sweep, and do not let the final report upgrade any "measured" to "proven" or any "no worse on the tested set" to "universally no worse."