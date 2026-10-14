# SOTA Leads — Ultra-Low-Latency Mixer Primitives

Dated, append-only. Fresh targeted sweeps for new low-latency hash/mixer
primitives, lightweight-cipher results, and non-xorshift fast-diffusion ideas.

---

## 2026-10-01 — Round 6 opening sweep

### THF: Designing Low-Latency Tweakable Block Ciphers (eprint 2025/1314)
- 2025 paper with fresh unrolled-synthesis latency table (NanGate 45nm / 15nm, ASAP 7nm).
- 45nm minimal-latency: SPEEDY-6-192 2.54ns, PRINCE 2.63ns, MANTIS 3.28ns,
  QARMA-64 3.44ns, QARMAv2-7-64 3.53ns, Midori64 4.69ns.
- Blink's reflection structure: identical enc/dec circuits, multiplexers select
  key — relevant if we ever need invertible mixing cheaply.
- Lead: QARMAv2's tweak schedule and the 3-round keyed-hash round keys
  h1(t), h2(t) — cheap keyed mixing ideas.

### Orthros (Banik et al., 2021)
- Low-latency PRF: two keyed permutations, cancels the reversible-primitive
  design (no decryption needed). Directly relevant: our mixer need not be
  invertible — non-invertible low-latency PRFs are a valid design space.
- Lead: explore 2-permutation non-invertible constructions.

### SCARF (Canale et al., 2022)
- 10-bit block low-latency cipher for cache randomization. Only encryption
  latency matters (decryption parallelized elsewhere) — same asymmetric
  requirement as our 1-cycle forward-only mixer.
- Lead: ciphers designed with forward-only latency as the metric.

### ILEA (PRINCE variant)
- Adds Balanced Block Mixing (BBM) layers at input and output of PRINCE for
  diffusion. 25% latency cost.
- Lead: BBM-style input/output mixing layers as cheap pre/post-diffusion
  around an SPN core (alternative to xorshift64).

### wyhash / MUM (Wang Yi)
- Masked-MUM: MUM(A^secret, B^seed); two rounds pass all statistical tests.
  BUT: full 64-bit multiply ~40u alone in our flow — structurally incompatible
  with even the relaxed 0.9x bar. Rejected (again) for this project.
- Lead: none for ASIC; the "two rounds suffice" lesson suggests 2 strong
  nonlinear layers may beat N weak ones — supports deep-SPN direction.

### Haraka (AES-based)
- Optimized for AES-NI CPUs, not ASIC gate depth. Not relevant.

### Confirmed reusable (from earlier deep research)
- Blink depth-3.5 4-bit S-box, Midori almost-MDS matrix, chi-like layers,
  fixed bit-permutations as free wiring. Avoid MDS matrices and ARX adder chains.

---

## Design implications for Round 6
1. Non-invertible is fine (Orthros precedent) — don't pay for decryption structure.
2. Forward-only latency metric (SCARF precedent) — matches our 1-cycle requirement.
3. 2 strong rounds may beat N weak rounds (wyhash lesson) — but our LIN/DIFF
   gate is stricter than PractRand; verify empirically.
4. BBM-style layers (ILEA) worth testing as xorshift64 replacement.

---

## 2026-10-03 — Wide SOTA survey (deep research, 2019–2026 + classics)

Full report: `~/workspace/research_notes/low-latency-mixer-sota-20261003-1552/report.md`
(per-source notes in `notes/`). Headline: the strongest chassis change vs the
37u 6-round Feistel baseline is the **Blink-64a α-reflection SPN core**
(Wang et al., ToSC 2025, ePrint 2025/1314 — same paper as the THF tables):
5 rounds of a boolean-depth-3.5 involutory 4-bit S-box + Midori almost-MDS
matrix + free cell permutation, round keys by *slicing a long master key*
(zero key-schedule logic). Unrolled: 2.92ns @45nm vs PRINCE 2.63ns (~11%
slower than PRINCE, fastest TBC at comparable security) → est. ~35u unrolled,
inside the 37u budget. Source verified via core.ac.uk mirror of the ePrint.

### Ranked top-10 (why it could win / biggest risk)
1. **Blink-64a α-reflection core** (5-round SPN, no key schedule) — ~35u est.;
   risk: PractRand/SAC/BIC at 5 rounds untested; needs 448 key bits (fold to 128?).
2. **Even-Mansour over reduced-round Gimli SP-box** (8 rounds ≈ 25–30u;
   shallowest measured round anywhere: 47 levels/24 rounds unrolled, 715.9ps
   Intel 10nm) — key injection = 128 XORs; risk: 64-bit truncation of a 384-bit
   permutation needs diffusion re-validation.
3. **ChiChi nonlinear layer at 64 bits** (EUROCRYPT 2025) — whole-state χ-like,
   depth ~2/round but global; risk: no 64-bit instance exists, uncharacterized.
4. **Rasoolzadeh depth-3.5 class-1 4-bit S-box** (ToSC 2022) as drop-in round
   upgrade — concrete equations published; risk: incremental gain unless the
   chassis changes too.
5. **Twinkle-PRF "one fat call"** (CIC 2024; Twinkle-PA: 64-bit pointer+context
   → tag at 2.04ns @45nm, 2.75× faster than QARMA-64) — risk: Twinkle-AE mode
   already cryptanalyzed; PRF core needs a deep read.
6. **Nonlinear keyed Beneš network** (11 stages × keyed 4-bit S-boxes on Beneš
   wiring) — zero published prior art, guaranteed full diffusion in 11 shallow
   stages (~22u linear part); risk: no statistical track record at all.
