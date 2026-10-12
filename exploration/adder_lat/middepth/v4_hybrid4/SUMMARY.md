# V4 4-stage hybrid — Summary (2026-10-12)

## Verdict: TERMINAL (O147)

## Key findings

### 1. Cost model correction (critical)
The 4-term rotl-xor linear measures **5.5u**, not the 2.5u assumed in DESIGN.md.
- 5 operands (`x ^ 4 rotations`) require a 3-level XOR tree (genlib has only XOR2).
- 5.5u / 3 levels = ~1.8u per XOR2 level (consistent with V1/O146).

**Measured stage costs (S0, ref mul64 103.5u):**
| Stage | Cost | Cells |
|---|---|---|
| MUX2 layer (64x tt=0xac) | 2.0u | 64 |
| 4-term linear | 5.5u | 745 |
| 3-term linear | 4.0u | 174 |
| 2-term linear | 4.0u | 128 |
| Midori Sb0 layer | 3.0u | 179 |

### 2. All 4-stage options COST-DEAD
| Option | Structure | True cost | Budget |
|---|---|---|---|
| 1 | MUX2→4-term→MUX2→4-term | 15.0u | 9.0u (assumed) |
| 2 | S-box→MUX2→4-term→MUX2 | 12.5u | 9.5u (assumed) |
| 3 | MUX2→S-box→MUX2→4-term | 12.5u | 9.5u (assumed) |
| 4 | S-box→4-term→S-box→4-term | 17.0u | 11.0u (assumed) |

Killed on cost before building (escalation rule 1).

### 3. MUX2 substitution is not bijective
Structural collisions: when MUX data inputs coincide, the select bit is ignored.
Example: f(0x123456789abcdef0) = f(0x123456789abcded0) (differ only in bit 5).

### 4. 3-stage reconsideration: MUX2→4-term→MUX2
- **9.4u S0** (under 10u budget), 1311 cells.
- Bit-exact Python model (`model_hyb3.py`) and Verilog (`hyb3.v`).
- **Fisher CATASTROPHIC**: LIN D=4096/4096, DIFF |z|=739994.

### 5. S-box variant: S-box→P-box→MUX2-FF-keyed→P-box→S-box
- MUX2-FF-keyed: `y = x ^ mux(rotl(x,rs), rotl(x,ra), rotl(k,ck))` — keyed at no extra cost, bijective.
- Avalanche 4.6/64 (poor diffusion).
- **Fisher CATASTROPHIC**: LIN D=4096/4096, DIFF |z|=1.48e6.

## Files
- `mux2_layer.v`, `lin4.v`, `lin2.v`, `lin3.v`, `sbox4_midori0.v` — stage Verilog
- `hyb3.v` — 3-stage full Verilog (9.4u S0)
- `model_hyb3.py` — 3-stage Python model (bit-exact with hyb3.v)
- `model_hyb3b.py` — S-box variant Python model
- `triage_hyb3.py`, `triage_hyb3b.py` — Fisher triage scripts
- `s0_*/` — S0 measurement workdirs

## Conclusion
The 4-stage MUX2/4-term hybrid cannot reach <10u (4-term cost). The 3-stage
reconsiderations fit cost but fail Fisher catastrophically — 2 MUX2 layers
provide insufficient nonlinearity/diffusion for the Fisher bar.
