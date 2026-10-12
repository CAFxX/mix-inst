#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_304b: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.04)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,33) & rotl64(x,48)) | (~rotl64(x,33) & rotl64(x,16))) ^ rotl64(x,39);
    x ^= ((rotl64(x,54) & rotl64(x,60)) | (~rotl64(x,54) & rotl64(x,51))) ^ rotl64(x,44);
    x ^= ((rotl64(x,34) & rotl64(x,37)) | (~rotl64(x,34) & rotl64(x,30))) ^ rotl64(x,3);
    x ^= ((rotl64(x,48) & rotl64(x,19)) | (~rotl64(x,48) & rotl64(x,43))) ^ rotl64(x,26);
    x ^= ((rotl64(x,42) & rotl64(x,33)) | (~rotl64(x,42) & rotl64(x,61))) ^ rotl64(x,32);
    x ^= rotl64(key, 13);
    return x;
}
