#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=3.3)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,25) & rotl64(x,45)) ^ rotl64(x,42);
    x ^= (rotl64(x,44) & rotl64(x,14)) ^ rotl64(x,26);
    x ^= (rotl64(x,51) & rotl64(x,54)) ^ rotl64(x,34);
    x ^= (rotl64(x,41) & rotl64(x,53)) ^ rotl64(x,51);
    x ^= (rotl64(x,54) & rotl64(x,40)) ^ rotl64(x,6);
    x ^= (rotl64(x,12) & rotl64(x,15)) ^ rotl64(x,11);
    x ^= rotl64(key, 13);
    return x;
}
