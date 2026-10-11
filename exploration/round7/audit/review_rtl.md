# Independent RTL review: r7_feist8_s1_1sbox

**Reviewer stance:** adversarial — attempted to break bit-exactness, the S-box,
the key schedule, and the structure. Worked alone; read all source files
directly, did not rely on prior audit docs.

**Verdict: APPROVE** (no BLOCKER / MAJOR findings; three MINOR notes below).

## Scope

Design: RV64 `mix` candidate `r7_feist8_s1_1sbox` — 8-round Feistel,
val^key whitening, F(R,rk) = S1-nibble-layer → x^rotl32(x,7)^rotl32(x,13) →
^(rk low 32), one S-box layer per F, no final swap, out = {R,L}.

Files reviewed (read in full, line by line):
- Model: `~/workspace/mix/exploration/round7/models/r7.py`
  (`r7_feist8_s1_1sbox`; key schedule `_rk_np` imported from
  `round5/models/r5.py`, which re-exports it from
  `round4/models/r4_hybrid.py` — **read that definition directly**)
- C: `~/workspace/mix/exploration/fast_battery/candidates/r7_feist8_s1_1sbox/impl.c`
- RTL: `~/workspace/mix/exploration/fast_battery/candidates/r7_feist8_s1_1sbox/rtl.v`

Out of scope: statistical quality (S1–S4), synthesis delay numbers, P&R,
bijectivity proofs. This review covers implementation fidelity only:
RTL ≡ Python model, RTL ≡ C, plus structural RTL hygiene.

## Method

Toolchain: iverilog was **not** installed (contrary to the task note); installed
Icarus Verilog 13.0 from conda-forge into `~/tools/ivl-env`
(`~/tools/bin/micromamba create -y -p ~/tools/ivl-env iverilog`).
gcc (system), python3 + numpy 1.26.4.

All scripts kept in `~/workspace/mix/exploration/round7/audit/`:

1. **Bit-exactness sim** — `gen_vectors.py` builds 2139 vectors (2000 seeded
   random + edge cases: key=0, val=0, val=key=0, all-ones val/key, all 64
   single-bit val with key=0, all 64 single-bit key with val=0,
   alternating-bit patterns, 0x0123456789ABCDEF/0xFEDCBA9876543210) with
   expected outputs from `r7.py`, written to `vectors.hex`.
   `tb_rtl.v` drives the DUT combinationally and compares with `===`
   (strict: any X bit fails):
   ```
   cd ~/workspace/mix/exploration/round7/audit && python3 gen_vectors.py
   ~/tools/ivl-env/bin/iverilog -o sim_rtl -Wall \
     ../../fast_battery/candidates/r7_feist8_s1_1sbox/rtl.v tb_rtl.v
   ./sim_rtl
   ```
   Extended sweep: 20,000 more seeded random vectors (`vectors20k.hex`,
   model evaluated vectorized), same TB via `tb_rtl20k.v`.
2. **S-box / nibble order** — `check_sbox_rk.py` regex-extracts all 16 `case`
   entries from `rtl.v` and compares against `S1` from `r7.py`; checks the
   part-select pattern `t[4*j+:4] = sbox(R[4*j+:4])` (LSB-nibble-first) vs the
   model's `((x >> 4*i) & 0xF)` loop.
