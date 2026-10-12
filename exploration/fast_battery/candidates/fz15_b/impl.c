#include <stdint.h>
/* fz15_b: gen_fused15.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ (rotl64(x,2) & rotl64(x,9)) ^ rotl64(x,17) ^ rotl64(x,33);
    x = x ^ (rotl64(x,5) & rotl64(x,13)) ^ rotl64(x,21) ^ rotl64(x,39);
    x = x ^ (rotl64(x,9) & rotl64(x,19)) ^ rotl64(x,27) ^ rotl64(x,45);
    x = x ^ (rotl64(x,13) & rotl64(x,27)) ^ rotl64(x,35) ^ rotl64(x,53);
    x = x ^ rotl64(k, 13);
    return x;
}
