/* r7_feist8_rkcheap: 8-round Feistel, F=r6 rotl7/rotl13, rk = k^(i+1)*GOLDEN (no rotation)
 * Bit-exact vs round7/models/r7c.py (r7_feist8_rkcheap).
 */
#include <stdint.h>

static const uint8_t S1[16] = {0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10};

static uint32_t sbox_layer32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)S1[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}

static uint32_t rotl32(uint32_t x, int n) { return (x << n) | (x >> (32 - n)); }
static uint64_t rotl64(uint64_t x, int n) { return (x << n) | (x >> (64 - n)); }

static uint32_t lin32(uint32_t t) {   /* x^rotl7^rotl13 */
    return t ^ rotl32(t, 7) ^ rotl32(t, 13);
}

static uint64_t rk(uint64_t k, int i) {   /* k ^ (i+1)*GOLDEN, no rotation */
    return k ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}

static uint32_t F_spn(uint32_t R, uint64_t rkv) {
    uint32_t t = sbox_layer32(R);
    t = lin32(t);
    t = sbox_layer32(t);
    return t ^ (uint32_t)rkv;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32) ^ (uint32_t)(key >> 32);
    uint32_t R = (uint32_t)val ^ (uint32_t)key;
    for (int i = 1; i <= 8; i++) {
        uint32_t F = F_spn(R, rk(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }
    return ((uint64_t)R << 32) | L;
}
