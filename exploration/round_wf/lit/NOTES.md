# Wire-friendly P-boxes — literature notes (Phase A, 2026-10-04)

## 1. PRESENT pLayer (Bogdanov et al., CHES 2007)
- P(i) = 16·i mod 63 for i < 63, P(63) = 63. Regular, highly structured.
- Rationale (from the paper §4.2): hardware efficiency demands a linear layer with
  minimum transistors → bit permutation ("simple wiring"); regularity chosen for
  *analyzability* (clean security argument), not for diffusion optimality.
- Known cost: slow diffusion; bits 0, 21, 42, 63 are static (never permuted) —
  "hourglass" design. Diffusion weakness documented (truncated differentials).
- Wirelength view: P(i)=16i%63 has large stretches (e.g. i=4 → 64→1? no: 16*4=64 mod 63 = 1,
  stretch 3; i=60 → 960 mod 63 = 960-945=15, stretch 45). Nobody measured this —
  wiring was "free" in their cost model (GE count only).

## 2. GIFT PermBits (Banik et al., CHES 2017) + BOGI
- 64-bit permutation given as explicit table (see hal.science GIFT spec dump in
  search). e.g. P64(0)=0 — GIFT's permutation HAS fixed points (handled at cipher level).
- Rationale: "bit permutation is just wire shuffle and has no hardware area at all."
- BOGI paradigm ("Bad Output must go to Good Input", from "On the design of Bit
  Permutation Based Ciphers", ToSC 2020): co-design S-box + permutation — the
  permutation is chosen to route cryptographically weak S-box output bits to strong
  input positions of the next S-box layer. This is diffusion-driven permutation
  design, but the objective is cryptanalytic (differential/linear resistance),
  NOT physical (wirelength). BOGI is the closest prior art to "permutation with a
  purpose beyond diffusion", but its purpose is still security-only.

## 3. Minimum Linear Arrangement (MLA) / wirelength-driven placement
- Our proxy objective Σ|P(i)−i| on a linear 64-bit datapath is exactly MLA on a
  perfect matching (n=64, 64 edges (i, P(i))). MLA is NP-hard in general; the
  matching case is polynomial (assignment), but our extra constraints (single
  cycle, spreading) make it NP-hard again → heuristics justified.
- Standard heuristics: simulated annealing (state of the art for placement),
  spectral sequencing (Fiedler vector of Laplacian — good starting point),
  successive augmentation. We use SA with a tour representation (see solver notes).
- Key insight from placement literature: for a *matching*, min Σ|P(i)−i| without
  other constraints is trivial (identity, W=0) — ALL the difficulty (and all the
  wirelength cost) comes from the cryptographic constraints. I.e., wirelength is
  the price of diffusion; the Pareto frontier W-vs-spreading is the right object.

## 4. What's missing (the gap this track fills)
- No prior work found co-optimizing a cipher P-box for diffusion AND wirelength.
  Cipher designers price permutations at zero ("just wiring"); placement people
  never touch crypto constraints. The S5 P&R gate is where the bill arrives.
- PRESENT/GIFT chose permutations for analyzability / security (BOGI); wirelength
  was never an objective. Our contribution: Pareto-map W vs spreading under
  single-cycle + maximal-spreading constraints, and validate diffusion
  empirically (S2/Q1) rather than by security argument.

## Sources
- PRESENT: https://elhacker.info/Books/BOOKS%20PART%203/An_Ultra-Ligh_Block_Cipher(en)-.pdf (§4.2)
- GIFT: https://iacr.steepath.eu/2017/760-GIFTASmallPresentFullversion.pdf
- BOGI / bit-permutation design: https://iacr.steepath.eu/2020/680-OnthedesignofBitPermutationBasedCiphersTheInterplayAmongSboxBitPermutationandKeyaddition.pdf
- MLA survey: https://ilianaxn.github.io/papers/mla_survey.pdf
- GIFT-64 P64 table: https://hal.science/hal-04692191v1/document
