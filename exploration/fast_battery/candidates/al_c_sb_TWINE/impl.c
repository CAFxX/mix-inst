#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint8_t SBOX[16] = {14, 1, 11, 6, 15, 13, 0, 10, 7, 3, 12, 9, 2, 8, 4, 5};
static inline uint64_t sbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= (uint64_t)SBOX[(x >> (4*i)) & 0xF] << (4*i);
    return y;
}
// component: TWINE sbox alone
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = sbox64(x);
    x ^= rotl64(key, 13);
    return x;
}
