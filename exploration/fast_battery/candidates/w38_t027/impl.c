#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t027 (triage z=4.776)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,23) & rotl64(x,38)) ^ rotl64(x,26);
    x ^= (rotl64(x,43) & rotl64(x,36)) ^ rotl64(x,54);
    x ^= (rotl64(x,12) & rotl64(x,61)) ^ rotl64(x,30);
    x ^= (rotl64(x,44) & rotl64(x,2)) ^ rotl64(x,45);
    x ^= (rotl64(x,60) & rotl64(x,16)) ^ rotl64(x,18);
    x ^= (rotl64(x,49) & rotl64(x,20)) ^ rotl64(x,31);
    x ^= rotl64(key, 13);
    return x;
}
