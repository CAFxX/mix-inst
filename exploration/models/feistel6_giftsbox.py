"""C4 feistel6_giftsbox: 6-round Feistel, 32-bit halves, GIFT S-box.

Construction: L=val[31:0], R=val[63:32]; L0=L^key[31:0], R0=R^key[63:32];
round (L,R)->(R, L^F(R,rk[i])); F(x,rk)=P32(SBOX8(x^rk)) with 8x GIFT
4-bit S-box GS: 1 A 4 C 6 F 3 9 2 D B 7 5 0 8 E (Table 3 of the primary
GIFT paper, Banik et al. "GIFT: A Small Present", CHES 2017; 16 distinct
asserted in _feistel_common -- the table is borrowed from GIFT only, not
the cipher; its published bounds do not transfer) and 32-bit
bit-permutation P32(i)=8*i mod 31 (i<31), P32(31)=31 (asserted a
permutation in _feistel_common);
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
from models._feistel_common import (GIFT_SBOX, p32_s, p32_np, sbox8_s,
                                    sbox8_np, feistel_s, feistel_np)


def F_s(x, rk):
    return p32_s(sbox8_s(x ^ rk, GIFT_SBOX))


def F_np(x, rk):
    return p32_np(sbox8_np(x ^ rk, GIFT_SBOX))


def mix_feistel6_giftsbox_scalar(val, key):
    return feistel_s(val, key, 6, F_s)


def mix_feistel6_giftsbox_np(val, key):
    return feistel_np(val, key, 6, F_np)


if __name__ == "__main__":
    check_model_equiv(mix_feistel6_giftsbox_scalar, mix_feistel6_giftsbox_np,
                      "feistel6_giftsbox")
    bijectivity_spotcheck(mix_feistel6_giftsbox_np, "feistel6_giftsbox")
