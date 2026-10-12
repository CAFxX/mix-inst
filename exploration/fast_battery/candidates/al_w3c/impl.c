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
// wave-14 W3 GF-diffused word-AND (screen z_seq=2.63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,59) & rotl64(x,43));
    x ^= (rotl64(x,24) & rotl64(x,38));
    x = gf_mul(x, 0x94D049BB133111EBULL);
    x ^= (rotl64(x,28) & rotl64(x,49));
    x ^= (rotl64(x,17) & rotl64(x,15));
    x = gf_mul(x, 0x94D049BB133111EBULL);
    x ^= rotl64(key, 13);
    return x;
}
