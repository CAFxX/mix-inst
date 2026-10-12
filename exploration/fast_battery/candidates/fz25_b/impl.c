#include <stdint.h>
/* fz25_b: gen_fused25.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    uint64_t p = rotl64(x, 7) ^ rotl64(x, 41);
    x = x ^ (rotl64(x,2) & rotl64(x,9)) ^ rotl64(p,0);
    x = x ^ (rotl64(x,4) & rotl64(x,13)) ^ rotl64(p,17);
    x = x ^ (rotl64(x,6) & rotl64(x,17)) ^ rotl64(p,33);
    x = x ^ (rotl64(x,11) & rotl64(x,23)) ^ rotl64(p,11);
    x = x ^ (rotl64(x,15) & rotl64(x,27)) ^ rotl64(p,47);
    return x ^ rotl64(k, 13);
}
