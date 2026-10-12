/* h_xorspn3 reference implementation for the fast staged battery.
 * xorshift64 pre-diffusion + 3-round SPN (S1 S-box + Midori M + nibble shuffle).
 * Bit-identical to round4/models/r4_hybrid.py :: mix_h_xorspn3_s and to
 * round4/testu01_h_xorspn3.c. Goldens: f(0,0x123456789ABCDEF0)=0x726ecd2eeb1fb24f,
 * f(0,0)=0xe8aa0581be8e17cc.
 */
#include <stdint.h>

static const uint8_t SBOX[16] = {0x0,0x1,0x2,0x4,0x3,0x8,0xF,0xC,
                                 0x9,0x5,0xB,0x6,0x7,0xE,0xD,0xA};
/* nibble shuffle: y_nibble[i] = x_nibble[PERM[i]] */
static const uint8_t PERM[16] = {0,10,5,15,14,4,11,1,9,3,12,6,7,13,2,8};
static const uint64_t GOLDEN = 0x9E3779B97F4A7C15ULL;

static uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}

static uint64_t sbox16(uint64_t x) {
    uint64_t y = 0;
    for (int b = 0; b < 16; b++)
        y |= (uint64_t)SBOX[(x >> (4*b)) & 0xF] << (4*b);
    return y;
}

/* Midori almost-MDS binary matrix: per 4-nibble column, out_j = parity ^ in_j */
static uint64_t midori_M(uint64_t x) {
    uint64_t y = 0;
    for (int c = 0; c < 4; c++) {
        uint64_t n[4];
        for (int j = 0; j < 4; j++)
            n[j] = (x >> (16*c + 4*j)) & 0xF;
        uint64_t p = n[0] ^ n[1] ^ n[2] ^ n[3];
        for (int j = 0; j < 4; j++)
            y |= (p ^ n[j]) << (16*c + 4*j);
    }
    return y;
}

static uint64_t shuffle(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= ((x >> (4*PERM[i])) & 0xFULL) << (4*i);
    return y;
}

static uint64_t xorshift64(uint64_t x) {
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    return x;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = xorshift64(val ^ key);
    for (int i = 1; i <= 3; i++) {
        uint64_t rk = rotl64(key, 13u*(unsigned)i) ^ ((uint64_t)i * GOLDEN);
        x = shuffle(midori_M(sbox16(x ^ rk)));
    }
    uint64_t rk4 = rotl64(key, 13u*4u) ^ ((uint64_t)4 * GOLDEN);
    return x ^ rk4;
}
