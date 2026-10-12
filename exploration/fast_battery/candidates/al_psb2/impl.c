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
// PIVOT wave: [t3,t3,SKINNY-sboxL(46,15),SKINNY-sboxL(24,51)], proxy z=3.7@logN14, est 20.0u
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13) ^ rotl64(x,29);
    x ^= (rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,19) ^ rotl64(x,37);
    x = sbox64(x); x ^= rotl64(x,46) ^ rotl64(x,15);
    x = sbox64(x); x ^= rotl64(x,24) ^ rotl64(x,51);
    x ^= rotl64(key, 13);
    return x;
}
