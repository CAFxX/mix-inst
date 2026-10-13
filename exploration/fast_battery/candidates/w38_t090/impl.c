#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t090 (triage z=5.280)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,57) & rotl64(x,34)) ^ rotl64(x,29);
    x ^= (rotl64(x,57) & rotl64(x,10)) ^ rotl64(x,49);
    x ^= (rotl64(x,26) & rotl64(x,3)) ^ rotl64(x,36);
    x ^= (rotl64(x,4) & rotl64(x,20)) ^ rotl64(x,8);
    x ^= (rotl64(x,45) & rotl64(x,39)) ^ rotl64(x,54);
    x ^= (rotl64(x,1) & rotl64(x,59)) ^ rotl64(x,44);
    x ^= rotl64(key, 13);
    return x;
}
