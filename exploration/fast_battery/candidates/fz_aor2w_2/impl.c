// Fused candidate fz_aor2w_2: 2-stage fused 4x2-AND-OR
#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r) {
    r &= 63; if (!r) return x;
    return (x << r) | (x >> (64 - r));
}
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    uint64_t s0r0 = rotl64(x, 1);
    uint64_t s0r1 = rotl64(x, 9);
    uint64_t s0r2 = rotl64(x, 17);
    uint64_t s0r3 = rotl64(x, 29);
    uint64_t s0r4 = rotl64(x, 43);
    uint64_t s0r5 = rotl64(x, 55);
    uint64_t s0r6 = rotl64(x, 7);
    uint64_t s0r7 = rotl64(x, 25);
    x ^= ((s0r0&s0r1)|(s0r2&s0r3)|(s0r4&s0r5)|(s0r6&s0r7));
    uint64_t s1r0 = rotl64(x, 5);
    uint64_t s1r1 = rotl64(x, 15);
    uint64_t s1r2 = rotl64(x, 27);
    uint64_t s1r3 = rotl64(x, 39);
    uint64_t s1r4 = rotl64(x, 51);
    uint64_t s1r5 = rotl64(x, 61);
    uint64_t s1r6 = rotl64(x, 11);
    uint64_t s1r7 = rotl64(x, 33);
    x ^= ((s1r0&s1r1)|(s1r2&s1r3)|(s1r4&s1r5)|(s1r6&s1r7));
    x ^= rotl64(k, 13);
    return x;
}
