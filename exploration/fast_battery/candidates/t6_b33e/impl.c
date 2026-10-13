#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=5.7)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,57) & rotl64(x,43)) ^ rotl64(x,8);
    x ^= (rotl64(x,41) & rotl64(x,50)) ^ rotl64(x,24);
    x ^= (rotl64(x,52) & rotl64(x,3)) ^ rotl64(x,22);
    x ^= (rotl64(x,36) & rotl64(x,32)) ^ rotl64(x,21);
    x ^= (rotl64(x,41) & rotl64(x,56)) ^ rotl64(x,10);
    x ^= (rotl64(x,54) & rotl64(x,56)) ^ rotl64(x,22);
    x ^= rotl64(key, 13);
    return x;
}
