#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-21d proxy-guided 5-stage 1-AND+2-linear schedule (triage z=2.48)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,29) & rotl64(x,54)) ^ rotl64(x,38) ^ rotl64(x,39);
    x ^= (rotl64(x,10) & rotl64(x,4)) ^ rotl64(x,46) ^ rotl64(x,6);
    x ^= (rotl64(x,37) & rotl64(x,5)) ^ rotl64(x,57) ^ rotl64(x,49);
    x ^= (rotl64(x,10) & rotl64(x,29)) ^ rotl64(x,35) ^ rotl64(x,33);
    x ^= (rotl64(x,30) & rotl64(x,17)) ^ rotl64(x,44) ^ rotl64(x,50);
    x ^= rotl64(key, 13);
    return x;
}