7. **Xoodoo-χ 4–6-round EM core** — depth-2 nonlinearity, same family as our
   chi; risk: θ's XOR tree (depth ~4/round) less efficient than Gimli; 6 rounds
   borderline ~36u.
8. **uLBC logical-effort S-box search** (CIC 2024) — better delay metric than
   boolean depth for our "u" calibration; methodology only.
9. **uKNIT roundwise-heterogeneous rounds** (ePrint 2024) — strong S-box rounds
   alternating cheap chi rounds; framework only.
10. **BipBip-style wide nonlinear key injection** (CHES 2023) — already broken
    (DS-MITM, ToSC 2024); highest risk.

### Honest negative results (do not pursue without new evidence)
- No established pure-xor/shift/rotate 64-bit finalizer is PractRand-clean
  (linearity provably fails binary-rank; every famous finalizer — fmix64,
  splitmix64, xxHash3, mx3, komihash — uses 64-bit multiplies, excluded).
  Multiply-free + addition-based passers (jsf64, sfc64) use 64-bit adds —
  conflicts with no-long-adder-chains.
- Full Ascon-p / Xoodoo / Keccak-f unrolled exceed 37u; only reduced variants
  debatable (lose cryptanalysis backing).
- Forkciphers (win = two outputs for one prefix — useless for single output),
  Lai–Massey (no true orthomorphisms on 2^n blocks), MISTY recursion,
  unbalanced Feistel: no demonstrated 64-bit latency win at this target.

### Reference layer stack (delay arithmetic)
depth-3.5 S-box + almost-MDS binary matrix (XOR depth 2) + free permutation
+ key XOR ≈ 6.5–7u per SPN round → 5 rounds ≈ 35u. Matches Blink-64a's
measured 2.92ns @45nm vs PRINCE 2.63ns.

### Gaps / unverified
- Twinkle-PRF internals not read in depth; uKNIT-BC parameters not opened;
  IoVCipher paywalled; Gimli-at-64-bits diffusion needs recomputation;
  ChiChi at 64 bits = new design work; eprint.iacr.org 403'd (mirrors used).

---

## 2026-10-03 — Analytical reference-text pass (complements the web survey above)

Full note: [`exploration/sota_analytical_designs.md`](sota_analytical_designs.md). Method: per-layer depths **measured** in the
pinned Yosys-0.69 flow (XOR2=2u — the survey's ~1u/XOR assumption is optimistic by ~2× on
XOR-heavy paths), not estimated. Key corrections to the survey's numbers:
- Literal 5-round Blink-64a = **43u** measured (8.6u/round), NOT ~35u — killed as specified;
  4-round Blink-style variant (34.4u) survives.
- EM-over-Gimli: SP-box measures **9.6u** (sequential x→y→z dependencies); 8 rounds ≈ 77u.
  The survey's "25–30u" does not reproduce — killed pending its source.