3. **Round-key schedule** — `check_sbox_rk.py` emits `rk_vectors.hex`
   (6 keys × rounds 1..8, expected = model's `_rk_np`); `tb_rk.v` calls the
   RTL's **actual internal function** hierarchically (`dut.rk(key, round)`)
   and compares.
4. **Structural** — line-by-line read of `rtl.v` + `iverilog -Wall` clean
   check for width/latch warnings.
5. **Mutation red-green** — copied `rtl.v` → `mut/rtl_mut.v` (original
   untouched), flipped one entry (`4'h3` output `4'h4` → `4'h5`), recompiled
   with the unchanged TB:
   ```
   sed -i "s/4'h3: sbox_feist8_s1_1sbox = 4'h4;/4'h3: sbox_feist8_s1_1sbox = 4'h5;/" mut/rtl_mut.v
   ~/tools/ivl-env/bin/iverilog -o sim_mut mut/rtl_mut.v tb_rtl.v && ./sim_mut
   ```
6. **C vs RTL** — `harness.c` links `impl.c` (`mix_hash`), checks the first
   301 rows of `vectors.hex` (all edge cases + ~290 random) against the
   model-derived expected values:
   ```
   gcc -O2 -Wall -Wextra -o check_c harness.c \
     ../../fast_battery/candidates/r7_feist8_s1_1sbox/impl.c && ./check_c
   ```

## Findings

### Exact key-schedule formula (established from code, all three artifacts)

- Model (`r4_hybrid.py`): `_rk_np(k, i) = rotl64(k, 13*(i+1)) ^ (((i+1) *
  0x9E3779B97F4A7C15) mod 2^64)`. `_feistel8_np` calls it with **1-based**
  round `i` = 1..8, so effective rotations are **26, 39, 52, 1, 14, 27, 40,
  53** — rotation 13 never occurs. (This is a consequence of reusing r4's
  0-based `_rk_np` with a 1-based loop; the r7.py docstring formula
  `rotl64(k,13*(i+1))` with i = round number is consistent with this.)
- RTL `rk(k, i)`: `r = (13*(i+1)) % 64`; `rc = (i+1) * 64'h9E3779B97F4A7C15`;
  `rk = ((k<<r)|(k>>(64-r))) ^ rc` (with an `r==0` guard). Called as
  `rk(key, i+1)` from a 0-based loop → rounds 1..8, identical values.
- C `rk(k, i)`: `rotl64(k, 13*(i+1)) ^ ((uint64_t)(i+1) * 0x9E3779B97F4A7C15ULL)`,
  loop `i = 1..8`. Identical (unsigned 64-bit wraparound is well-defined).

### [MINOR] Dead `r == 0` branch in RTL `rk()`

`rtl.v` lines ~33–36: `if (r == 0) rk = k ^ rc; else rk = <rotate> ^ rc;`.
For rounds 1..8, r ∈ {26,39,52,1,14,27,40,53} — never 0 — so the branch is
dead code in this design (it only triggers when 13·(i+1) ≡ 0 mod 64, i.e.
i+1 ≡ 0 mod 64). It is correct if ever reached, and untestable here.
Harmless, but dead defensive code in a function whose exact bit behavior is
load-bearing. Suggest either deleting it or a comment stating the
precondition. Not a correctness issue.

### [MINOR] `rtl.v` has no `timescale` directive

Only the testbench declares `` `timescale 1ns/1ps ``; iverilog emits the
"Some modules have no timescale" note. Cosmetic; no sim impact observed.

### [MINOR] Module-scope `integer i` shared with `always @(*)`

`i` is declared at module scope and used as the round-loop index inside the
combinational block (and the function `rk` has its own parameter also named
`i`, shadowing it at the call `rk(key, i+1)` — correct, verified by the
48-vector RK test, but easy to misread). Works in sim and unrolls in synth;
style-only.

### Non-findings (things I tried to break and could not)

- **S-box**: all 16 `case` entries match `S1 =
  [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]` exactly; nibble ordering is
  LSB-first in both RTL (`[4*j+:4]`, j=0..7) and model (`(x >> 4*i) & 0xF`).
  The `default` arm is unreachable (all 16 4-bit values covered).
- **Linear layer**: `{t[24:0], t[31:25]}` ≡ rotl32(t,7) and
  `{t[18:0], t[31:19]}` ≡ rotl32(t,13), verified by bit-position analysis
  (result bit k = t[(k−7) mod 32], resp. (k−13)) and by 22,139 passing sim
  vectors.
- **F composition**: model applies S-layer → linear → ^rk32 for nlayers=1;
  RTL does exactly this (the model's `if nlayers == 1` linear fixup is
  present in RTL unconditionally — correct for this 1-layer candidate).
- **Whitening / Feistel update / output packing**: `L=val_hi^key_hi`,
  `R=val_lo^key_lo`, `Lt=R; Rt=L^F(R, rk[31:0])`, `out={R,L}` — all match.
- **Widths/signage**: `(i+1) * 64'h9E3779B97F4A7C15` is 64-bit unsigned mod
  2^64, matching model's `& M64`; all shift amounts positive; `-Wall` is
  clean for the design file.
- **Latches / undriven nets**: every reg (`L,R,Lt,Rt,rkv,t,r,rc`, function
  returns) is assigned on all paths before use; no incomplete if/case.

## Results

| Check | Result |
|---|---|
| RTL vs Python model, 2139 vectors (2000 random + 139 edge incl. key=0, val=0, all-ones, all 64 single-bit vals, all 64 single-bit keys) | **2139/2139 match**, 0 fail |
| RTL vs Python model, 20,000 additional seeded random vectors | **20000/20000 match**, 0 fail |
| S-box table, 16/16 entries, nibble order | match |
| Round keys, 6 keys × rounds 1..8, via hierarchical call to RTL's own `rk()` | **48/48 match** |
| Mutation: one S-box entry flipped in a copy of rtl.v (original untouched) | **RED — 2090/2139 fail, first vector (val=key=0) already mismatches**; sim is sensitive |
| C (`impl.c` `mix_hash`) vs model on 301 vectors | **301/301 match**; `gcc -Wall -Wextra` clean |

## Verdict

**APPROVE.** The RTL is bit-exact against the Python model on 22,139 vectors
including adversarial edge cases, the S-box table and nibble ordering match
exactly, the round-key schedule matches the model's `_rk_np` on all 8 rounds
for 6 keys (verified against the RTL's actual `rk()` function, not a
reimplementation), and the C implementation agrees. The mutation test proves
the sim would catch a single-entry S-box corruption. Structural review found
no latches, undriven nets, width truncations, or signedness hazards. The three
MINOR notes (dead `r==0` branch, missing timescale, module-scope loop
variable) do not affect correctness.
