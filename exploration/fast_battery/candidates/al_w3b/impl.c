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
// wave-14 W3 GF-diffused word-AND (screen z_seq=2.54)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,47) & rotl64(x,35));
    x ^= (rotl64(x,55) & rotl64(x,47));
    x = gf_mul(x, 0x9E3779B97F4A7C15ULL);
    x ^= (rotl64(x,13) & rotl64(x,3));
    x ^= (rotl64(x,31) & rotl64(x,26));
    x = gf_mul(x, 0x9E3779B97F4A7C15ULL);
    x ^= rotl64(key, 13);
    return x;
}
