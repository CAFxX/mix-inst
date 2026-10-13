#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// chi_3 S-box, 21 contiguous 3-bit lanes, bit 63 identity (b42)
static inline uint64_t chi3(uint64_t x) {
    uint64_t m0 = 0x9249249249249249ULL & 0x7FFFFFFFFFFFFFFFULL;
    uint64_t m1 = 0x2492492492492492ULL;
    uint64_t m2 = 0x4924924924924924ULL;
    uint64_t y0 = (x & m0) ^ ((~(x >> 1) & m0) & ((x >> 2) & m0));
    uint64_t y1 = (x & m1) ^ ((~(x >> 1) & m1) & ((x << 1) & m1));
    uint64_t y2 = (x & m2) ^ ((~(x << 2) & m2) & ((x << 1) & m2));
    return y0 | y1 | y2 | (x & 0x8000000000000000ULL);
}
// batch-45 chiS4 schedule (triage z=2.82)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t y;
    y = chi3(x); x = y ^ rotl64(y,23) ^ rotl64(y,13);
    y = chi3(x); x = y ^ rotl64(y,28) ^ rotl64(y,7);
    y = chi3(x); x = y ^ rotl64(y,45) ^ rotl64(y,60);
    y = chi3(x); x = y ^ rotl64(y,29) ^ rotl64(y,59);
    x ^= rotl64(key, 13);
    return x;
}
