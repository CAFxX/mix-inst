/* TestU01 SmallCrush for the round-4 hybrid candidate h_xorspn3
 * (xorshift64 pre-diffusion + 3-round SPN: S1 S-box + Midori M + shuffle).
 * Usage: ./testu01_h_xorspn3 <key_hex>
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "TestU01.h"

/* S1 = THF/Blink 4-bit S-box */
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

static uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = xorshift64(val ^ key);
    for (int i = 0; i < 3; i++) {
        uint64_t rk = rotl64(key, 13*(i+1)) ^ ((uint64_t)(i+1) * GOLDEN);
        x ^= rk;
        x = shuffle(midori_M(sbox16(x)));
    }
    uint64_t rk3 = rotl64(key, 13*4) ^ ((uint64_t)4 * GOLDEN);
    return x ^ rk3;
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
    /* sanity: must match Python model f(0,key)=0x726ecd2eeb1fb24f,
       f(0,0)=0xe8aa0581be8e17cc */
    if (mix_hash(0, 0x123456789ABCDEF0ULL) != 0x726ecd2eeb1fb24fULL ||
        mix_hash(0, 0) != 0xe8aa0581be8e17ccULL) {
        fprintf(stderr, "MODEL MISMATCH\n");
        return 1;
    }
    unif01_Gen *gen = unif01_CreateExternGenBits("mix_h_xorspn3", gen_bits);
    bbattery_SmallCrush(gen);
    unif01_DeleteExternGen01(gen);
    return 0;
}
