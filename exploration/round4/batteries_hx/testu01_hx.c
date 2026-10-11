/* TestU01 SmallCrush for the round-4 finalist candidate h_xorspn3:
 * xorshift64 pre-diffusion + 3-round SPN (S1 S-box + Midori M).
 * Ported from mix_h_xorspn3_s in round4/models/r4_hybrid.py.
 * C port verified against Python model on 12 reference values
 * (keys 0x123456789ABCDEF0 and 0x0, vals 0..5) — all match.
 * Usage: ./testu01_hx <key_hex>
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "TestU01.h"

/* _S1 table */
static const uint8_t S1[16] = {0x0,0x1,0x2,0x4,0x3,0x8,0xF,0xC,
                               0x9,0x5,0xB,0x6,0x7,0xE,0xD,0xA};
/* _PERM (shuffle: output nibble i = input nibble PERM[i]) */
static const int PERM[16] = {0,10,5,15,14,4,11,1,9,3,12,6,7,13,2,8};
static const uint64_t GOLDEN = 0x9E3779B97F4A7C15ULL;

static uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}

static uint64_t rk(uint64_t key, int i) {
    return rotl64(key, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * GOLDEN);
}

static uint64_t sbox16(uint64_t x) {
    uint64_t y = 0;
    for (int b = 0; b < 16; b++)
        y |= (uint64_t)S1[(x >> (4 * b)) & 0xF] << (4 * b);
    return y;
}

static uint64_t midori_M(uint64_t x) {
    uint64_t y = 0;
    for (int c = 0; c < 4; c++) {
        uint64_t col[4];
        for (int j = 0; j < 4; j++)
            col[j] = (x >> (4 * (4 * c + j))) & 0xF;
        uint64_t p = col[0] ^ col[1] ^ col[2] ^ col[3];
        for (int j = 0; j < 4; j++)
            y |= (p ^ col[j]) << (4 * (4 * c + j));
    }
    return y;
}

static uint64_t shuffle(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= ((x >> (4 * PERM[i])) & 0xF) << (4 * i);
    return y;
}

static uint64_t xorshift64(uint64_t x) {
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    return x;
}

static uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = xorshift64(val ^ key);
    for (int i = 0; i < 3; i++)
        x = shuffle(midori_M(sbox16(x ^ rk(key, i))));
    return x ^ rk(key, 3);
}

static uint64_t g_key;
static uint64_t g_ctr;
static uint64_t g_buf;
static int g_have;

static uint32_t gen_bits(void) {
    if (!g_have) {
        g_buf = mix_hash(g_ctr++, g_key);
        g_have = 1;
        return (uint32_t)(g_buf & 0xFFFFFFFFULL);
    } else {
        g_have = 0;
        return (uint32_t)(g_buf >> 32);
    }
}

int main(int argc, char **argv) {
    g_key = argc > 1 ? strtoull(argv[1], NULL, 16) : 0x123456789ABCDEF0ULL;
    g_ctr = 0;
    g_have = 0;
    unif01_Gen *gen = unif01_CreateExternGenBits("mix_h_xorspn3", gen_bits);
    bbattery_SmallCrush(gen);
    unif01_DeleteExternGen01(gen);
    return 0;
}
