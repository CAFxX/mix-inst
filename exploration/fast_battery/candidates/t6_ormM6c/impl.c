#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-40 ormM6 schedule (triage z=2.37)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,55) | rotl64(x,12)) ^ rotl64(x,38);
    x ^= (rotl64(x,6) | rotl64(x,58)) ^ rotl64(x,59);
    x ^= (rotl64(x,40) | rotl64(x,34)) ^ rotl64(x,48);
    x ^= (rotl64(x,41) | rotl64(x,23)) ^ rotl64(x,17);
    x ^= (rotl64(x,12) | rotl64(x,35)) ^ rotl64(x,45);
    x ^= (rotl64(x,30) | rotl64(x,33)) ^ rotl64(x,50);
    x ^= rotl64(key, 13);
    return x;
}
