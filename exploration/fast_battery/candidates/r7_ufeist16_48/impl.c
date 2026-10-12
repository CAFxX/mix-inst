/* r7_ufeist16_48: unbalanced Feistel, L=16/R=48, 8 rounds.
 * Bit-exact vs Python model round7/models/r7d.py (r7_ufeist16_48_np).
 * Round: newL = (R>>32)&0xFFFF,
 *        newR = (((R&0xFFFFFFFF)<<16) | ((L ^ F(R))&0xFFFF)) & 0xFFFFFFFFFFFF.
 * F: 48->16: S1 on 12 nibbles -> xor-fold 48->16 -> x^rotl16(x,3)^rotl16(x,7)
 *   -> xor 16-bit rk chunk.
 */
#include <stdint.h>

static const uint8_t S1[16] = {0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10};

static uint64_t rotl64(uint64_t x, int n) {
    n &= 63;
    return n ? (x << n) | (x >> (64 - n)) : x;
}

static uint16_t rotl16(uint16_t x, int n) {
    n &= 15;
    return n ? (uint16_t)(((x << n) | (x >> (16 - n))) & 0xFFFF) : x;
}

static uint64_t rk(uint64_t k, int i) {
    return rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}

static uint16_t F_48to16(uint64_t R, uint16_t rk16) {
    uint64_t s = 0;
    for (int j = 0; j < 12; j++)
        s |= (uint64_t)S1[(R >> (4 * j)) & 0xF] << (4 * j);
    uint16_t f = (uint16_t)(((s >> 32) ^ (s >> 16) ^ s) & 0xFFFF);
    f = (uint16_t)((f ^ rotl16(f, 3) ^ rotl16(f, 7)) & 0xFFFF);
    return (uint16_t)((f ^ rk16) & 0xFFFF);
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint16_t L = (uint16_t)(x >> 48);
    uint64_t R = x & 0xFFFFFFFFFFFFULL;
    for (int i = 1; i <= 8; i++) {
        uint16_t F = F_48to16(R, (uint16_t)rk(key, i));
        uint16_t nL = (uint16_t)(R >> 32);
        uint64_t nR = ((((R & 0xFFFFFFFFULL) << 16) | ((L ^ F) & 0xFFFF))
                       & 0xFFFFFFFFFFFFULL);
        L = nL; R = nR;
    }
    return (((uint64_t)L << 48) | R);
}
