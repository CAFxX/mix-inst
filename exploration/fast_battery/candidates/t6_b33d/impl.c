#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=3.4)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,38) & rotl64(x,34)) ^ rotl64(x,15);
    x ^= (rotl64(x,47) & rotl64(x,35)) ^ rotl64(x,33);
    x ^= (rotl64(x,47) & rotl64(x,2)) ^ rotl64(x,23);
    x ^= (rotl64(x,16) & rotl64(x,11)) ^ rotl64(x,60);
    x ^= (rotl64(x,19) & rotl64(x,5)) ^ rotl64(x,44);
    x ^= (rotl64(x,18) & rotl64(x,42)) ^ rotl64(x,41);
    x ^= rotl64(key, 13);
    return x;
}
