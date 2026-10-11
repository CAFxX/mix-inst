"""Generator for round-4 family G: Feistel with Goldreich-style 5-local F.

Emits BOTH models/r4_glfeistel.py and rtl/r4_glfeistel.v from one tap list,
so model and RTL cannot disagree.

F(h)[j] = h[a]^h[b]^h[c]^(h[d]&h[e]) with fixed random taps per output bit j.
Feistel: (L,R) -> (R, L ^ F(R ^ rk[i])), rk[i] = ROTL32(key_lo,7*(i+1))^RC32[i].
G1: 6 rounds. G2: 8 rounds.

Bijectivity (fixed key): standard Feistel => permutation of 2^64 (F need not
be bijective).
"""
import numpy as np

R4 = "/home/hatch/workspace/mix/exploration/round4"
rng = np.random.default_rng(0x6A09E667)
TAPS = [sorted(rng.choice(32, size=5, replace=False).tolist()) for _ in range(32)]
taps_repr = repr(TAPS)

PY = '''"""Round 4, family G: Feistel with Goldreich-style 5-local F (generated).

F(h)[j] = h[a]^h[b]^h[c]^(h[d]&h[e]); taps fixed below (seed 0x6A09E667).
G1 = 6 rounds, G2 = 8 rounds. (L,R) -> (R, L ^ F(R ^ rk[i])).
Bijectivity: Feistel => permutation for fixed key.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, check_model_equiv, bijectivity_spotcheck)

M32 = np.uint64(0xFFFFFFFF)
_TAPS = %s
_RC_MUL = 0x9E3779B9


def _rotl32_np(v, r):
    r = int(r) & 31
    v = np.asarray(v, dtype=np.uint64) & M32
    if r == 0:
        return v
    return (((v << np.uint64(r)) | (v >> np.uint64(32 - r))) & M32)


def _F_np(h):
    h = np.asarray(h, dtype=np.uint64) & M32
    out = np.zeros(h.shape, dtype=np.uint64)
    hb = [(h >> np.uint64(i)) & np.uint64(1) for i in range(32)]
    for j, (a, b, c, d, e) in enumerate(_TAPS):
        bit = hb[a] ^ hb[b] ^ hb[c] ^ (hb[d] & hb[e])
        out = out | (bit << np.uint64(j))
    return out & M32


def _feistel_np(val, key, rounds):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    klo = np.asarray(key, dtype=np.uint64) & M32
    L = (x >> np.uint64(32)) & M32
    R = x & M32
    for i in range(rounds):
        rk = (_rotl32_np(klo, 7 * (i + 1)) ^
              np.uint64(((i + 1) * _RC_MUL) & 0xFFFFFFFF)) & M32
        nL = R
        nR = (L ^ _F_np(R ^ rk)) & M32
        L, R = nL, nR
    return ((L << np.uint64(32)) | R) & MASK64


def mix_gl5_f6_np(val, key):
    return _feistel_np(val, key, 6)


def mix_gl5_f8_np(val, key):
    return _feistel_np(val, key, 8)


def _rotl32_s(v, r):
    r &= 31
    v &= 0xFFFFFFFF
    return (((v << r) | (v >> (32 - r))) & 0xFFFFFFFF) if r else v


def _F_s(h):
    h &= 0xFFFFFFFF
    out = 0
    for j, (a, b, c, d, e) in enumerate(_TAPS):
        bit = (((h >> a) & 1) ^ ((h >> b) & 1) ^ ((h >> c) & 1) ^
               (((h >> d) & 1) & ((h >> e) & 1)))
        out |= bit << j
    return out & 0xFFFFFFFF


def _feistel_s(val, key, rounds):
    x = (val ^ key) & 0xFFFFFFFFFFFFFFFF
    klo = key & 0xFFFFFFFF
    L = (x >> 32) & 0xFFFFFFFF
    R = x & 0xFFFFFFFF
    for i in range(rounds):
        rk = (_rotl32_s(klo, 7 * (i + 1)) ^ (((i + 1) * _RC_MUL) & 0xFFFFFFFF)) & 0xFFFFFFFF
        nL = R
        nR = (L ^ _F_s(R ^ rk)) & 0xFFFFFFFF
        L, R = nL, nR
    return ((L << 32) | R) & 0xFFFFFFFFFFFFFFFF


def mix_gl5_f6_s(v, k): return _feistel_s(v, k, 6)
def mix_gl5_f8_s(v, k): return _feistel_s(v, k, 8)


if __name__ == "__main__":
    for s, n in [(mix_gl5_f6_s, mix_gl5_f6_np), (mix_gl5_f8_s, mix_gl5_f8_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
''' % taps_repr

flines = []
for j, (a, b, c, d, e) in enumerate(TAPS):
    flines.append(f"        F5[{j}] = h[{a}] ^ h[{b}] ^ h[{c}] ^ (h[{d}] & h[{e}]);")
FASSIGN = "\n".join(flines)

V = """// Round 4, family G: Feistel with Goldreich-style 5-local F (generated).
// F(h)[j] = h[a]^h[b]^h[c]^(h[d]&h[e]); taps fixed (seed 0x6A09E667).
// (L,R) -> (R, L ^ F(R ^ rk[i])); rk[i] = ROTL32(key_lo,7*(i+1)) ^ RC32[i].
module r4_glfeistel #(parameter ROUNDS = 6)
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [31:0] F5(input [31:0] h);
        reg [31:0] F5;
        begin
%s
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [31:0] klo = key[31:0];
    wire [31:0] L [0:ROUNDS];
    wire [31:0] R [0:ROUNDS];
    assign L[0] = x0[63:32];
    assign R[0] = x0[31:0];
    genvar i;
    generate
        for (i = 0; i < ROUNDS; i = i + 1) begin : rnd
            localparam integer RR = (7 * (i + 1)) %% 32;
            wire [31:0] rk = {klo[31-RR:0], klo[31:32-RR]} ^ ((i + 1) * 32'h9E3779B9);
            assign L[i+1] = R[i];
            assign R[i+1] = L[i] ^ F5(R[i] ^ rk);
        end
    endgenerate
    assign out = {L[ROUNDS], R[ROUNDS]};
endmodule
""" % FASSIGN

with open(f"{R4}/models/r4_glfeistel.py", "w") as f:
    f.write(PY)
with open(f"{R4}/rtl/r4_glfeistel.v", "w") as f:
    f.write(V)
print("generated models/r4_glfeistel.py and rtl/r4_glfeistel.v")
print("taps[0..2] =", TAPS[:3])
