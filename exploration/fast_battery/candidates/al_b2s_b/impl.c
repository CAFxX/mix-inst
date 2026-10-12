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
// (b2) sparse-GF: 3st d-constrained word-AND, cheap linear pq=(52,1), one gf_mul at end
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,6) & rotl64(x,2));
    x ^= (rotl64(x,44) & rotl64(x,46));
    x ^= rotl64(x,52) ^ rotl64(x,1);
    x ^= (rotl64(x,34) & rotl64(x,32));
    x ^= (rotl64(x,38) & rotl64(x,39));
    x ^= rotl64(x,52) ^ rotl64(x,1);
    x ^= (rotl64(x,52) & rotl64(x,54));
    x ^= (rotl64(x,24) & rotl64(x,21));
    x ^= rotl64(x,52) ^ rotl64(x,1);
    x = gf_mul(x, 0x94D049BB133111EBULL);
    x ^= rotl64(key, 13);
    return x;
}
