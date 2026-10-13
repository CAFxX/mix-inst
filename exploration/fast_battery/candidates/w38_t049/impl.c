#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t049 (triage z=4.095)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,24) & rotl64(x,31)) ^ rotl64(x,28);
    x ^= (rotl64(x,43) & rotl64(x,41)) ^ rotl64(x,22);
    x ^= (rotl64(x,36) & rotl64(x,34)) ^ rotl64(x,19);
    x ^= (rotl64(x,9) & rotl64(x,7)) ^ rotl64(x,42);
    x ^= (rotl64(x,10) & rotl64(x,15)) ^ rotl64(x,38);
    x ^= (rotl64(x,26) & rotl64(x,23)) ^ rotl64(x,14);
    x ^= rotl64(key, 13);
    return x;
}
