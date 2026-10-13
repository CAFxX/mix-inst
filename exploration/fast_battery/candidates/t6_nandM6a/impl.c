#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-41 nandM schedule (triage z=2.15)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (~(rotl64(x,22) & rotl64(x,45))) ^ rotl64(x,18);
    x ^= (~(rotl64(x,29) & rotl64(x,60))) ^ rotl64(x,15);
    x ^= (~(rotl64(x,39) & rotl64(x,29))) ^ rotl64(x,41);
    x ^= (~(rotl64(x,49) & rotl64(x,7))) ^ rotl64(x,38);
    x ^= (~(rotl64(x,35) & rotl64(x,24))) ^ rotl64(x,53);
    x ^= (~(rotl64(x,62) & rotl64(x,22))) ^ rotl64(x,2);
    x ^= rotl64(key, 13);
    return x;
}
