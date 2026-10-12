#include <stdint.h>
/* fz23_c: gen_fused23.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ (rotl64(x,1) & rotl64(x,7)) ^ rotl64(x,13);
    x = x ^ (rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,19) ^ rotl64(x,37);
    x = x ^ (rotl64(x,5) & rotl64(x,15)) ^ rotl64(x,25);
    x = x ^ (rotl64(x,9) & rotl64(x,21)) ^ rotl64(x,31) ^ rotl64(x,49);
    x = x ^ (rotl64(x,13) & rotl64(x,27)) ^ rotl64(x,43);
    return x ^ rotl64(k, 13);
}
