#include <stdint.h>
/* fz15_d: gen_fused15.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13) ^ rotl64(x,29);
    x = x ^ (rotl64(x,5) & rotl64(x,15)) ^ rotl64(x,25) ^ rotl64(x,41);
    x = x ^ (rotl64(x,11) & rotl64(x,23)) ^ rotl64(x,37) ^ rotl64(x,53);
    x = x ^ rotl64(k, 13);
    return x;
}
