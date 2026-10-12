#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static uint64_t gf_mul(uint64_t a, uint64_t C) {
    uint64_t res = 0, p = a;
    while (C) {
        if (C & 1) res ^= p;
        uint64_t hi = p >> 63;
        p = (p << 1) ^ (hi ? 0x1BULL : 0ULL);
        C >>= 1;
    }
    return res;
}
// (b2) sparse-GF: 3st d-constrained word-AND, cheap linear pq=(30,60), one gf_mul at end
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,11) & rotl64(x,12));
    x ^= (rotl64(x,20) & rotl64(x,24));
    x ^= rotl64(x,30) ^ rotl64(x,60);
    x ^= (rotl64(x,3) & rotl64(x,7));
    x ^= (rotl64(x,24) & rotl64(x,27));
    x ^= rotl64(x,30) ^ rotl64(x,60);
    x ^= (rotl64(x,46) & rotl64(x,48));
    x ^= (rotl64(x,7) & rotl64(x,3));
    x ^= rotl64(x,30) ^ rotl64(x,60);
    x = gf_mul(x, 0x94D049BB133111EBULL);
    x ^= rotl64(key, 13);
    return x;
}
