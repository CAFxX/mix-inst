#include <stdint.h>
/* fz26_a: gen_fused26.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13) ^ rotl64(x,29);
    x = x ^ (rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,19) ^ rotl64(x,37);
    x = x ^ (rotl64(x,5) & rotl64(x,15)) ^ rotl64(x,21);
    x = x ^ (rotl64(x,1) & rotl64(x,7)) ^ ((~rotl64(x,13)) & rotl64(x,27)) ^ rotl64(x,41) ^ rotl64(x,53);
    return x ^ rotl64(k, 13);
}
