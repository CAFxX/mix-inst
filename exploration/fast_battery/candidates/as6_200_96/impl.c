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
// and6 sched search as6_200_96 z=14.8
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,4) & rotl64(x,21)) ^ rotl64(x,37);
    x ^= (rotl64(x,15) & rotl64(x,41)) ^ rotl64(x,43);
    x ^= (rotl64(x,17) & rotl64(x,13)) ^ rotl64(x,46);
    x ^= (rotl64(x,28) & rotl64(x,48)) ^ rotl64(x,16);
    x ^= (rotl64(x,11) & rotl64(x,18)) ^ rotl64(x,18);
    x ^= (rotl64(x,24) & rotl64(x,29)) ^ rotl64(x,38);
    x ^= rotl64(key, 13);
    return x;
}
