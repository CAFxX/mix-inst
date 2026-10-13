#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-40 ormM6 schedule (triage z=2.22)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,31) | rotl64(x,20)) ^ rotl64(x,53);
    x ^= (rotl64(x,29) | rotl64(x,23)) ^ rotl64(x,63);
    x ^= (rotl64(x,50) | rotl64(x,55)) ^ rotl64(x,62);
    x ^= (rotl64(x,45) | rotl64(x,61)) ^ rotl64(x,5);
    x ^= (rotl64(x,16) | rotl64(x,49)) ^ rotl64(x,37);
    x ^= (rotl64(x,37) | rotl64(x,16)) ^ rotl64(x,14);
    x ^= rotl64(key, 13);
    return x;
}
