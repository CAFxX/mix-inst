# Peer Review: Statistical Validation Methodology for RV64 `mix` (SPN)

**Role:** adversarial auditor. **Verdict summary:** the core machinery is correct (I verified the highest-risk parts by brute force), findings (a), (b), (d) are **CONFIRMED**, (c) is **CONFIRMED with a statistical refinement** — but I found **one real effect the battery missed** (a per-bit coverage gap), plus a flag-threshold miscalibration. Details below.

---

## 1. Exact null distributions — VERIFIED CORRECT (highest-risk area)

I brute-forced the toy analog (W=2¹²) of both formulas against direct enumeration:
- `lemire_preimg` (tests_final.py:95): `ceil(hi·W/X) − ceil(lo·W/X)` — **0 mismatches** across 30 X values (incl. X=1, X=W−1, random X) and random [lo,hi) intervals. The ceil (not floor) is correct: `(s·X)>>k = r ⟺ r·2ᵏ/X ≤ s < (r+1)·2ᵏ/X`, and #{integers in [L,U)} = ⌈U⌉−⌈L⌉.
- `mod_preimg` (tests_final.py:102): **0 mismatches** across 28 y values.
- `lemire_np` object arithmetic (line 71): matches pure-Python reference for all battery X **including X=2⁶⁴−1**; no overflow.
- The `np.digitize(R.astype(object), ...)` path for X>1024 (lines 143–147): matches manual binning elementwise; boundary values land in the correct [lo,hi) bin.
- All expected counts ≥ 5 (min: 16 for low14-chi2; 64+ elsewhere). χ² normal approximation valid where used.

## 2. Verdicts on headline findings

**(a) SPN-8 fails catastrophically — CONFIRMED.** Independent repro (different N=2¹⁷, different keys): MSB fraction 0.483 on the battery's config (monobit z=−17.3); key=0xCAFEBABEDEADBEEF gives 0.516 (z=+11.6); the bias spans high bits with a gradient (bits 63→56: 0.516, 0.510, 0.504, 0.501…). Adversarial log: 39 flags, **all** SPN-8, coherent pattern (Lemire+monobit on sequential inputs), z up to +212 (p~10⁻⁶⁷). Rejection is unambiguous. Note: the weakness is **key-dependent** (key=0x1 is clean) — the report should say "some keys fail badly," not "all keys fail."

**(b) SPN-9 fails — CONFIRMED and extended.** I reproduced on the parent's key (z=+9.12 at N=2¹⁸) **and a second key** 0x123456789ABCDEF0 (lemire-X=10 z=+4.60, lemire-X=2 z=+11.35). One failing key disqualifies under "arbitrary key." The N-scaling argument (z growing ∝N for fixed bias) is the right test and was applied correctly.

**(c) SPN-10's single flag is a fluke — CONFIRMED, with a refinement that strengthens the conclusion.** The flag (mask-m=1, z=+4.49) has **df=1**, where |z|>4 ⟺ χ²>6.66 ⟺ **p≈0.01**, not 6×10⁻⁵. The battery contains 48 df=1 tests (lemire-X=2, mask-m=1 × 24 config-runs); P(≥1 such flag under the global null) ≈ **28%**. So the flag was statistically *expected*, not anomalous. The 16× follow-up (z=+0.21 vs ~+10.8 under a real bias) definitively kills it. **However** — see §4: my per-bit screen found a genuine small effect the battery missed, so "SPN-10 is clean" needs qualification.

**(d) BIC claims — CONFIRMED, with mechanisms nailed down.**
- *Murmur (1,34) ≈0.96*: reproduced independently (seed=2026, T=30000): joint (D1,D34) = {00:277, 01:14713, 10:14749, 11:261}, phi=**−0.964**. Mechanism: flipping input bit 0 flips bit 1 of the pre-final-xorshift state with p=**0.982** (near-deterministic differential — the real story); the final `h ^= h>>33` gives out[1]=h3[1]^h3[34], out[34]=h3[34], so Δout[1]≈¬Δout[34]. Real, structural, both bits live (p≈0.50).
- *SplitMix 1.00 on (3,34), flip bit 62*: reproduced: joint = {00:14983, 11:15017, 01:0, 10:0} — **perfect correlation**, both bits live at p=0.5006 (not degenerate; all 64 bits live). Mechanism verified elementwise: integer multiply diffuses differentials only upward, so pre-final differential support is bits ≥5 (Δz5[3]=0 always); final `z ^= z>>31` gives Δout[3]=Δz5[34]=Δout[34] identically. This also explains the parent's (5,36)/flip-63 pair (j, j+31 for j below the diffusion floor). Real and arguably worse than Murmur's.
- *SPN-10 ≤0.05 all input bits*: confirmed (0.024–0.030, at the noise floor ~0.043 expected max). The battery's BIC (flips only val bit 0) actually **understates** SPN-10's advantage; recommend max-over-all-64-input-bits as the BIC metric.