- Ascon 5-bit S-box = 6.2u (worst depth-per-bit in §1.4); Ascon-p ≈ 61u/6r — killed.
- **New finding:** ChiChi (Eurocrypt'25) χχ_64 proxy measures **3.0u and is bijective** —
  shallower than our chi64 (3.5u, non-bijective); unlocks Even-Mansour/SPN chassis.
- Killed with arithmetic: unbalanced Feistel 48:16 (49u+ safe), 128-bit internal state
  (output-projection bijectivity), 4-way parallelism (combine-tree dominated), forkciphers.
Top build recommendations for round 22: (1) wide SPN-4 S1+(3,11) ~30–32u; (2) EM-χχ-4 ~30u;
(3) keyed SPN-6 ~34u. Speculative: correct-LM-5 ~26u.

---

## 2026-10-05 — Weekly sweep (10-topic parallel survey + primary-source deep reads)

Method: 10 workers (one per topic), 10/10 complete, no failures. Verification:
eprint.iacr.org/2025/2119, eprint.iacr.org/2025/1960, arxiv.org/abs/2609.31087
opened and read; ToSC 2025/3 "Generalizations of ChiChi" read in full
(verified real, DOI 10.46586/tosc.v2025.i3.800-826); uKNIT-BC (ToSC 2026(2),
10% faster unrolled than PRINCEv2, 64-bit block) confirmed via IACR news +
diva-portal record. Spot-verification caught one worker hallucination
(Twinkle-64 "downscale" — see Rejected below). All latency estimates are
hand depth-models, not syntheses; every lead needs S0 + full batteries.

### NEW — actionable, fits ~40u, bijectivity compatible

1. **Generalized ChiChi (b,b̂)_{31,33} 64-bit instances** (Andreoli–Leander–
   Piccione–Stennes, ToSC 2025/3; ref impl github.com/samuele-andreoli/
   chichi_generalizations; VERIFIED via full PDF read). Extends our known
   χχ_64 (3.0u, bijective) to new 64-bit instances at the same latency —
   degree-2 forward (single AND level), inverse degree 32 proven, and the
   (b,b̂) swap variant has near-ideal key-recovery resistance (no inverse
   component independent of more than 2 input bits). Attacks: **latency +
   DIFF/LIN** (max DP 2^-33, max LC 2^-31 per layer — far stronger per round
   than 4-bit S-box layers). Sketch: 4-round 64-bit SPN: χχ^{(b,b̂)}_{31,33}
   (~3u) → L64 y_i=x_{3i+1}^x_{3i+26}^x_{3i+50} (~4u, rank-test pending) →
   ^rk64 (~2u); rk_i=K^rotl64(K,16i+7)^C_i; est ~36–38u; all-bijective ⇒
   val→output bijective per fixed key. CAUTION: cryptanalysis floor (below)
   shows ≤5 chi_chi rounds broken at 32-bit TBC settings — 4-round sketch is
   statistical-gates-only, cryptanalytic exposure declared.
2. **uKNIT-BC + uKNIT GA design framework** (Hu–Khairallah–Peyrin–Tan, ToSC
   2026(2); VERIFIED via IACR news/diva-portal). 64-bit heterogeneous SPN,
   12 rounds, every round a different 4-bit S-box + sparse 64×64 linear
   layer (~1 XOR depth) + ShiftRows; unrolled latency ~10% BELOW PRINCEv2
   (TSMC 65nm 1.49ns vs 1.65ns), −17% area, designers' best attack 10/12r.
   Attacks: **latency + LIN/DIFF**. Bigger lead is the methodology: GA
   knitting cipher round-by-round with SAT/MILP cryptanalysis + real
   synthesis as the fitness function — repluggable with OUR objective
   (zero-rejection S1 + ≤40u cap). Also **gSTK key schedule** (same paper)
   generalizes STK to bit-oriented ciphers — principled round-key
   derivation for 64-bit keys (XOR-only, precomputable). Sketch: replicate
   framework; seed pool = live frontier; mutations = per-round S-box/linear
   swap (S1/Sb0/Orthros/Rasoolzadeh pool); fitness = S1 zero-rejection +
   ≤40u.
3. **Multiple Rows Mixers (MRM)** (Yu–Liu, ToSC 2026 v2025.i2.166-191;
   ePrint 2025/1960; VERIFIED via ePrint page + abstract). Rotation+XOR-only
   linear layer: 5×64 instance has differential BN 12, linear BN 5 at only
   **2.6 XORs/bit**; extensible to arbitrary dims (64-bit derivable). Attacks:
   **diffusion-per-round + latency**. Sketch: 4-round 64-bit SPN —
   16× S1-class S-boxes → MRM layer (~2–3 XOR levels, ~4–6u) → ^rk64;
   est ~36–40u; bijective per fixed key.
4. **Symmetric twin column parity mixer (sTCPM)** (Lei et al., ToSC 2024(4)).
   Fixes CRYPTO-2023 twin-CPM's weak linear BN: row cyclic shifts give
   differential AND linear BN both 12 at 4 XORs/bit. Attacks: **LIN +
   diffusion-per-round**. Sketch: 4-round 64-bit SPN (S-box → sTCPM ~3 XOR
   levels → key XOR), plausibly ≤40u; or drop into current 6r Feistel F
   replacing x^rotl32(x,7)^rotl32(x,13). Source-reported; needs own trail
   check vs original Gaston (CRYPTO 2023, BN 12 at 3–3.34 XORs/bit).
5. **Naito–Sasaki–Sugawara CRYPTO 2025 tight mu-security bound for
   single-permutation key-alternating Feistel** (LNCS 16004, pp.404-436;
   bound verified via IACR cryptodb abstract, full text paywalled). Direct
   round-floor answer for EM-at-64: n=64 → r=3:32b, r=4:42.7b, r=5:48b,
   r=6:51.2b provable mu-security. Attacks: **security-margin /
   latency**. Sketch: 5-round KAF over 64 bits with ONE public 64-bit P
   reused per round, (r-2)-wise independent subkeys; ~5×(S-box+linear+keyXOR)
   ≈ 34u est. Bijective per fixed key. Proof assumes ideal P — own
   cryptanalysis required.
6. **Two-round single-key EM over a LIGHT 2-round Blink-style SPN**
   (our synthesis; reopened by Andreeva–Bhati–Weninger SAC 2025 tightness
   note ePrint 2025/1543, which weakens the textbook 2-round-EM 2^{2n/3}
   attack story). E_k(x)=P(P(x^k)^k)^k with P = 2-round SPN
   (S-box layer ~3.5 + nibble perm + almost-MDS matrix), ~14u/call → ~30u
   total, bijective per fixed key, single 64-bit key. Attacks: **latency**.
   Needs S1–S4 + PractRand; provable side rests on shakier 2-round EM
   bounds — flag.
7. **BenX nonlinear Benes block → GF(2) adaptation** (Campa et al., arXiv
   2609.31087, submitted 2026-09-25; VERIFIED real). First published
   invertible nonlinear Benes block: B(x,y)=(f0(x)+f2(y), f1(x)+f3(y)) with
   f2=f3, f0−f1 a permutation polynomial; transforms BOTH branches per
   application ⇒ ~2× Feistel diffusion per gate-depth. Published instance
   is F_p/ZK-oriented (REJECTED as-is); the transferable part is the block
   structure. Attacks: **latency / diffusion-per-round**. Sketch (our
   synthesis, needs fresh DU/wide-trail analysis + batteries): GF(2)
   nibble-pair blocks B(x,y)=(S(x)^T(y), S(x)^x^T(y)), S,T bijective 4-bit
   S-boxes; 8 parallel blocks + fixed shuffle per round; ~7u/round
   (S-box + 3 XOR levels); 4–6 rounds plausible ≤~35u.
8. **Dialga multiple cell permutations** (Banik et al., ToSC 2025(4)).
   Independent confirmation of the heterogeneity thesis: cycling 4
   different bytewise cell permutations across rounds (period 4) beats the
   optimal single permutation — 64 active S-boxes, full diffusion still
   3 rounds fwd/bwd, ~half QARMAv2 unrolled delay. Permutations FREE in
   hardware. Attacks: **diffusion-per-round + latency**. Sketch: 4-round
   64-bit SPN, round = π_i ∘ M ∘ S with distinct π_i per round and
   per-round bit-permuted 4-bit S-box (Midori-Sb0 class ~3.0u). Also
   **per-round rotation variation** (uKNIT §8.1: SPECK-32 per-round
   rotations improved 5r differential 2^-9→2^-12 at ZERO latency cost) —
   stealable into 6r Feistel F: replace fixed (7,13) with per-round
   (a_i,b_i) from SAT/MILP bound maximization.
9. **Optimal rotational-XOR diffusion primitives** (ToSC "Direct
   Construction of Optimal Rotational-XOR Diffusion Primitives"; exact
   8 offset sets not extracted — gap). 8 MDS-class 32-bit instances with
   |I|=5 vs our x^rotl32(x,7)^rotl32(x,13). Attacks: **diffusion-per-round**.
   Sketch: drop-in replacement in current 6r Feistel F; same shape
   (2 rotations + 2 XORs/word, rotations free wiring); latency unchanged
   (~41u). Cheapest experiment of the set.
10. **BipBip core/shell round alternation** (Belkheyar et al., TCHES 2023;
    literal 24-bit instance full-round broken by DS-MITM ToSC 2024 —
    idea only). Alternate full-mixing rounds with S-box-only rounds
    (e.g. F,S,F,S) for the 64-bit mixer; heterogeneity buys
    diffusion-per-round at zero extra cost on the S-rounds. Attacks:
    **latency**. Sketch: 6–8 round mixer, alternate; validate diffusion
    and gates empirically. Bijectivity preserved.
11. **New latency-optimized 4-bit S-box components** (all NEW, feed the
    S-box track): (a) Sun et al. latency-complexity SAT-optimized circuits
    for LBlock-S0/Piccolo/SKINNY-64/RECTANGLE/PRESENT/TWINE (ePrint
    2025/961) — 50–74% latency cut vs prior best in TSMC 90nm;
    (b) Jia et al. joint crypto+implementation SAT tool with proven floor
    (min area of optimal 4-bit S-box = 11 GE at depth 3 with 4-input gates;
    ePrint 2025/386) — point it at involutory/no-fixed-point/degree-3 boxes
    minimizing latency complexity; (c) Osvik–Canright new bitsliced
    depth records: LBlock-S0 10→4, PRESENT 12→5 (ePrint 2024/1076);
    (d) uLBC logical-effort 4-bit S-box coordinate construction (CiC
    2025; concrete table NOT yet extracted — gap).
12. **Beyne–Leander–Schutt DDT-singular-value pairwise independence**
    (EUROCRYPT 2026; ePrint 2025/1495). Proof technique, not construction:
    derive eps(r) for OUR 4-bit S-box layer + linear layer from DDT
    singular values and read off the round count where pairwise
    independence hits noise floor — quantitative LIN round guidance.
    Attacks: **LIN (round guidance)**.

### NEW — cryptanalysis floors / caution data (calibrate round counts, not constructions)

13. **4-round Blink-style SPN is distinguishable-adjacent**: half-cipher
    active S-boxes 1/2/4/7/16/23/30/35/38 for rounds 1–8 (THF ePrint
    2025/1314); with DP 2^-2 boxes, 4 rounds ⇒ best characteristic ≤2^-32
    before clustering; impossible-differential and division-property
    trails reach 7 rounds. Conclusion: 4-round Blink-style SPN uncomfortable;
    5 rounds first defensible SPN point. Attacks: DIFF / ROUND-FLOOR.
14. **Bit-permutation SPNs (GIFT/PRESENT-class) need ≥7 rounds**: min active
    S-boxes GIFT-64 r=1..9 → 1,2,3,5,7,10,13,16,18; 4-round characteristic
    ≥2^-10 — trivially distinguishable. Directly bounds the wire-friendly
    P-box track. (GIFT-64 19-round boomerang distinguisher validated —
    clustering/boomerang extend reach ~1.4× differential.)
15. **ChiLow/ChiChi cryptanalytic floor**: ≤5 chi_chi rounds broken at
    practical cost (cube/integral key recovery on ChiLow-32: 5r at 2^32
    decryptions; 6r at 2^68/2^33; 7/8r MitM + DL); 6 rounds absolute floor
    and already cube-distinguishable (5 papers 2025–2026: ePrint 2025/1601,
    2025/1581, 2025/1806; ToSC 2026(1) ×2). Tensions with lead 1's 4-round
    sketch — declare statistical-gates-only justification.
16. **4-round Feistel with strong F is the theoretical floor** (Luby–Rackoff
    / Maurer et al.): 3r = CPA-PRP, 4r = strong PRP assuming PRF round
    functions, ≤2^32-query cap at 64 bits. Our 6r Feistel is conservative;
    our gates (≤2^30 words) sit below the 2^32 bound — consistent.
17. **Truncated differentials reach ~4 rounds beyond ordinary
    differentials** (QARMAv2-64: first valid single-tweak truncated attacks
    at 10–11 rounds, ePrint 2023/1449) — our truncated-χ² DIFF gate is
    well-aimed; ordinary-differential round floors understate its reach.
18. **Blink reduced-round structural caution** (Chen–Guo–Zhang ToSC 2026(1)
    weak-tweak-key via Superbox; Beyne IACR news 2026-04-01 nonlinear
    invariants in 2-round Blink, partial key recovery 2^23 on 2^-96
    weak keys): at 2–4 rounds the binding constraint is structural, not
    probabilistic. Fixed key per table blunts the tweak angle, but add
    BCLR17 invariant-subspace + nonlinear-invariant screening at ≤4 rounds
    for the live 4-round Blink-style SPN track.
19. **Integral/division-property ceilings for 64-bit SPNs** (Hebborn et al.
    HAL-04692191): integral distinguishers reach 9–12 rounds (SKINNY-64
    12/13, GIFT-64 10/12, PRESENT 9/13) — deeper than differential/linear.
    THF found 7-round division trails in Blink-64. Integral is not in our
    gate list: add SAT division-property check to the candidate pipeline.

### Pipeline-gap recommendations (new screens proposed by the sweep)

- SAT bit-based division-property search at full round count per
  surviving candidate (Todo/SWW models; require UNSAT).
- BCLR17 invariant-subspace computation on round-constant differences +
  nonlinear-invariant screen at ≤4 rounds.
- Automated differential-linear composition search (2r diff + 1–2r linear
  tail) — Schwaemm/Alzette evidence (Cybersecurity 2026) shows 4-round
  64-bit structures fall to DL at ~2^10 data; analogical for SPN but worth
  adding.
- MILP truncated-differential search per candidate (expect reach ≈
  ordinary-differential reach + 3–4 rounds).
- DDT-singular-value → pairwise-independence round guidance (lead 12).

### REJECTED (fabrication caught, plus literature verdicts)

- **Twinkle-64 "downscale" — FABRICATED by a sweep worker**: claimed a new
  ePrint 2025/2119 design (5.5-round 64-bit EM SPN, 4×4×4 cube, ~18–25u).
  Verified against the actual ePrint page: 2025/2119 is a *major revision*
  of the SAME CIC 2024 Twinkle paper (1280-bit Twinkle-P, Twinkle-PA
  2.04ns @45nm). No 64-bit downscale exists. Original Twinkle-PRF remains
  area-infeasible (1280-bit state ≈ 20× our block). Lesson: every
  un-sourced latency/structure claim in future sweeps gets the same
  primary-source verification before entering sota_leads.md.
- SipHash family (no 2023–2026 successor; SipHash-1-3 unrolls ~8 sequential
  64-bit adders, ~100u+) — 64-bit-adder-chain dead end, re-confirmed.
- Multiply-based 2023–2026 successor generation (a5hash, prvhash,
  PolymurHash, HalftimeHash, polyxor, komihash/mx3/rapidhash class) —
  class rejection; Ahle (Sep 2026) adversarial collision witnesses
  (gxhash-64 seed-independent collisions, t1ha2-64 2^-30 pairs) add
  keyed-soundness failures on top.
- lanehash (2026), GxHash v3 — multiply/AES-based.
- 4-round Gimli EM (~38u) — designers' own trail weights: 2^-6 at 4r;
  dead on DIFF.
- Rotational-ADD MDS (ePrint 2025/1544) — adder chains, not low-latency HW.
- LTLBC full cipher (14r, 4.73ns unrolled = 1.8× PRINCE) — over budget;
  only its hybrid linear layer (2-round full diffusion) survives as an
  idea-only item, primary paper still paywalled.
- Koala (257-bit state), uLBC-128 (128-bit, 18r), Gleeok literal (12r × 3
  parallel branches; 7r key-recovery + Branch3 linear flaw per arXiv
  2512.04675 — chassis thin-margined, only the multi-branch-sum idea
  transfers), BipBip literal (broken full-round).
- STH/EDM/sirX sum-of-permutation PRFs — not bijective, fail the hard
  gate. Modular-addition EM whitening (CRYPTO 2025) — 64-bit adders exceed
  budget alone. Tweakable-permutation Luby–Rackoff — ≥4–6 permutation
  calls, over budget.

### DUPLICATE (already known / tracked)

- ChiChi/χχ_64 baseline (3.0u, bijective); Orthros 2-permutation idea;
  THF/Blink latency tables; Rasoolzadeh S-boxes (superseded in part by
  leads 11a–c); Gleeok/Orthros S4 box (baseline only); xorshift-family
  linearity evidence (Vigna; Lemire–O'Neill); wyhash/MUM multiply
  exclusion; QARMAv2 designers' distinguisher table (extends known QARMA
  line); QARMAv1 truncated-differential results (extends known);
  MANTIS-5 practical break (1980s-class caution); GIFT-64/PRESENT MILP
  tables are refinements of known bit-permutation floors.

## 2026-10-06 — ChainHash (Thomas Ahle) — keyed hash with proven collision bounds

Missed by the 2026-10-05 weekly sweep (completed 07:37:39Z; the feed item landed
2026-10-05T09:06:16Z; repo commits ~5 days old). Existence of the primary sources
verified 2026-10-06 via web search (repo `thomasahle/chainhash` is live); the deep
read is pending the next sweep — treat everything below as a lead, not a verified
claim.

- https://github.com/thomasahle/chainhash/blob/HEAD/docs/DESIGN.md
- https://github.com/thomasahle/chainhash/blob/HEAD/results/design/smhasher-survey.md
- https://github.com/thomasahle/chainhash/blob/HEAD/docs/THEOREM-128.md

Summary (from repo docs, not yet deep-read): 64-bit keyed non-cryptographic hash,
256-byte blocks over GF(2^64), carry-less bulk products (PCLMUL/VPCLMUL,
PMULL/PMULL2, EOR3), Horner block chaining in an independent key, integer twist +
quintic finalizer; collision bound stated as a theorem and machine-checked in Lean
(lean/README.md, lean/VERIFICATION.txt); SMHasher3 200/200 on x86-64 and arm64.
DESIGN.md measures three level-1 engine designs against the carry-less stage on
Xeon Platinum 8375C and M2 Pro, rejecting AES-round mixing and lo^hi/lo+hi folds
as fast-but-boundless (no almost-universal family, no root-count argument).

Why it matters for us:
1. Speaks directly to the 2026-10-06 directive (better mixing-quality metrics):
   ChainHash quantifies by algebra, not batteries — almost-universal families +
   root-counting bounds. The DESIGN.md lens "does this technique *admit a bound*?"
   is transferable to the predictive-metrics search: which of our structural
   metrics (active S-box bounds, diffusion rounds, avalanche distribution) have a
   theorem behind them, and which are theater.
2. The smhasher-survey's A/B/C/D classification (A: already used, B: no bound,
   C: unmeasured but bound-preserving, D: measured and rejected) is a methodology
   worth lifting for future SOTA evaluations.
