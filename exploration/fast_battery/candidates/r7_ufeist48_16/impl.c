/* r7_ufeist48_16: unbalanced Feistel, L=48/R=16, 8 rounds.
 * Bit-exact vs Python model round7/models/r7d.py (r7_ufeist48_16_np).
 * Round: newL = (R<<32)|(L>>16), newR = ((L&0xFFFF) ^ F(R)) & 0xFFFF
 *   (F is 16->48 bits; only its low 16 bits enter newR).
 * F: S1 on 4 nibbles -> each nibble n expanded to 12 bits as
 *   (n ^ rotl4(n,1) ^ rotl4(n,2)) replicated x3 -> xor 48-bit rk chunk.
 */
#include <stdint.h>

static const uint8_t S1[16] = {0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10};

static uint64_t rotl64(uint64_t x, int n) {
    n &= 63;
    return n ? (x << n) | (x >> (64 - n)) : x;
}

static uint8_t rotl4(uint8_t x, int n) {
    n &= 3;
    return n ? (uint8_t)(((x << n) | (x >> (4 - n))) & 0xF) : (uint8_t)(x & 0xF);
}

static uint64_t rk(uint64_t k, int i) {
    return rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}

static uint64_t F_16to48(uint16_t R, uint64_t rk48) {
    uint64_t out = 0;
    for (int j = 0; j < 4; j++) {
        uint8_t n = S1[(R >> (4 * j)) & 0xF];
        uint8_t e = (uint8_t)((n ^ rotl4(n, 1) ^ rotl4(n, 2)) & 0xF);
        uint16_t rep = (uint16_t)((e | (e << 4) | (e << 8)) & 0xFFF);
        out |= (uint64_t)rep << (12 * j);
    }
    return (out ^ (rk48 & 0xFFFFFFFFFFFFULL)) & 0xFFFFFFFFFFFFULL;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t L = (x >> 16) & 0xFFFFFFFFFFFFULL;
    uint16_t R = (uint16_t)x;
    for (int i = 1; i <= 8; i++) {
        uint64_t F = F_16to48(R, rk(key, i));
        uint64_t nL = (((uint64_t)R << 32) | (L >> 16)) & 0xFFFFFFFFFFFFULL;
        uint16_t nR = (uint16_t)(((L & 0xFFFF) ^ F) & 0xFFFF);
        L = nL; R = nR;
    }
    return (L << 16) | R;
}
