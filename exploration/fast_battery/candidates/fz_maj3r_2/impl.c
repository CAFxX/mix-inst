// Fused candidate fz_maj3r_2: 2-stage balanced maj3 replacement
#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r) {
    r &= 63; if (!r) return x;
    return (x << r) | (x >> (64 - r));
}
static uint64_t maj3(uint64_t a, uint64_t b, uint64_t c) {
    return (a&b)|(a&c)|(b&c);
}
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    uint64_t s0r0 = rotl64(x, 1);
    uint64_t s0r1 = rotl64(x, 10);
    uint64_t s0r2 = rotl64(x, 19);
    uint64_t s0r3 = rotl64(x, 29);
    uint64_t s0r4 = rotl64(x, 44);
    uint64_t s0r5 = rotl64(x, 55);
    uint64_t s0r6 = rotl64(x, 7);
    uint64_t s0r7 = rotl64(x, 26);
    uint64_t s0r8 = rotl64(x, 41);
    x = maj3(s0r0,s0r1,s0r2) ^ maj3(s0r3,s0r4,s0r5) ^ maj3(s0r6,s0r7,s0r8);
    uint64_t s1r0 = rotl64(x, 5);
    uint64_t s1r1 = rotl64(x, 16);
    uint64_t s1r2 = rotl64(x, 27);
    uint64_t s1r3 = rotl64(x, 39);
    uint64_t s1r4 = rotl64(x, 52);
    uint64_t s1r5 = rotl64(x, 61);
    uint64_t s1r6 = rotl64(x, 11);
    uint64_t s1r7 = rotl64(x, 34);
    uint64_t s1r8 = rotl64(x, 47);
    x = maj3(s1r0,s1r1,s1r2) ^ maj3(s1r3,s1r4,s1r5) ^ maj3(s1r6,s1r7,s1r8);
    x ^= rotl64(k, 13);
    return x;
}
