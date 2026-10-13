#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t064 (triage z=4.072)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,46) & rotl64(x,52)) ^ rotl64(x,18);
    x ^= (rotl64(x,7) & rotl64(x,13)) ^ rotl64(x,57);
    x ^= (rotl64(x,37) & rotl64(x,36)) ^ rotl64(x,51);
    x ^= (rotl64(x,24) & rotl64(x,19)) ^ rotl64(x,32);
    x ^= (rotl64(x,12) & rotl64(x,48)) ^ rotl64(x,21);
    x ^= (rotl64(x,37) & rotl64(x,33)) ^ rotl64(x,15);
    x ^= rotl64(key, 13);
    return x;
}
