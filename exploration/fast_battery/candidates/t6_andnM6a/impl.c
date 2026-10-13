#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-39 andnM6 schedule (triage z=2.2)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,21) & ~rotl64(x,17)) ^ rotl64(x,43);
    x ^= (rotl64(x,5) & ~rotl64(x,37)) ^ rotl64(x,27);
    x ^= (rotl64(x,32) & ~rotl64(x,3)) ^ rotl64(x,56);
    x ^= (rotl64(x,32) & ~rotl64(x,43)) ^ rotl64(x,18);
    x ^= (rotl64(x,49) & ~rotl64(x,31)) ^ rotl64(x,44);
    x ^= (rotl64(x,28) & ~rotl64(x,19)) ^ rotl64(x,7);
    x ^= rotl64(key, 13);
    return x;
}
