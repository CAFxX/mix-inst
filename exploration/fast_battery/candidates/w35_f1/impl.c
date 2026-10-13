#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint8_t SB0[16] = {0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6};
static inline uint64_t sbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 16; i++)
        y |= (uint64_t)SB0[(x >> (4*i)) & 0xF] << (4*i);
    return y;
}
static inline uint64_t splayer64(uint64_t x) {
    uint64_t xs = sbox64(x), y = 0;
    for (int i = 0; i < 64; i++)
        y |= ((xs >> i) & 1u) << ((9*i) & 63);
    return y;
}
// wave-35 two-state (template F): AND-cascade + Midori-Sb0 S-box layer
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,27) & rotl64(x,25)) ^ rotl64(x,37);
    x ^= (rotl64(x,42) & rotl64(x,26)) ^ rotl64(x,32);
    x = splayer64(x);
    x ^= (rotl64(x,2) & rotl64(x,23)) ^ rotl64(x,38);
    x ^= (rotl64(x,8) & rotl64(x,62)) ^ rotl64(x,31);
    x ^= (rotl64(x,20) & rotl64(x,3)) ^ rotl64(x,27);
    x ^= rotl64(key, 13);
    return x;
}
