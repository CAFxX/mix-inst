#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_339: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.39)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,20) & rotl64(x,10)) | (~rotl64(x,20) & rotl64(x,14))) ^ rotl64(x,12);
    x ^= ((rotl64(x,49) & rotl64(x,13)) | (~rotl64(x,49) & rotl64(x,53))) ^ rotl64(x,33);
    x ^= ((rotl64(x,43) & rotl64(x,38)) | (~rotl64(x,43) & rotl64(x,45))) ^ rotl64(x,24);
    x ^= ((rotl64(x,60) & rotl64(x,17)) | (~rotl64(x,60) & rotl64(x,62))) ^ rotl64(x,25);
    x ^= ((rotl64(x,46) & rotl64(x,52)) | (~rotl64(x,46) & rotl64(x,8))) ^ rotl64(x,32);
    x ^= rotl64(key, 13);
    return x;
}
