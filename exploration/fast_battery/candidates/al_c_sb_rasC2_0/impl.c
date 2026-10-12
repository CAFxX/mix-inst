#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint8_t SBOX[16] = {0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14};
static inline uint64_t sbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= (uint64_t)SBOX[(x >> (4*i)) & 0xF] << (4*i);
    return y;
}
// component: rasC2_0 sbox alone
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = sbox64(x);
    x ^= rotl64(key, 13);
    return x;
}
