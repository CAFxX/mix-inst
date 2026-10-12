#include <stdint.h>
/* fz16_d: gen_fused16.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ ((rotl64(x,1) & rotl64(x,5)) ^ rotl64(x,9) ^ rotl64(x,13));
    x = x ^ ((rotl64(x,2) & rotl64(x,6)) ^ rotl64(x,11) ^ rotl64(x,17));
    x = x ^ ((rotl64(x,3) & rotl64(x,8)) ^ rotl64(x,14) ^ rotl64(x,19));
    x = x ^ ((rotl64(x,5) & rotl64(x,11)) ^ rotl64(x,18) ^ rotl64(x,23));
    x = x ^ ((rotl64(x,7) & rotl64(x,13)) ^ rotl64(x,21) ^ rotl64(x,27));
    x = x ^ rotl64(k, 13);
    return x;
}
