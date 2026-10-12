/* r7_feist8_gift: 8-round Feistel, F = GIFT S-box x2 + rotl7/rotl13 XOR linear.
 * Bit-exact vs Python model round7/models/r7.py (r7_feist8_gift). */
#include <stdint.h>

static const uint8_t SB[16] = {0x1,0xA,0x4,0xC,0x6,0xF,0x3,0x9,
                               0x2,0xD,0xB,0x7,0x5,0x0,0x8,0xE};

static uint32_t sbox_layer32(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 8; i++)
        r |= (uint32_t)SB[(x >> (4*i)) & 0xF] << (4*i);
    return r;
}

static uint32_t rotl32(uint32_t x, int n) { return (x << n) | (x >> (32 - n)); }
static uint64_t rotl64(uint64_t x, int n) { return (x << n) | (x >> (64 - n)); }

static uint64_t rk(uint64_t k, int i) {
    return rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}

static uint32_t F_f(uint32_t R, uint64_t rkv) {
    uint32_t t = sbox_layer32(R);
    t = t ^ rotl32(t, 7) ^ rotl32(t, 13);
    t = sbox_layer32(t);
    return t ^ (uint32_t)rkv;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32) ^ (uint32_t)(key >> 32);
    uint32_t R = (uint32_t)val ^ (uint32_t)key;
    for (int i = 1; i <= 8; i++) {
        uint32_t F = F_f(R, rk(key, i));
        uint32_t nL = R, nR = L ^ F;
        L = nL; R = nR;
    }
    return ((uint64_t)R << 32) | L;
}
