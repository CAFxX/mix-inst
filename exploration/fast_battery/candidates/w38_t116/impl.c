#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t116 (triage z=9.833)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,7) & rotl64(x,37)) ^ rotl64(x,38);
    x ^= (rotl64(x,56) & rotl64(x,6)) ^ rotl64(x,31);
    x ^= (rotl64(x,7) & rotl64(x,8)) ^ rotl64(x,61);
    x ^= (rotl64(x,8) & rotl64(x,34)) ^ rotl64(x,50);
    x ^= (rotl64(x,6) & rotl64(x,23)) ^ rotl64(x,18);
    x ^= (rotl64(x,16) & rotl64(x,37)) ^ rotl64(x,23);
    x ^= rotl64(key, 13);
    return x;
}
