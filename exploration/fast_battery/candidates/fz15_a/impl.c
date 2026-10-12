#include <stdint.h>
/* fz15_a: gen_fused15.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13) ^ rotl64(x,29);
    x = x ^ (rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,19) ^ rotl64(x,37);
    x = x ^ (rotl64(x,7) & rotl64(x,17)) ^ rotl64(x,23) ^ rotl64(x,43);
    x = x ^ (rotl64(x,11) & rotl64(x,23)) ^ rotl64(x,31) ^ rotl64(x,47);
    x = x ^ rotl64(k, 13);
    return x;
}
