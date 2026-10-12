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
// and6 sched search winner as6_200_19, z=8.0@logN18
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,52) & rotl64(x,24)) ^ rotl64(x,19);
    x ^= (rotl64(x,61) & rotl64(x,44)) ^ rotl64(x,43);
    x ^= (rotl64(x,35) & rotl64(x,31)) ^ rotl64(x,50);
    x ^= (rotl64(x,25) & rotl64(x,39)) ^ rotl64(x,42);
    x ^= (rotl64(x,8) & rotl64(x,20)) ^ rotl64(x,12);
    x ^= (rotl64(x,60) & rotl64(x,59)) ^ rotl64(x,3);
    x ^= rotl64(key, 13);
    return x;
}
