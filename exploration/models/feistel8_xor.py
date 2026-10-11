"""C3 feistel8_xor: 8-round Feistel, 32-bit halves, xor-only F (boundary probe).

Construction: L=val[31:0], R=val[63:32]; L0=L^key[31:0], R0=R^key[63:32];
round (L,R)->(R, L^F(R,rk[i])); F(x,rk)=(x^rk)^ROTL32(x,7)^ROTL32(x,19)
-- a near-affine (linear-plus-keyxor) round function, CRYPTOGRAPHICALLY
WEAK BY CONSTRUCTION (differential probability does not decay; included
only to map the delay/statistical boundary, never as a finalizer);
rk[i]=ROTL32(key[31:0],3*(i+1))^ROTL32(key[63:32],5*(i+1))
^((i+1)*0x9E3779B9 mod 2^32); no final swap;
out={Rn^ROTL32(key[63:32],7), Ln^ROTL32(key[31:0],7)}.

Bijectivity (fixed key): each Feistel round (L,R)->(R,L^F(R,rk)) is bijective
for ANY F (recover R=L', L=R'^F(L',rk)); input/output key xors are bijective;
composition of bijections => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import check_model_equiv, bijectivity_spotcheck
from models._feistel_common import rotl32_s, rotl32_np, feistel_s, feistel_np


def F_s(x, rk):
    x ^= rk
    return x ^ rotl32_s(x, 7) ^ rotl32_s(x, 19)


def F_np(x, rk):
    x = x ^ rk
    return x ^ rotl32_np(x, 7) ^ rotl32_np(x, 19)


def mix_feistel8_xor_scalar(val, key):
    return feistel_s(val, key, 8, F_s)


def mix_feistel8_xor_np(val, key):
    return feistel_np(val, key, 8, F_np)


if __name__ == "__main__":
    check_model_equiv(mix_feistel8_xor_scalar, mix_feistel8_xor_np,
                      "feistel8_xor")
    bijectivity_spotcheck(mix_feistel8_xor_np, "feistel8_xor")
