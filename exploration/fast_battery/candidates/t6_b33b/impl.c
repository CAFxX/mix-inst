#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=3.0)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,58) & rotl64(x,53)) ^ rotl64(x,21);
    x ^= (rotl64(x,52) & rotl64(x,17)) ^ rotl64(x,18);
    x ^= (rotl64(x,25) & rotl64(x,23)) ^ rotl64(x,40);
    x ^= (rotl64(x,54) & rotl64(x,55)) ^ rotl64(x,13);
    x ^= (rotl64(x,42) & rotl64(x,33)) ^ rotl64(x,61);
    x ^= (rotl64(x,53) & rotl64(x,57)) ^ rotl64(x,29);
    x ^= rotl64(key, 13);
    return x;
}
