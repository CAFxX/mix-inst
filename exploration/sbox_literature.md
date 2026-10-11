# S-box literature — low latency / depth / classification

User-supplied reference list, 2026-10-05. Purpose: inform the `mix` S-box search
(Track B). Some titles noted from memory by the user; verify before citing.

Already covered by the 2026-10-05 survey report (~/workspace/research_notes/low-latency-sbox-survey-20261005-0522/report.md):
Midori, GJN17 depth tool, Stoffelen, Rasoolzadeh, Ullrich (AND gates),
Leander & Poschmann 2007 (16 optimal classes), Bilgin/De Meyer (AND-depth),
Sun et al. 2025 addendum.

## Classification and properties of 4-bit S-boxes

1. Leander & Poschmann, On the Classification of 4 Bit S-Boxes, WAIFI 2007.
   The 16 optimal affine classes.
2. Saarinen, Cryptographic Analysis of All 4×4-Bit S-Boxes, SAC 2011.
3. Zhang, Bao, Rijmen, Liu, A New Classification of 4-bit Optimal S-boxes…, FSE 2015.
   Splits the optimal S-boxes into 183 categories.
4. Biryukov, De Cannière, Braeken, Preneel, A Toolbox for Cryptanalysis:
   Linear and Affine Equivalence Algorithms, EUROCRYPT 2003.
5. De Meyer & Bilgin, Classification of Balanced Quadratic Functions, ToSC 2019(2).
   Rasoolzadeh cites both (4, 5) for equivalence testing; user gave the second
   title from memory — verify before citing.

## Depth, latency and area of S-box circuits

6. Rasoolzadeh, Low-Latency Boolean Functions and Bijective S-boxes, ToSC 2022(3),
   403–447. The key paper.
7. Jia et al., How Small Can S-boxes Be?, ToSC 2025(1).
   Finds 11 GE and depth 3 for optimal 4-bit S-boxes.
8. Sun et al., Addendum to How Small Can S-boxes Be?, ToSC 2025(2).
   Makes latency the primary search metric.
9. Stoffelen, Optimizing S-box Implementations for Several Criteria using SAT
   Solvers, FSE 2016 (ePrint 2016/198).
10. Lu et al., Pushing the Limits…. An area-optimal SAT tool.
11. Forced Independent Optimized Implementation of 4-Bit S-Box.
    Finds GE-optimal circuits under a fixed depth.
12. Boyar, Find, Peralta, Small low-depth circuits for cryptographic
    applications, 2019.

## Low-latency designs that choose S-boxes this way

13. Leander, Moos, Moradi, Rasoolzadeh, SPEEDY, ToSC 2021(4).
    Section 2 studies CMOS gate latency. Rasoolzadeh reports NAND and OAI are
    the best low-latency gates.
14. Borghoff et al., PRINCE, ASIACRYPT 2012.
15. Knežević, Nikov, Rombouts, Low-Latency Encryption, CHES 2012.
16. Banik et al., Orthros, ToSC 2021(1).
17. Belkheyar et al., BipBip, TCHES 2023(1).
18. Banik et al., Midori, ASIACRYPT 2015.
19. Wang et al., THF/Blink, ToSC 2025.
20. Banik et al., Dialga, ToSC 2025(4).
    User has NOT checked the S-boxes of (19) or (20).
21. uLBC (CiC). Coordinate-function construction with more precise delay
    computation.

## Target profile (expert recommendation, 2026-10-05, non-binding)

Lexicographic optimization objective for the `mix` S-box selection:

- Hard constraints: bijectivity, DU = 4, NL = 4, algebraic degree 3
  (optional hard), full coordinate dependency, plus whole-function
  security criteria from the fast battery (S1/S2 gates unchanged).
- Primary objective: minimum FORWARD critical-path delay, post-synthesis
  in the target cell library (Sky130), not abstract logical depth alone.
  (Two-level NAND depth does not guarantee minimum delay: gate sizes,
  fan-in, arrival times, loading, fan-out, routing all matter.)
- Secondary: area, power, fan-out, input capacitance.
- Tie-breakers: differential/linear branch numbers, boomerang uniformity,
  fixed-point/cycle structure — NOT on the same footing as DU/NL.
- DROP inverse implementation metrics entirely (latency, depth, area):
  `mix` never computes the inverse. Inverse cryptographic metrics (e.g.
  inverse degree) kept only if a specific reason requires them.
- Free optimization dimensions to search explicitly: output XOR constants
  (S⊕c preserves all relevant metrics) and input/output bit permutations —
  16 × 16 × 16 = 4096 variants per base S-box, all cryptographically
  equivalent but potentially very different circuits. Also search over
  output constants absorbed into surrounding logic/wiring.
- Whole-function caveat: single-S-box metrics (branch number, BU, fixed
  points) matter less than the complete keyed mixing function's avalanche
  behavior; the S-box operates on independent 4-bit chunks, so per-chunk
  nonlinearity does not automatically give cross-chunk diffusion.
- Notable datapoint: requiring every coordinate to be degree 3 pushed Jia
  et al.'s minimum to 14 GE / depth 8 (2/3-input basis) — the user's
  USER_SBOX1 reportedly achieves degree 3 everywhere with a 2-level NAND
  implementation, an unusual point on the crypto-quality ↔ latency Pareto
  frontier (verify independently, do not take on faith).
