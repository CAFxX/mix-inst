#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint8_t SBOX[16] = {12, 6, 9, 0, 1, 10, 7, 11, 3, 14, 15, 8, 4, 13, 5, 2};
static inline uint64_t sbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= (uint64_t)SBOX[(x >> (4*i)) & 0xF] << (4*i);
    return y;
}
// and6 sched search as6_200_108 z=15.5
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,24) & rotl64(x,63)) ^ rotl64(x,6);
    x ^= (rotl64(x,17) & rotl64(x,36)) ^ rotl64(x,49);
    x ^= (rotl64(x,59) & rotl64(x,4)) ^ rotl64(x,57);
    x ^= (rotl64(x,47) & rotl64(x,5)) ^ rotl64(x,48);
    x ^= (rotl64(x,34) & rotl64(x,18)) ^ rotl64(x,50);
    x ^= (rotl64(x,10) & rotl64(x,38)) ^ rotl64(x,42);
    x ^= rotl64(key, 13);
    return x;
}
