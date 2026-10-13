#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=2.6)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,37) & rotl64(x,43)) ^ rotl64(x,51);
    x ^= (rotl64(x,12) & rotl64(x,11)) ^ rotl64(x,63);
    x ^= (rotl64(x,28) & rotl64(x,33)) ^ rotl64(x,27);
    x ^= (rotl64(x,63) & rotl64(x,2)) ^ rotl64(x,57);
    x ^= (rotl64(x,4) & rotl64(x,14)) ^ rotl64(x,1);
    x ^= (rotl64(x,18) & rotl64(x,17)) ^ rotl64(x,40);
    x ^= rotl64(key, 13);
    return x;
}
