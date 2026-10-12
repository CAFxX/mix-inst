// Fused candidate fz_r3x3_2: 2-stage pure replacement: x = AOR3a ^ AOR3b
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
    uint64_t s0r8 = rotl64(x, 39);
    uint64_t s0r9 = rotl64(x, 13);
    uint64_t s0r10 = rotl64(x, 23);
    uint64_t s0r11 = rotl64(x, 33);
    uint64_t s0r12 = rotl64(x, 47);
    uint64_t s0r13 = rotl64(x, 57);
    uint64_t s0r14 = rotl64(x, 61);
    uint64_t s0r15 = rotl64(x, 5);
    uint64_t s0r16 = rotl64(x, 19);
    uint64_t s0r17 = rotl64(x, 37);
    x = (((s0r0&s0r1&s0r2)|(s0r3&s0r4&s0r5)|(s0r6&s0r7&s0r8)) ^ ((s0r9&s0r10&s0r11)|(s0r12&s0r13&s0r14)|(s0r15&s0r16&s0r17)));
    uint64_t s1r0 = rotl64(x, 5);
    uint64_t s1r1 = rotl64(x, 15);
    uint64_t s1r2 = rotl64(x, 27);
    uint64_t s1r3 = rotl64(x, 39);
    uint64_t s1r4 = rotl64(x, 51);
    uint64_t s1r5 = rotl64(x, 61);
    uint64_t s1r6 = rotl64(x, 11);
    uint64_t s1r7 = rotl64(x, 33);
    uint64_t s1r8 = rotl64(x, 47);
    uint64_t s1r9 = rotl64(x, 3);
    uint64_t s1r10 = rotl64(x, 17);
    uint64_t s1r11 = rotl64(x, 29);
    uint64_t s1r12 = rotl64(x, 43);
    uint64_t s1r13 = rotl64(x, 53);
    uint64_t s1r14 = rotl64(x, 59);
    uint64_t s1r15 = rotl64(x, 9);
    uint64_t s1r16 = rotl64(x, 25);
    uint64_t s1r17 = rotl64(x, 49);
    x = (((s1r0&s1r1&s1r2)|(s1r3&s1r4&s1r5)|(s1r6&s1r7&s1r8)) ^ ((s1r9&s1r10&s1r11)|(s1r12&s1r13&s1r14)|(s1r15&s1r16&s1r17)));
    x ^= rotl64(k, 13);
    return x;
}
