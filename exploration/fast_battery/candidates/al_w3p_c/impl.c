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
// wave-14 W3 GF-diffused word-AND (screen z_seq=2.43)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,28) & rotl64(x,24));
    x ^= (rotl64(x,33) & rotl64(x,35));
    x = gf_mul(x, 0xBF58476D1CE4E5B9ULL);
    x ^= (rotl64(x,41) & rotl64(x,42));
    x ^= (rotl64(x,57) & rotl64(x,60));
    x = gf_mul(x, 0xBF58476D1CE4E5B9ULL);
    x ^= (rotl64(x,50) & rotl64(x,49));
    x ^= (rotl64(x,56) & rotl64(x,58));
    x = gf_mul(x, 0xBF58476D1CE4E5B9ULL);
    x ^= rotl64(key, 13);
    return x;
}
