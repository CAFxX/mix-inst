#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t104 (triage z=6.239)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,6) & rotl64(x,15)) ^ rotl64(x,28);
    x ^= (rotl64(x,6) & rotl64(x,19)) ^ rotl64(x,16);
    x ^= (rotl64(x,60) & rotl64(x,11)) ^ rotl64(x,9);
    x ^= (rotl64(x,11) & rotl64(x,28)) ^ rotl64(x,60);
    x ^= (rotl64(x,24) & rotl64(x,13)) ^ rotl64(x,4);
    x ^= (rotl64(x,61) & rotl64(x,3)) ^ rotl64(x,14);
    x ^= rotl64(key, 13);
    return x;
}
