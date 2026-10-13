#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-40 ormM6 schedule (triage z=2.08)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,3) | rotl64(x,38)) ^ rotl64(x,25);
    x ^= (rotl64(x,47) | rotl64(x,49)) ^ rotl64(x,4);
    x ^= (rotl64(x,2) | rotl64(x,26)) ^ rotl64(x,14);
    x ^= (rotl64(x,9) | rotl64(x,45)) ^ rotl64(x,40);
    x ^= (rotl64(x,27) | rotl64(x,37)) ^ rotl64(x,47);
    x ^= (rotl64(x,39) | rotl64(x,12)) ^ rotl64(x,62);
    x ^= rotl64(key, 13);
    return x;
}
