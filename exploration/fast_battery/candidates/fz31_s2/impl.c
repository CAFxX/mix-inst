#include <stdint.h>
/* fz31_s2: wave31 axis C (S-box layer probe) */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
static inline uint64_t psbox(uint64_t x) {
    static const uint8_t S[16] = {0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2};
    uint64_t y = 0;
    for (int n = 0; n < 16; n++) y |= (uint64_t)S[(x >> (4*n)) & 0xFu] << (4*n);
    return y; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ psbox(x) ^ rotl64(x,13);
    x = x ^ (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13) ^ rotl64(x,29);
    x = x ^ (rotl64(x,5) & rotl64(x,15)) ^ rotl64(x,21);
    x = x ^ rotl64(k, 13);
    return x;
}
