#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_480: batch-28 MU5 MUX-gate 5-stage cascade (triage z=4.80)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,46) & rotl64(x,42)) | (~rotl64(x,46) & rotl64(x,28))) ^ rotl64(x,52);
    x ^= ((rotl64(x,15) & rotl64(x,56)) | (~rotl64(x,15) & rotl64(x,50))) ^ rotl64(x,25);
    x ^= ((rotl64(x,18) & rotl64(x,41)) | (~rotl64(x,18) & rotl64(x,32))) ^ rotl64(x,24);
    x ^= ((rotl64(x,50) & rotl64(x,26)) | (~rotl64(x,50) & rotl64(x,35))) ^ rotl64(x,46);
    x ^= ((rotl64(x,12) & rotl64(x,16)) | (~rotl64(x,12) & rotl64(x,4))) ^ rotl64(x,21);
    x ^= rotl64(key, 13);
    return x;
}
