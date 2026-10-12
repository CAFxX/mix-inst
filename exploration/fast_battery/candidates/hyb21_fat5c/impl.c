#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-21b proxy-guided 5-stage fat-AND schedule (triage z=2.59)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,38) & rotl64(x,34)) ^ (rotl64(x,14) & rotl64(x,20)) ^ rotl64(x,4);
    x ^= (rotl64(x,55) & rotl64(x,5)) ^ (rotl64(x,6) & rotl64(x,57)) ^ rotl64(x,23);
    x ^= (rotl64(x,19) & rotl64(x,38)) ^ (rotl64(x,23) & rotl64(x,53)) ^ rotl64(x,30);
    x ^= (rotl64(x,53) & rotl64(x,6)) ^ (rotl64(x,5) & rotl64(x,2)) ^ rotl64(x,44);
    x ^= (rotl64(x,37) & rotl64(x,47)) ^ (rotl64(x,16) & rotl64(x,6)) ^ rotl64(x,35);
    x ^= rotl64(key, 13);
    return x;
}
