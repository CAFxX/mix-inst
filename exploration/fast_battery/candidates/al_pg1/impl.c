#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint8_t SBOX[16] = {1, 10, 4, 12, 6, 15, 3, 9, 2, 13, 11, 7, 5, 0, 8, 14};
static inline uint64_t sbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= (uint64_t)SBOX[(x >> (4*i)) & 0xF] << (4*i);
    return y;
}
// PIVOT: [t3,t3,GIFT-sboxL(46,15),GIFT-sboxL(24,51)], z=3.9@14
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13) ^ rotl64(x,29);
    x ^= (rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,19) ^ rotl64(x,37);
    x = sbox64(x); x ^= rotl64(x,46) ^ rotl64(x,15);
    x = sbox64(x); x ^= rotl64(x,24) ^ rotl64(x,51);
    x ^= rotl64(key, 13);
    return x;
}
