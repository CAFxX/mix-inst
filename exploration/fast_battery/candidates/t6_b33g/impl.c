#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-33 proxy-guided 6-stage AND schedule (triage z=8.3)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,21) & rotl64(x,46)) ^ rotl64(x,53);
    x ^= (rotl64(x,29) & rotl64(x,16)) ^ rotl64(x,38);
    x ^= (rotl64(x,57) & rotl64(x,4)) ^ rotl64(x,18);
    x ^= (rotl64(x,5) & rotl64(x,59)) ^ rotl64(x,5);
    x ^= (rotl64(x,12) & rotl64(x,41)) ^ rotl64(x,31);
    x ^= (rotl64(x,23) & rotl64(x,11)) ^ rotl64(x,51);
    x ^= rotl64(key, 13);
    return x;
}
