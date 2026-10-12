// Fused candidate fz_aor3_3: 3-stage fused 3x3-AND-OR: x ^= (ra&rb&rc)|(rd&re&rf)|(rg&rh&ri)
#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r) {
    r &= 63; if (!r) return x;
    return (x << r) | (x >> (64 - r));
}
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    uint64_t s0r0 = rotl64(x, 1);
    uint64_t s0r1 = rotl64(x, 7);
    uint64_t s0r2 = rotl64(x, 13);
    uint64_t s0r3 = rotl64(x, 29);
    uint64_t s0r4 = rotl64(x, 41);
    uint64_t s0r5 = rotl64(x, 53);
    uint64_t s0r6 = rotl64(x, 5);
    uint64_t s0r7 = rotl64(x, 23);
    uint64_t s0r8 = rotl64(x, 37);
    x ^= ((s0r0&s0r1&s0r2)|(s0r3&s0r4&s0r5)|(s0r6&s0r7&s0r8));
    uint64_t s1r0 = rotl64(x, 3);
    uint64_t s1r1 = rotl64(x, 11);
    uint64_t s1r2 = rotl64(x, 19);
    uint64_t s1r3 = rotl64(x, 37);
    uint64_t s1r4 = rotl64(x, 47);
    uint64_t s1r5 = rotl64(x, 59);
    uint64_t s1r6 = rotl64(x, 9);
    uint64_t s1r7 = rotl64(x, 31);
    uint64_t s1r8 = rotl64(x, 43);
    x ^= ((s1r0&s1r1&s1r2)|(s1r3&s1r4&s1r5)|(s1r6&s1r7&s1r8));
    uint64_t s2r0 = rotl64(x, 7);
    uint64_t s2r1 = rotl64(x, 17);
    uint64_t s2r2 = rotl64(x, 23);
    uint64_t s2r3 = rotl64(x, 43);
    uint64_t s2r4 = rotl64(x, 51);
    uint64_t s2r5 = rotl64(x, 61);
    uint64_t s2r6 = rotl64(x, 13);
    uint64_t s2r7 = rotl64(x, 35);
    uint64_t s2r8 = rotl64(x, 49);
    x ^= ((s2r0&s2r1&s2r2)|(s2r3&s2r4&s2r5)|(s2r6&s2r7&s2r8));
    x ^= rotl64(k, 13);
    return x;
}
