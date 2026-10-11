/* TestU01 SmallCrush for the round-3 winner (r3_xorlin_qm, function-identical
 * to spn4_xorlin_1137). Implements the 4-round SPN directly in C.
 * Usage: ./testu01_smallcrush <key_hex>
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "TestU01.h"

static const uint8_t SBOX[16] = {0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2};
static const uint64_t GOLDEN = 0x9E3779B97F4A7C15ULL;

static uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}

static uint64_t sbox_layer(uint64_t x) {
    uint64_t y = 0;
    for (int b = 0; b < 16; b++) {
        y |= (uint64_t)SBOX[(x >> (4*b)) & 0xF] << (4*b);
    }
    return y;
}

static uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    for (int i = 0; i < 4; i++) {
        uint64_t rk = rotl64(key, 13*(i+1)) ^ ((uint64_t)(i+1) * GOLDEN);
        x ^= rk;
        x = sbox_layer(x);
        x = x ^ rotl64(x, 11) ^ rotl64(x, 37);
    }
    uint64_t rk4 = rotl64(key, 13*5) ^ ((uint64_t)5 * GOLDEN);
    return x ^ rk4;
}

static uint64_t g_key;
static uint64_t g_ctr;
static uint64_t g_buf;
static int g_have;  // 0 = need new 64-bit, 1 = have high 32 bits buffered

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
    // sanity: first output must match Python model
    // (verified externally; here just run)
    unif01_Gen *gen = unif01_CreateExternGenBits("mix_r3", gen_bits);
    bbattery_SmallCrush(gen);
    unif01_DeleteExternGen01(gen);
    return 0;
}
