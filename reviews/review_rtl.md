All checks complete. Compiling the final report.

---

# Peer Review Report: `mix` RTL (`~/workspace/mix/rtl/`)

**Method:** adversarial black-box + white-box review. Wrote a fully independent Python model from the spec equations alone (never imported `spn.py`), generated fresh vectors, and checked the RTL with my own testbenches; exhaustively probed `sbox4`, `player()`, and `rkey()` via simulation; elaborated with Yosys 0.33 to check for latches/ROMs/loops; tested X-propagation and missing-file behavior of every testbench.

## Verdicts

| # | Item | Verdict |
|---|------|---------|
| 1 | Independent model vs RTL (ROUNDS=10 and 8) | **PASS** |
| 2 | S-box Boolean equations vs PRESENT table | **PASS** |
| 3 | pLayer wiring vs P(i)=16·i mod 63 | **PASS** |
| 4 | Round-key rotations incl. whitening, ROUNDS=8/10 | **PASS** |
| 5 | Purely combinational, no latches/loops | **PASS** |
| 6 | `gen_vectors.py` semantics | **PASS** |

## Evidence

**1. Functional correctness.** Independent model `/tmp/review_model.py` (spec text only): 400 random vectors × ROUNDS=10 → **400/400 match**; 400 × ROUNDS=8 → **400/400 match** (own testbench `/tmp/tb_review.v`, `===` comparison). Project's own benches reproduced in my hands: `tb_mix.v` → **TB PASS** (3007 vectors); `tb_mix8.v` → ran to completion, zero `MIS` lines (500 vectors); `tb_golden.v` → **8/8 pass**, and all 8 golden vectors independently match my model. X-propagation clean: defined inputs → fully-defined outputs (`mix(0,0,10)=caa7cd352519f486` agrees with model bit-for-bit); X input → all-X output (no X-optimism, no undriven bits). Any rotation/constant/nibble-order error would fail these; none did.

**2. S-box.** Exhaustive simulation of `sbox4`: **16/16** match the PRESENT table (`C 5 6 B 9 0 A D 3 E F 8 4 7 1 2`); X→X. SOP `assign`s only — no case statement, no ROM inference pattern.

**3. pLayer.** Hierarchical calls to `dut.player()`: all 64 single-bit probes (each input bit i lands exactly on output bit `(16*i)%63`) + 200 random words → **264/264**. Confirmed `(16*i)%63` permutes 0..62 (gcd(16,63)=1) and bit 63 is fixed.

**4. Round keys.** Hierarchical calls to `dut.rkey(k,i)` for ROUNDS∈{8,10}, i=0..ROUNDS, keys {0, all-ones, 0x8000…0, 1, random} → **100/100** match `ROTL64(key,13*(i+1) mod 64) XOR (i+1)*0x9E3779B97F4A7C15`. Generate loop `g=0..ROUNDS-1` + whitening `rkey(key,ROUNDS)`: no off-by-one (end-to-end vector matches at both ROUNDS values prove it). `rotl64` correctly guards `r==0` (avoids shift-by-64); rotation is never 0 for ROUNDS≤10 anyway since 13 is invertible mod 64.

**5. Combinational.** No clock/reset ports. Yosys elaboration: **0** `$dff`/`$dlatch`/`$sr`, 0 memories, 0 processes; cell types only `$and/$not/$or/$xor`; 160 `sbox4` instances = 16×10 as expected. Generate chain is strictly feedforward (`s[g]→s[g+1]`); no combinational loop is structurally possible.

**6. `gen_vectors.py`.** Calls `mix_spn_scalar(v,k,10)`; I verified `spn.py` ≡ my independent model on **1000** random vectors (ROUNDS 8 and 10), all match — so the golden vectors encode the spec semantics. Fixed seed `0xBEEF` → reproducible; writes the absolute path `tb_mix.v` reads; 3000 random + 7 edge cases = 3007 lines confirmed.

## Findings (no RTL logic bugs found)

1. **`tb_mix8.v` vacuous pass (test-hygiene bug).** Missing `vectors8.hex` → prints `TB8: 0/0 pass`, exit code 0 (confirmed in empty dir). There is no `fd==0` check, unlike `tb_mix.v` which FATALs correctly. A CI grep for "pass" would accept zero tested vectors. **Recommend** adding the same FATAL check as `tb_mix.v:13`.
2. **`tb_golden.v` has the same missing-file vacuity** (no fd check; `../golden_vectors.txt`). Current results are valid (file exists, 8/8 pass), but the hole should be closed the same way.
3. **`tb_mix8.v` prints no explicit PASS/FAIL verdict** — just `TB8: np/nf pass`. Verdict must be inferred from the ratio; recommend an explicit verdict line.
4. **Build artifacts in the source tree:** compiled sim binaries `tb_mix`, `tb_mix8`, `tb_golden` (3–3.6 MB each) are checked into `rtl/`. Recommend `.gitignore`-ing them.

## Notes for the parent agent
- The header comment's bijectivity claim is sound: I confirmed the S-box table is a permutation of 0..15 and the pLayer permutes bit positions, so each stage is bijective as claimed.
- The S-box SOP was verified by exhaustive simulation, not by re-deriving the Quine–McCluskey minimization — but 16/16 exact match is definitive regardless of how the equations were obtained.
- `gen_vectors.py` hardcodes 10 rounds (no ROUNDS parameter); fine for the default DUT, but a future 8-round tapeout would need `vectors8.hex` regenerated from an equivalent parameterized path (as was done inline for the current `vectors8.hex`).

**Overall: RTL is functionally correct against the spec. No logic bugs. Two test-hygiene fixes recommended (missing-file guards + explicit verdict in `tb_mix8.v`/`tb_golden.v`).**