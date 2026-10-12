#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_325: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.25)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,39) & rotl64(x,61)) | (~rotl64(x,39) & rotl64(x,24))) ^ rotl64(x,4);
    x ^= ((rotl64(x,57) & rotl64(x,43)) | (~rotl64(x,57) & rotl64(x,58))) ^ rotl64(x,6);
    x ^= ((rotl64(x,36) & rotl64(x,24)) | (~rotl64(x,36) & rotl64(x,20))) ^ rotl64(x,40);
    x ^= ((rotl64(x,53) & rotl64(x,23)) | (~rotl64(x,53) & rotl64(x,47))) ^ rotl64(x,12);
    x ^= ((rotl64(x,17) & rotl64(x,60)) | (~rotl64(x,17) & rotl64(x,49))) ^ rotl64(x,18);
    x ^= rotl64(key, 13);
    return x;
}
