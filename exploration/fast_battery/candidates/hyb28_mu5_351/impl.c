#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_351: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.51)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,3) & rotl64(x,63)) | (~rotl64(x,3) & rotl64(x,49))) ^ rotl64(x,36);
    x ^= ((rotl64(x,23) & rotl64(x,17)) | (~rotl64(x,23) & rotl64(x,51))) ^ rotl64(x,55);
    x ^= ((rotl64(x,53) & rotl64(x,38)) | (~rotl64(x,53) & rotl64(x,14))) ^ rotl64(x,9);
    x ^= ((rotl64(x,20) & rotl64(x,2)) | (~rotl64(x,20) & rotl64(x,35))) ^ rotl64(x,25);
    x ^= ((rotl64(x,5) & rotl64(x,50)) | (~rotl64(x,5) & rotl64(x,59))) ^ rotl64(x,52);
    x ^= rotl64(key, 13);
    return x;
}