## 3. Methodology bugs (with line refs)

1. **[Minor] Flag threshold miscalibrated across df** (tests_final.py:218,225; tests_adversarial.py). `|z|>4` means p≈6×10⁻⁵ for df=1023 but p≈0.01 for df=1 (lemire-X=2, mask-m=1) and p≈0.0067 for df=2 (lemire-X=3, mod-3). Flag counts mix incomparable scales. Doesn't change any verdict, but the final report must flag in p-values, and "18 flags" should be reported as "17 with p<10⁻⁹, 1 with p≈0.007."
2. **[Moderate] Per-bit coverage gap in `seq_battery`** (line 110). No per-bit monobit screen on sequences: raw-monobit pools 64 bits (dilutes a single-bit bias 64×); lemire-X=2 sees only the MSB; low-bit χ² covers bits 0–13; lemire-X=2³²'s 1024-bin χ² dilutes a δ=0.003 single-bit bias to z≈0.05 (I computed this). **This gap hid a real effect** (§4). Recommend adding a 64-bit per-bit screen.
3. **[Minor] PART C single key** (line 60): one fixed key, paired across candidates (good) but no key diversity; adversarial battery doesn't repeat it.
4. **[Trivial] Stale docstring** (line 4): "takes ~10-20 min" — actual runtime ~1–2 min.

## 4. NEW FINDING (audit): SPN-10 small transient per-bit bias — bit 39

My per-bit screen (the coverage fix for bug #2) found a **real, key-dependent** bias the battery missed:
- Sequential inputs, N=2¹⁸: bit 39 z=−3.84 (key=0), −4.03 (key=0x2); 20-key screen: 3 keys with |z|>3 (keys 0, 2, 0x76a03c33175dc957); p≈2.6×10⁻⁵ under null → real.
- **Small**: δ≈0.002–0.004, ~6× smaller than SPN-8's MSB flaw.
- **Transient**: implied δ shrinks with N (key=0x2: −0.0039 → −0.0033 → −0.0015 at N=2¹⁸→2²⁰→2²²); concentrated in small-V region, washes out by ~2²⁰–2²¹.
- **Sequential-input-specific**: clean on stride-big (|z|≤0.96) and random (|z|≤1.53) inputs.
- **Crucial calibration — SplitMix64 shows the same phenomenon**: bit 31 transient on sequential inputs (z=+3.33, δ=+0.0033 at N=2¹⁸, washing out to z=+1.24 at N=2²²). Not SPN-10-specific.
- Practical impact for the use case is nil (Lemire/mask/mod reductions dilute it to undetectability), but it *is* a deviation from the literal "must pass for arbitrary key/I/j" requirement — a requirement SplitMix64 also fails. Honest claim: **parity-or-better vs baselines**, not literal universality.

## 5. Required disclosures for the final report

1. **Finite sampling, no proofs**: ~10–20 keys of 2⁶⁴; 6 X values; 5 y values; 1 key in PART C. Key-dependent weaknesses (SPN-8's, SPN-10's bit39) prove sampling can miss things.
2. **No standard batteries** (PractRand/Dieharder/TestU01) were run.
3. **Flag in p-values**, not raw z (bug #1); the SPN-10 mask-m=1 flag was a 28%-likely event, not an anomaly.
4. **Disclose the bit39 transient** with the SplitMix64 calibration — do not let "SPN-10 is clean" stand unqualified.
5. **BIC**: battery flips only val bit 0; full-sweep results favor SPN-10 even more strongly — include them.
6. **Untested**: key-sequenced inputs (varying key, fixed val); related-key behavior; X values beyond the 6 tested; y=2⁶⁴−1.
7. **Model/spec consistency verified**: rotations reduce mod 64; S-box/P-layer/round constants match isa_spec.md; scalar==vector==RTL on 3007 vectors (per parent).

**Bottom line:** the statistical methodology is sound where it matters (exact nulls verified, follow-up protocol correct), all four headline findings survive adversarial re-testing, and SPN-10 remains the right choice. But the battery needs the per-bit screen added, p-value flagging, and the final report must disclose the bit39 transient and the finite-sampling limits rather than claiming literal "passes for arbitrary key/I/j."