3. Constructive counterpart to Ahle's adversarial witnesses (gxhash-64
   seed-independent collisions, t1ha2-64 2^-30 pairs) that the 2026-10-05 sweep
   already cites in the rapidhash-class rejection.
4. Cross-project note: carry-less GF(2^64) multiply is the primitive; of passing
   interest to raidjit's GF-multiply twin work (VGF2P8AFFINEQB).

Honest limits: different construction family (variable-length keyed polynomial
hashing, not a fixed 64-bit keyed SPN finalizer); nothing ports directly to the
mix chassis. Fold the deep read into the next sweep.


---

## 2026-10-12 — Weekly sweep (3-topic parallel survey, corrected round-8 frame)

**Judging-frame correction:** earlier briefs assumed r6_feist8_spn (86.5u) as
leader; mid-sweep the frame was corrected to
[r8_feist6_s1_1sbox_nw](fast_battery/candidates/r8_feist6_s1_1sbox_nw/) (round 8,
2026-10-02; evidence in [ROUND8_TABLE.md](round8/ROUND8_TABLE.md)): 6-round
balanced Feistel, F = single S1 4-bit S-box layer → `x^rotl32(x,7)^rotl32(x,13)`
→ `^rk32`, no input whitening; **42.9u = 0.414× the same-flow 64×64 multiplier
(bar 93.2u)**, 4,133 cells; S0–S4 clear plus Q1 (SAC/BIC at noise floor,
sac_z5=0). **~50u of headroom** under the bar. The binding question shifted
from delay to the *cryptanalytic margin* of a 6-round Feistel with a
single-S-box-layer F, and to chassis diversification (stronger F, same or
bigger margin, still ≪93u).

