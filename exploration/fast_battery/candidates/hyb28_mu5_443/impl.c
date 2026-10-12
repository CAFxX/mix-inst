#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_443: batch-28 MU5 MUX-gate 5-stage cascade (triage z=4.43)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,36) & rotl64(x,29)) | (~rotl64(x,36) & rotl64(x,27))) ^ rotl64(x,48);
    x ^= ((rotl64(x,32) & rotl64(x,8)) | (~rotl64(x,32) & rotl64(x,56))) ^ rotl64(x,50);
    x ^= ((rotl64(x,50) & rotl64(x,25)) | (~rotl64(x,50) & rotl64(x,27))) ^ rotl64(x,63);
    x ^= ((rotl64(x,24) & rotl64(x,56)) | (~rotl64(x,24) & rotl64(x,2))) ^ rotl64(x,54);
    x ^= ((rotl64(x,43) & rotl64(x,51)) | (~rotl64(x,43) & rotl64(x,16))) ^ rotl64(x,5);
    x ^= rotl64(key, 13);
    return x;
}
