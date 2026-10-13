#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=6.9)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,25) & rotl64(x,44)) ^ rotl64(x,8);
    x ^= (rotl64(x,27) & rotl64(x,40)) ^ rotl64(x,37);
    x ^= (rotl64(x,63) & rotl64(x,5)) ^ rotl64(x,39);
    x ^= (rotl64(x,11) & rotl64(x,22)) ^ rotl64(x,6);
    x ^= (rotl64(x,29) & rotl64(x,7)) ^ rotl64(x,21);
    x ^= (rotl64(x,12) & rotl64(x,3)) ^ rotl64(x,44);
    x ^= rotl64(key, 13);
    return x;
}
