#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_304a: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.04)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,39) & rotl64(x,27)) | (~rotl64(x,39) & rotl64(x,37))) ^ rotl64(x,26);
    x ^= ((rotl64(x,15) & rotl64(x,33)) | (~rotl64(x,15) & rotl64(x,52))) ^ rotl64(x,28);
    x ^= ((rotl64(x,37) & rotl64(x,33)) | (~rotl64(x,37) & rotl64(x,7))) ^ rotl64(x,10);
    x ^= ((rotl64(x,56) & rotl64(x,2)) | (~rotl64(x,56) & rotl64(x,58))) ^ rotl64(x,50);
    x ^= ((rotl64(x,53) & rotl64(x,24)) | (~rotl64(x,53) & rotl64(x,37))) ^ rotl64(x,9);
    x ^= rotl64(key, 13);
    return x;
}
