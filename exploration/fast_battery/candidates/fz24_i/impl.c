#include <stdint.h>
/* fz24_i: gen_fused24.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
static inline uint64_t nibchi(uint64_t x) {
    uint64_t y = 0;
    for (int n = 0; n < 16; n++) {
        uint64_t b = (x >> (4*n)) & 0xFu;
        uint64_t b0=(b>>0)&1u, b1=(b>>1)&1u, b2=(b>>2)&1u, b3=(b>>3)&1u;
        uint64_t y0 = b0 ^ ((~b1) & b2);
        uint64_t y1 = b1 ^ ((~b2) & b3);
        uint64_t y2 = b2 ^ ((~b3) & b0);
        uint64_t y3 = b3 ^ ((~b0) & b1);
        y |= ((y0 | (y1<<1) | (y2<<2) | (y3<<3)) << (4*n));
    }
    return y; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;

    x = x ^ nibchi(x) ^ rotl64(x,1) ^ rotl64(x,61);
    x = x ^ nibchi(x) ^ rotl64(x,1) ^ rotl64(x,61);
    x = x ^ nibchi(x) ^ rotl64(x,1) ^ rotl64(x,61);
    x = x ^ nibchi(x) ^ rotl64(x,1) ^ rotl64(x,61);
    x = x ^ nibchi(x) ^ rotl64(x,1) ^ rotl64(x,61);
    return x ^ rotl64(k, 13);
}
