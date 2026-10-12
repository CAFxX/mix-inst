#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_282: batch-28 MU5 MUX-gate 5-stage cascade (triage z=2.82)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,50) & rotl64(x,57)) | (~rotl64(x,50) & rotl64(x,56))) ^ rotl64(x,12);
    x ^= ((rotl64(x,27) & rotl64(x,22)) | (~rotl64(x,27) & rotl64(x,62))) ^ rotl64(x,7);
    x ^= ((rotl64(x,18) & rotl64(x,10)) | (~rotl64(x,18) & rotl64(x,19))) ^ rotl64(x,55);
    x ^= ((rotl64(x,61) & rotl64(x,38)) | (~rotl64(x,61) & rotl64(x,36))) ^ rotl64(x,49);
    x ^= ((rotl64(x,16) & rotl64(x,26)) | (~rotl64(x,16) & rotl64(x,35))) ^ rotl64(x,59);
    x ^= rotl64(key, 13);
    return x;
}