### NEW — actionable (judged against the 6-round Feistel / ~50u headroom frame)

1. **Leurent–Pernot rotation-XOR LBoxes** (ToSC 2024; VERIFIED via paper text +
   `Lbox-ToSC/lboxsearch` repo). **L32**: single-word 32-bit linear layer,
   **branch number 12 at 5 XORs + 5 rotations per word**, matching the best
   known [64,32,12] linear code (concrete instance in the paper's Algorithm 2).
   Why it matters: our F's diffusion is a 2-term rotation-XOR with a weak
   branch number — cryptanalytically thin; this is the denser-diffusion-per-
   XOR-level co-design target at ~3 XOR levels vs ~2 now. Gate: **LIN +
   diffusion-per-XOR-level**. Sketch: F = S1 layer (~3.5u) + L32 (~5–6u) +
   `^rk32` → ~9–10u/round; 6r ≈ 55–60u ≪ 93u. Fallback: L32×2 (Clyde-128's,
   BN 16, 6 XORs+6 rots/word) if F ever widens to 64 bits.

2. **ChainHash "integer twist" transfer** (Thomas Ahle; VERIFIED via the
   repo's DESIGN.md "Twist and finalizer" section + `results/64/suite/
   REPORT.md`). `v = V ⊞ tau`: one 64-bit integer add of an independent key
   word before the finalizer, breaking GF(2)-linearity between stages.
   ChainHash's own A/B: untwisted degree-5 circuit → 178/200 SMHasher3
   (failures exactly on Zeroes/Sparse/TwoBytes/Bitflip — affine second
   derivatives of pure-quadratic GF(2) maps); twisted → 200/200. Transfer:
   our 6r F is pure GF(2); the round-7/8 "whitening is pure cost" finding was
   XOR-whitening — integer-add twist is qualitatively different. Gate:
   **LIN / marginal algebraic structure**. Sketch: keep the 6r Feistel, add
   ONE 64-bit ⊞ of an independent key word as pre- or post-processing; est
   ~51–55u total, still ≪93u; bijectivity per fixed key holds (⊞ is a
   permutation). Untested — needs S0 + S1–S4.

3. **HILL — heuristic search for minimal-depth linear-layer circuits**
   (ToSC 2026; artifact repo with downloadable circuits: AES MixColumns
   270.4 GE at depth 3; 16×16 and 32×32 Hadamard matrices; VERIFIED via
   ToSC page + repo). Heuristic SLP search with an h-XOR area×depth metric.
   Our F's diffusion was hand-picked; HILL generates the depth-optimal
   32×32 binary matrix at fixed XOR depth. Gate: **delay + LIN/DIFF**.
   Methodology lead — direct plug-in to the F-function track; complements
   the "optimal rotational-XOR primitives" lead.

4. **MATTER — 3–6-round balanced Feistel with a public permutation as F,
   designed for low latency** (Avanzi–Dunkelman–Minematsu, ePrint 2024/1186;
   abstract VERIFIED). 512-bit Feistel, F = ASCON permutation keyed by
   round-key XOR, explicitly low-latency hardware. Design precedent that 6r
   Feistel + strong public F is defensible, and suggests the diversification
   move: replace our single-S-box F with a stronger public P (2-round
   Blink-style SPN, χχ-based) — ~50u headroom affords P≈10u/round → ≈60u
   total. Gate: **security margin**. Sketch: 6r Feistel, F(x) = P(x ^ rk_i),
   affine key schedule as now.

5. **MSX-64's strongly-universal 32-bit round function** (Minematsu et al.,
   CiC 2025, doi:10.62056/av11c3c2h; full PDF VERIFIED). F = 32-bit
   half-multiplication + modular addition ("without primes" UH à la Thorup):
   provably pairwise-independent ⇒ differential/linear probabilities at the
   information-theoretic minimum *by design*; bijective per fixed key for odd
   multiplier. 64-bit Feistel / 32-bit F = our exact chassis. Gate:
   **LIN/DIFF directly**. Sketch: F(x) = lo32(a·x) + b, per-round odd a,
   then rotation-XOR diffusion; 5r ≈ 65–80u fits **IF** a 32-bit
   half-multiplier synthesizes ≤ ~12–15u in the pinned flow — S0 decides.
   Caveat: SU proof assumes uniform random key; fixed-key behavior must go
   through S1–S4 (DFC-lineage attacks beyond the guarantee).

6. **Sonic/SuperSonic — gate-delay-balanced Feistel, asymmetric
   forward-optimized F** (2023; existence VERIFIED via mirror, spec not read
   in depth). All paths through F balanced for equal gate delay; inverse
   deliberately expensive — the forward-only latency metric (SCARF-style,
   matches our 1-cycle requirement) applied to Feistel. Transferable idea:
   for a forward-only mixer, F need not be cheaply invertible — opens
   non-bijective F's with better diff/linear profiles per gate-depth.
   Gate: **margin + diffusion-per-round**. Idea-only (no 64-bit instance);
   partial verification.

7. **CTET+ — 2-round tweakable SPN from a single secret S-box,
   beyond-birthday security** (ToSC; page VERIFIED). Transferable as a
   stronger F: 2-round "secret-S-box + nonlinear middle layer + independent
   round keys" beats S1+rotlXOR at similar depth. Gate: **LIN/DIFF**.
   Idea-only: needs a 32-bit instance designed from scratch; proof is in the
   RPM.

8. **Carry-less "binary MUM" Feistel F** (our synthesis; prior art CLHASH/
   Lemire 2016, ChainHash, polyxor — repos VERIFIED live). F(R) =
   low32(clmul32(R^a_i, R^b_i)): quadratic nonlinearity from XOR trees only
   (~10–12u/F), no integer multiplies, no adder chains. Feistel gives
   bijectivity for ANY F. Gate: **per-round DIFF/LIN**. Sketch: 6r balanced
   Feistel, independent 32-bit round keys; ≈60–72u < 93u. Caveat: pure-
   quadratic GF(2) maps have affine second derivatives (ChainHash measured
   this); battery decides; hybrid clmul+S-box variant breaks the quadratic
   structure. PROPOSED, not a published construction.

### NEW — cryptanalysis calibrations (the 6-round Feistel's margin, not its batteries)

9. **Özdemir–Rijmen: generic multidimensional-linear distinguishing reaches
   7 rounds** (ToSC 2026(1) pp. 376–409; ePrint 2025/2333; IACR news
   2025-12-31 — triple-attested; eprint.iacr.org 403s in this environment,
   noted). Type-2 GFC with t branches → distinguishing reach 2t+3 rounds;
   t=2 ⇒ **7 rounds** (key recovery 8). Round-function-agnostic; works with
   non-invertible F. Implication: our **linear margin = exactly 1 round —
   distinguisher-adjacent**. Caveat: data ≤2^64 at max reach, far above our
   ≤2^30 threat model — existence of key-independent linear hulls, not a
   practical break. Our LIN gate (binary-rank on consecutive outputs) is
   weaker than a full multidimensional-linear distinguisher → add a
   dedicated linear-hull screen (complements the DDT-singular-value lead).

10. **Maurer–Oswald–Pietrzak–Sjödin, "Luby-Rackoff Ciphers from Weak Round
    Functions?"** (ePrint 2006/213; full PDF read). With only-nCPA-secure
    round functions: 3r provably NOT CPA-secure; 4r CPA-secure in the
    quasirandom setting but not the pseudorandom one; 5r gives CCA in the
    quasirandom setting. KPA-only F unconditionally too weak. Our F (public
    single-S-box layer) qualifies for NONE of the positive results — the
    provable line contributes **zero** margin argument for 6r-with-weak-F;
    our margin case is empirical-only. Theory-backed margin direction:
    **heterogeneous F, stronger in middle rounds 2–5** (first round may be
    pairwise-independent; last needs only KPA security).

11. **Patarin, CRYPTO 2004: 5r CPA-2 minimal (4r CPA attacks exist at
    m ≥ O(2^{n/2})), 6r CPCA-2** (abstract verified verbatim via two mirrors;
    LNCS 3152). With ideal F, 6r sits exactly AT the CPCA floor, one above
    the CPA floor; with weak F the true floor is higher by an unquantified
    amount.

12. **Generic 5-round impossible differential for Feistel with bijective F**
    (Kühn 2001; verified text + independently re-derived: (α,0) ↛ (0,α),
    α≠0, over 5 rounds, miss-in-the-middle + F-bijectivity contradiction).
    Our F is bijective (S-box ∘ linear ∘ key XOR) → applies directly.
    **ID margin = exactly 1 round**; do not go below 6r without new evidence.

13. **MISTY1 falls to impossible-differential key recovery at 6 rounds**
    (Dunkelman–Keller 2008: 6r with FL at 2^51 CP; Kühn 2001: 6r without FL
    at 2^39 PT). 64-bit Feistel with F far stronger than ours still falls at
    6r. What saves our design is the threat model (fixed key, statistical
    indistinguishability at ≤2^30, no key-recovery goal) — not the round
    count. Document that restriction.

**Margin verdict:** 6 rounds is the cryptanalytic floor, not a comfortable
margin — three independent generic results put floors at 5r (CPA/random F),
5r (ID/bijective F), 7r (generic linear-distinguisher reach, 1 above us).
Two actionable consequences: (i) a 7th round costs ~7.15u/round → ~50u
total, still ≪93u — worth testing against S1–S4 (note:
r8_feist7_s1_1sbox_nw was S1-killed on LIN — whitening matters at 7r, so the
7-round test must keep whitening); (ii) strengthen the middle rounds first
if buying margin structurally.

### DUPLICATE (already tracked; re-judged against the round-8 frame)

- **ChiChi/χχ_64 as F's nonlinear part** — re-judged: strongest known
  per-round LIN/DIFF upgrade over a single S-box layer at ~3u; F ≈ χχ_64 +
  rotation-XOR ≈ 7–8u/round; ≤5r χχ cryptanalytic floor still declared.
- **sTCPM / MRM re-parameterized for the 32-bit F word** — new action nuance:
  derive 32-bit parameters via the papers' §7 text / parameter generators.
- **uKNIT heterogeneity + Dialga** — transferable nugget = zero-delay-cost
  per-round variation ((a_i,b_i) from MILP trail-bound maximization,
  per-round S-box classes).
- **Sun et al. SAT-optimized 4-bit S-box circuits** (TWINE 41 gates / depth 4 /
  0.17ns, Piccolo 0.16ns, …) as S1 drop-ins.
- **Rotational-XOR MDS family** as the dense-diffusion option (L32 now
  preferred: concrete instances published).
- **uLBC methodology** — concrete S-box table still not extracted (gap
  carried).
- **BipBip** χ-layer + core/shell round alternation (idea only); **BenX**
  GF(2) nibble-block adaptation (idea only); **Twinkle literal**
  (area-infeasible).
- Multiply/adder-chain class rejections re-confirmed (wyhash, xxHash3
  finalMerge ≈160u, rapidhash class, lanehash, GxHash v3, SipHash ≈100u+,
  jsf64/sfc64, Ahle's gxhash-64/t1ha2-64 witnesses).
- **ZIP-GIFT literal** — NEW but REJECTED (bijectivity gate + published
  key-recovery attacks, ePrint 2025/2291); retained as chassis-family
  evidence only.
- 2026-10-05 "5-round SPN chassis" leads (Blink-64a literal etc.) are now
  **obsolete as chassis** given the Feistel breakthrough — they remain
  F-function sources only.

### ChainHash deep-read closeout (deferred from 2026-10-06 — done)

DESIGN.md read in full. Confirmed: methodology-only value (the "does this
technique *admit a bound*?" lens + the A/B/C/D evaluation classification);
the construction ports nothing to our ASIC target — the finalizer is a monic
quintic over integers/GF(2^64) (three products + one add; the GF(2^64)
quintic is explicitly non-injective, failing the bijectivity gate;
~60–70u for the carry-less multiplies alone). The transferable primitive is
the integer twist (lead 2 above).

### UNVERIFIED / watch items

- **LLBC** ("A Novel Feistel-Based Low-Latency Block Cipher for IoT
  Applications", IEEE Internet of Things Journal 12(21):45583–45595, Nov
  2025) — Feistel-based low-latency cipher; paywalled, no ePrint mirror;
  existence VERIFIED via researchr.org only. Flag for follow-up.
- **NGCC candidate hashes** (`ngcc-dev/ngcc-harness`, repo VERIFIED live) —
  new hash designs with 64-bit-word XOR/rotation/S-box round functions
  (MoFang-BC: 3-bit S-box + MDS over GF(2^3) + rotations; ZC: chi+theta);
  no keyed 64-bit finalizer among them. Monitor for transferable F ideas.
- **Jia et al. "11-GE floor at depth 3"** (ePrint 2025/386) — number not
  located this sweep; the underlying ToSC 2025(1) SAT tool is real (cited in
  Sun et al.'s addendum).
- **Osvik–Canright bitslice depth records** (claimed ePrint 2024/1076) — not
  located; bitslice depth ≠ ASIC gate depth anyway.

### Method notes

3 parallel workers (ciphers / primitives / mixers+cryptanalysis), each
verifying claims against primary sources; mid-sweep frame correction to the
round-8 leader (earlier briefs carried the stale r6 winner). No new
fabrication incidents; unverifiable claims flagged UNVERIFIED. The prior
sweep's hallucination lesson (Twinkle-64 downscale, 2026-10-05) held —
spot-verification discipline unchanged.
