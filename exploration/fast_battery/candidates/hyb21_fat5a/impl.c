#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-21b proxy-guided 5-stage fat-AND schedule (triage z=2.42)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,11) & rotl64(x,6)) ^ (rotl64(x,25) & rotl64(x,13)) ^ rotl64(x,30);
    x ^= (rotl64(x,16) & rotl64(x,7)) ^ (rotl64(x,24) & rotl64(x,23)) ^ rotl64(x,31);
    x ^= (rotl64(x,22) & rotl64(x,18)) ^ (rotl64(x,3) & rotl64(x,14)) ^ rotl64(x,38);
    x ^= (rotl64(x,7) & rotl64(x,28)) ^ (rotl64(x,14) & rotl64(x,15)) ^ rotl64(x,10);
    x ^= (rotl64(x,11) & rotl64(x,34)) ^ (rotl64(x,19) & rotl64(x,38)) ^ rotl64(x,5);
    x ^= rotl64(key, 13);
    return x;
}
