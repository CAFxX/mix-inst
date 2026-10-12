// Fused candidate fz_maj3r_3: 3-stage balanced maj3 replacement: x = maj3a ^ maj3b ^ maj3c
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
    uint64_t s0r1 = rotl64(x, 8);
    uint64_t s0r2 = rotl64(x, 15);
    uint64_t s0r3 = rotl64(x, 29);
    uint64_t s0r4 = rotl64(x, 42);
    uint64_t s0r5 = rotl64(x, 53);
    uint64_t s0r6 = rotl64(x, 6);
    uint64_t s0r7 = rotl64(x, 23);
    uint64_t s0r8 = rotl64(x, 38);
    x = maj3(s0r0,s0r1,s0r2) ^ maj3(s0r3,s0r4,s0r5) ^ maj3(s0r6,s0r7,s0r8);
    uint64_t s1r0 = rotl64(x, 3);
    uint64_t s1r1 = rotl64(x, 12);
    uint64_t s1r2 = rotl64(x, 21);
    uint64_t s1r3 = rotl64(x, 37);
    uint64_t s1r4 = rotl64(x, 48);
    uint64_t s1r5 = rotl64(x, 59);
    uint64_t s1r6 = rotl64(x, 10);
    uint64_t s1r7 = rotl64(x, 31);
    uint64_t s1r8 = rotl64(x, 44);
    x = maj3(s1r0,s1r1,s1r2) ^ maj3(s1r3,s1r4,s1r5) ^ maj3(s1r6,s1r7,s1r8);
    uint64_t s2r0 = rotl64(x, 7);
    uint64_t s2r1 = rotl64(x, 18);
    uint64_t s2r2 = rotl64(x, 25);
    uint64_t s2r3 = rotl64(x, 43);
    uint64_t s2r4 = rotl64(x, 52);
    uint64_t s2r5 = rotl64(x, 61);
    uint64_t s2r6 = rotl64(x, 14);
    uint64_t s2r7 = rotl64(x, 35);
    uint64_t s2r8 = rotl64(x, 50);
    x = maj3(s2r0,s2r1,s2r2) ^ maj3(s2r3,s2r4,s2r5) ^ maj3(s2r6,s2r7,s2r8);
    x ^= rotl64(k, 13);
    return x;
}
