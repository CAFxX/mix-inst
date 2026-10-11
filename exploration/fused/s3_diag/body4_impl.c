#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ (rotl64(x,1) & rotl64(x,6)) ^ rotl64(x,13) ^ rotl64(x,31);
    x = x ^ (rotl64(x,2) & rotl64(x,13)) ^ rotl64(x,20) ^ rotl64(x,36);
    x = x ^ (rotl64(x,5) & rotl64(x,17)) ^ rotl64(x,22);
    x = x ^ (rotl64(x,10) & rotl64(x,22)) ^ rotl64(x,43);
    x = x ^ rotl64(k, 13);
    return x;
}
