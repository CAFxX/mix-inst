# SOTA Leads Triage — 2026-10-05 Weekly Sweep → Directed Experiments

**Source:** `sota_leads.md` §2026-10-05 (10-topic parallel survey, primary-source verified).
**Context:** Frontier S = rasC2_0 (26.5u) / r22c (28.3u); 4-round pba19 SPN is the winning construction; S-box track is hot.
**Rule:** Every lead needs S0 + full batteries. Latency estimates are hand depth-models, not syntheses.

## Priority 1 — Direct drop-ins to the winning 4r SPN (run first)

### E1. Generalized ChiChi (b,b̂)_{31,33} as the nonlinear layer
- **Lead:** sota #1 (ToSC 2025/3, verified). New 64-bit instances at ~3u (same as known χχ_64), degree-2 forward, max DP 2^-33 / max LC 2^-31 per layer.
- **Experiment:** Replace the 16× 4-bit S-box layer in the 4r pba19 SPN with χχ^{(b,b̂)}_{31,33}. Keep P-box pba19b01, L=lin(3,11), golden ks.
- **Why first:** Same latency class as current S-boxes (~3u), far stronger per-round crypto. Direct swap, minimal new code.
- **Caution:** 4-round sketch is statistical-gates-only (cryptanalysis floor #13: ≤5 chi_chi rounds broken at 32-bit TBC). Declare exposure.

### E2. MRM linear layer replacing lin(3,11)
- **Lead:** sota #3 (ToSC 2026, ePrint 2025/1960, verified). Rotation+XOR-only, 2.6 XORs/bit, differential BN 12, linear BN 5.
- **Experiment:** 4r SPN with 16× rasC2_0-class S-boxes → 64-bit MRM instance (~2–3 XOR levels) → ^rk64.
- **Why:** Cheapest strong linear layer in the survey. Direct lin(3,11) replacement.

### E3. Per-round P-box variation (Dialga-style)
- **Lead:** sota #8 (ToSC 2025(4)). Cycling 4 different cell permutations beats the optimal single permutation; permutations FREE in hardware.
- **Experiment:** 4r SPN with distinct affine P-box per round (π_0..π_3), e.g. pba19/pba27/r22c-P plus one new. Also per-round rotation variation in lin layer (uKNIT §8.1: zero-cost differential improvement).
- **Why:** Zero hardware cost, confirmed heterogeneity thesis. Our P-boxes are already affine — just vary them.

### E4. SAT-optimized S-box circuits (lead 11a–c)
- **Lead:** sota #11. (a) Sun et al. 50–74% latency cut for LBlock-S0/Piccolo/SKINNY-64/RECTANGLE/PRESENT/TWINE; (c) Osvik–Canright bitsliced depth records (LBlock-S0 10→4, PRESENT 12→5).
- **Experiment:** Extract the optimized circuits, drop into 4r pba19 SPN, measure S0.
- **Why:** Feeds the winning S-box track directly. The rasC2_0 win proves S-box swaps move the frontier.

## Priority 2 — New structures (needs fresh analysis + batteries)

### E5. sTCPM linear layer
- **Lead:** sota #4 (ToSC 2024(4)). Differential + linear BN both 12 at 4 XORs/bit. Fixes CRYPTO-2023 twin-CPM's weak linear BN.
- **Experiment:** 4r SPN with sTCPM replacing lin(3,11). Compare vs E2 (MRM).
- **Why second:** Higher XOR cost than MRM (4 vs 2.6/bit). Run if MRM disappoints.

### E6. BenX GF(2) nibble-pair blocks
- **Lead:** sota #7 (arXiv 2609.31087, verified real). Nonlinear Benes: B(x,y)=(S(x)^T(y), S(x)^x^T(y)); ~2× Feistel diffusion per gate-depth; ~7u/round.
- **Experiment:** 8 parallel blocks + fixed shuffle per round, 4–6 rounds. Needs fresh DU/wide-trail analysis first.
- **Why:** Novel structure, but needs groundwork before batteries.

### E7. 2-round single-key EM over Blink-style SPN
- **Lead:** sota #6 (our synthesis; SAC 2025 tightness note). ~30u total, single 64-bit key.
- **Experiment:** P = 2-round SPN (~14u/call), E_k(x)=P(P(x^k)^k)^k. Full S1–S4 + PractRand.
- **Caution:** Provable side rests on shakier 2-round EM bounds. Flag.

## Priority 3 — Cheap but lower-leverage

### E8. Rotational-XOR diffusion in 6r Feistel F
- **Lead:** sota #9. 8 MDS-class 32-bit instances, |I|=5. Drop-in for x^rotl32(x,7)^rotl32(x,13).
- **Why P3:** Cheapest experiment, but Feistel track is 10u behind the SPN frontier.

### E9. BipBip core/shell alternation
- **Lead:** sota #10 (idea only; literal broken). Alternate full-mixing rounds with S-box-only rounds.
- **Why P3:** We're winning at 4r; adding rounds costs delay. Only if 4r hits a wall.

## Not constructions — methodology / guidance

- **uKNIT-BC GA framework (#2):** Replicate the GA-with-SAT/MILP-fitness methodology with OUR objective (S1 zero-rejection + ≤40u). Seed pool = live frontier. Separate track from E1–E9.
- **gSTK key schedule (#2):** Principled round-key derivation for 64-bit keys (XOR-only, precomputable). Evaluate vs golden ks.
- **Naito–Sasaki–Sugawara KAF bound (#5):** Round-floor guidance for EM. 5-round KAF sketch (~34u) is a P2 experiment, not P1.
- **DDT-singular-value (#12):** Derive eps(r) for our S-box + linear layer; quantitative LIN round guidance. Analytical, no batteries.

## Cryptanalysis floors — calibrate, don't panic

- **#13:** 4-round Blink-style SPN is distinguishable-adjacent (4r uncomfortable, 5r first defensible). **Tension with our 4r SPN frontier.** Our gates are empirical (PractRand 1GB, SmallCrush, S2 differentials) not cryptanalytic proofs. The 4r SPN passes all empirical gates; the floor says a dedicated cryptanalyst would want 5r. Record the tension; do not abandon 4r on theory alone.
- **#14–#19:** Bit-permutation SPNs need ≥7r; truncated differentials reach +4r beyond ordinary; integral distinguishers reach 9–12r (not in our gate list — add SAT division-property check per surviving candidate); 4r Feistel is the theoretical floor (our 6r is conservative); BCLR17 invariant screening at ≤4r for Blink-style tracks.

## Pipeline gaps to close (from the sweep)

1. SAT bit-based division-property search per surviving candidate (require UNSAT).
2. BCLR17 invariant-subspace + nonlinear-invariant screen at ≤4 rounds.
3. Automated differential-linear composition search (2r diff + 1–2r linear tail).
4. MILP truncated-differential search per candidate.
5. DDT-singular-value → pairwise-independence round guidance (#12).

## Rejected / duplicate (no action)

Per sota_leads.md: Twinkle-64 downscale (fabricated), SipHash, multiply-based hashes, lanehash, 4r Gimli, Rotational-ADD MDS, LTLBC full, Koala, uLBC-128, Gleeok literal, BipBip literal, STH/EDM/sirX, modular-addition EM, tweakable-LR. Duplicates: ChiChi baseline, Orthros idea, THF/Blink tables, Rasoolzadeh (superseded by #11a–c in part).
