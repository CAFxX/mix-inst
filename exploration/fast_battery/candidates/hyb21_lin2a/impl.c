#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-21d proxy-guided 5-stage 1-AND+2-linear schedule (triage z=2.38)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,11) & rotl64(x,63)) ^ rotl64(x,18) ^ rotl64(x,52);
    x ^= (rotl64(x,25) & rotl64(x,8)) ^ rotl64(x,20) ^ rotl64(x,51);
    x ^= (rotl64(x,5) & rotl64(x,31)) ^ rotl64(x,14) ^ rotl64(x,34);
    x ^= (rotl64(x,50) & rotl64(x,6)) ^ rotl64(x,1) ^ rotl64(x,54);
    x ^= (rotl64(x,14) & rotl64(x,1)) ^ rotl64(x,62) ^ rotl64(x,39);
    x ^= rotl64(key, 13);
    return x;
}
