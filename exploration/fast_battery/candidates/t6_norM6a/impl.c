#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-41 norM schedule (triage z=2.76)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (~(rotl64(x,49) | rotl64(x,51))) ^ rotl64(x,17);
    x ^= (~(rotl64(x,41) | rotl64(x,61))) ^ rotl64(x,26);
    x ^= (~(rotl64(x,23) | rotl64(x,37))) ^ rotl64(x,34);
    x ^= (~(rotl64(x,63) | rotl64(x,34))) ^ rotl64(x,30);
    x ^= (~(rotl64(x,59) | rotl64(x,40))) ^ rotl64(x,31);
    x ^= (~(rotl64(x,20) | rotl64(x,1))) ^ rotl64(x,12);
    x ^= rotl64(key, 13);
    return x;
}
