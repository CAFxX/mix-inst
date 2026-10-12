/* r7_misty: 8-round balanced Feistel 32/32; F contains a 3-round inner
 * Feistel on 16/16 halves with S1 S-boxes (Misty-like, recursive).
 * Bit-exact vs Python model round7/models/r7d.py (r7_misty_np).
 * Outer round: (L,R) = (R, L ^ F(R)).
 * F(R32, rk64): split (a16,b16); 3x (a,b) = (b, a ^ G(b)),
 *   G(b) = sbox16(b) ^ subkey_j, subkey_j = (rk64 >> (16*j)) & 0xFFFF;
 *   F_out = ((a << 16) | b) ^ (rk64 & 0xFFFFFFFF).
 */
#include <stdint.h>

static const uint8_t S1[16] = {0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10};

static uint64_t rotl64(uint64_t x, int n) {
    n &= 63;
    return n ? (x << n) | (x >> (64 - n)) : x;
}

static uint64_t rk(uint64_t k, int i) {
    return rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}

static uint16_t sbox16(uint16_t b) {
    uint16_t r = 0;
    for (int j = 0; j < 4; j++)
        r |= (uint16_t)S1[(b >> (4 * j)) & 0xF] << (4 * j);
    return r;
}

static uint32_t F_misty(uint32_t R, uint64_t rk64) {
    uint16_t a = (uint16_t)(R >> 16), b = (uint16_t)R;
    for (int j = 0; j < 3; j++) {
        uint16_t rk16 = (uint16_t)(rk64 >> (16 * j));
        uint16_t na = b;
        uint16_t nb = (uint16_t)((a ^ (sbox16(b) ^ rk16)) & 0xFFFF);
        a = na; b = nb;
    }
    uint32_t out = ((uint32_t)a << 16) | b;
    return (out ^ (uint32_t)rk64) & 0xFFFFFFFFu;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint32_t L = (uint32_t)(x >> 32), R = (uint32_t)x;
    for (int i = 1; i <= 8; i++) {
        uint32_t F = F_misty(R, rk(key, i));
        uint32_t nL = R, nR = (L ^ F) & 0xFFFFFFFFu;
        L = nL; R = nR;
    }
    return ((uint64_t)R << 32) | L;
}
