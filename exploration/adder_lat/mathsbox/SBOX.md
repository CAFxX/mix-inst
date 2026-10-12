# MATH-SBOX: First-Principles 8×8 S-box and 64×64 Construction

**Method**: pure mathematics — truth tables, Walsh spectra, ANF as polynomials.
No gates, no netlists, no circuits. All results in
[`~/workspace/mix/exploration/adder_lat/mathsbox/`](~/workspace/mix/exploration/adder_lat/mathsbox/).

## 1. The 8×8 S-box S

**Construction**: `S(x) = C · inv(A·x + b) + d`, where `inv` is inversion in
GF(2⁸) = GF(2)[t]/(t⁸+t⁴+t³+t+1) (0→0), and (A,b,C,d) is a random affine
equivalence chosen by search (NOT the AES affine — independently found).

Affine parameters (rows as bitmasks, bit 0 = LSB):
- A rows: `0x42 0x76 0x51 0x45 0x16 0xa7 0x61 0x78`, b = `0x68`
- C rows: `0x79 0xab 0x1c 0x83 0x91 0x6c 0xaf 0x0b`, d = `0xbc`

Table `S` (256 bytes, row-major hex):
```
d5 31 b1 57 03 b4 c1 7f 5b 5d 6d 30 cc 48 e4 76
... (full table in S_table.npy)
```

### Metrics (all computed on the 256-entry truth table)

| Metric | Value | Target | Status |
|---|---|---|---|
| Bijective | yes (permutation) | yes | ✓ |
| NL (min over 255 components) | **112** | 112 | ✓ optimal |
| Algebraic degree | **7** | 7 | ✓ max |
| Differential uniformity | **4** | 4 | ✓ optimal |
| SAC max bias | 16 (counts in [112,144]) | AES-level | ✓ |
| BIC max bias | 16 | AES-level | ✓ |
| Influence | every output bit depends on all 8 input bits | full | ✓ |

NL/degree/DU are affine-invariant: **every** affine equivalent of inversion
achieves 112/7/4. The search (3000 random affines) optimized only SAC/BIC bias,
reaching AES-level (16/16). Perfect SAC (bias 0) is impossible in this class:
the "good mask" table shows mean 32/255 good masks per direction and empty
intersection over unit directions — a structural fact, not a search failure.

### ANF (for documentation; NOT a netlist)

Each component is a degree-7 polynomial with 111–139 terms. Degree
distribution per component (0..7): e.g. comp 0: `{0:1, 1:4, 2:15, 3:32, 4:39,
5:29, 6:14, 7:4}`. Full ANF supports in `S_anf.npy`.

### Mathematical notes

1. **GF(2⁸) subtlety**: 0x11b is irreducible but NOT primitive — 0x02 has order
   51, not 255. Log/exp tables are invalid; all field arithmetic uses
   Russian-peasant multiply + Fermat inverse (a²⁵⁴), verified against FIPS-197
   vectors (0x57·0x83=0xc1).
2. **Why inversion**: it is the unique (up to affine equivalence) known 8-bit
   construction simultaneously achieving NL=112, degree 7, DU=4.
3. Gold functions x^(2^k+1) give no 8×8 permutations (gcd(2^k+1,255)>1 for all k).

## 2. The 64×64 construction F

**Definition**: `F(x) = M · (S(x₀), S(x₁), …, S(x₇))`, where x_q are the 8 input
bytes, S is applied per byte (8 parallel lookups), and M is a 64×64 binary
matrix (vector/matrix over GF(2)).

**M from 8×8 Cauchy over GF(2⁸)**: C8[i,j] = 1/(x_i + y_j) with
x_i = 1..8, y_j = 9..16; each entry expanded to its 8×8 binary
"multiply-by" matrix. Full matrix in `M64.npy`.

### M verification

| Property | Result |
|---|---|
| MDS (all 12,869 square submatrices nonsingular) | ✓ 0 singular |
| Byte branch number | **9** (maximal) |
| Binary rank | 64 (invertible) |
| SAC condition: every row hits every byte-block | ✓ |
| Max row weight | 39 → **6 XOR levels** |

### F properties (derived mathematically)

- **Bijective**: S bijective + M invertible ⟹ F bijective.
- **64-input dependence**: every M row-block is nonzero (8×8 blocks are
  invertible) so each output bit uses all 8 S-boxes; each S-box output bit
  depends on all 8 of its input bits ⟹ **each of the 64 output bits is a
  function of all 64 input bits**.
- **Degree 7** (M linear preserves S's degree).
- **Component NL**: each F-component = XOR of 8 independent S-components ⟹
  max|W| = 32⁸ = 2⁴⁰ ⟹ NL = **2⁶³ − 2³⁹** per component.
- **SAC of F**: follows from SAC of S + M's row-block-nonzero property
  (each output bit XORs ≥1 fair avalanche coin per flipped input bit).
- **Statistical SAC/BIC**: measured by sampling in `eval_F.py`
  (2⁶⁴ exhaustive impossible).

## 3. Latency estimate (mathematical operations, NOT gates)

- **1 S-box layer** (8 parallel 8-bit table lookups — the nonlinear cost).
- **6 XOR levels** (M's max row weight 39 → ⌈log₂39⌉ = 6).

Total: **1 S-box + 6 XOR levels**. For comparison, one AES round is
1 S-box + MixColumns (~4-5 XOR levels) + ShiftRows (0) — structurally similar,
but this F achieves byte branch 9 (vs AES's 5) in a single linear layer.

## 4. Files

- [`sbox_math.py`](~/workspace/mix/exploration/adder_lat/mathsbox/sbox_math.py) — GF(2⁸), affine maps, metric functions (Walsh, Möbius, SAC/BIC, DU)
- [`affine_search.py`](~/workspace/mix/exploration/adder_lat/mathsbox/affine_search.py) — random affine search
- [`goodmask.py`](~/workspace/mix/exploration/adder_lat/mathsbox/goodmask.py) — good-mask table + impossibility analysis
- [`bias_search.py`](~/workspace/mix/exploration/adder_lat/mathsbox/bias_search.py) — max-bias minimization (background)
- [`diffusion.py`](~/workspace/mix/exploration/adder_lat/mathsbox/diffusion.py) — Cauchy M + verification
- [`eval_F.py`](~/workspace/mix/exploration/adder_lat/mathsbox/eval_F.py) — statistical SAC/BIC of F
- [`S_table.npy`](~/workspace/mix/exploration/adder_lat/mathsbox/S_table.npy) — the S-box (256 bytes)
- [`S_anf.npy`](~/workspace/mix/exploration/adder_lat/mathsbox/S_anf.npy) — ANF supports
- [`M64.npy`](~/workspace/mix/exploration/adder_lat/mathsbox/M64.npy) — the 64×64 binary matrix
- [`best_affine.pkl`](~/workspace/mix/exploration/adder_lat/mathsbox/best_affine.pkl) — affine parameters

## 5. Open points (for parent)

1. Statistical SAC/BIC of F (`eval_F.py`) was still running at write time —
   check `eval_F_out.txt`.
2. The 20k-trial bias search (background) may find SAC/BIC bias < 16; if so,
   `S_best.npy` supersedes `S_table.npy`.
3. PractRand on F requires a circuit or C implementation — out of scope for
   this math task.
4. Two-round variant (S–M–S–M) would square the component NL
   (2⁶³−2³⁹ → ~2⁶³−2¹⁹) at 2 S-box + 12 XOR levels, if needed.
