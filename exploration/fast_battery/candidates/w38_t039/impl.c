#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t039 (triage z=2.580)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,30) & rotl64(x,59)) ^ rotl64(x,16);
    x ^= (rotl64(x,49) & rotl64(x,3)) ^ rotl64(x,59);
    x ^= (rotl64(x,16) & rotl64(x,44)) ^ rotl64(x,18);
    x ^= (rotl64(x,45) & rotl64(x,28)) ^ rotl64(x,60);
    x ^= (rotl64(x,23) & rotl64(x,42)) ^ rotl64(x,21);
    x ^= (rotl64(x,18) & rotl64(x,59)) ^ rotl64(x,8);
    x ^= rotl64(key, 13);
    return x;
}
