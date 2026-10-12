#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-24b guided 6-stage heterogeneous AND schedule (triage z=7.16)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,17) & rotl64(x,17)) ^ rotl64(x,26);
    x ^= (rotl64(x,41) & rotl64(x,56)) ^ rotl64(x,40);
    x ^= (rotl64(x,55) & rotl64(x,36)) ^ rotl64(x,4);
    x ^= (rotl64(x,22) & rotl64(x,4)) ^ rotl64(x,37);
    x ^= (rotl64(x,52) & rotl64(x,47));
    x ^= (rotl64(x,55) & rotl64(x,55));
    x ^= rotl64(key, 13);
    return x;
}
