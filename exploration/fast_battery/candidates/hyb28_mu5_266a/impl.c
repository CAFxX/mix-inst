#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_266a: batch-28 MU5 MUX-gate 5-stage cascade (triage z=2.66)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,24) & rotl64(x,19)) | (~rotl64(x,24) & rotl64(x,61))) ^ rotl64(x,46);
    x ^= ((rotl64(x,20) & rotl64(x,12)) | (~rotl64(x,20) & rotl64(x,30))) ^ rotl64(x,22);
    x ^= ((rotl64(x,4) & rotl64(x,45)) | (~rotl64(x,4) & rotl64(x,56))) ^ rotl64(x,31);
    x ^= ((rotl64(x,53) & rotl64(x,48)) | (~rotl64(x,53) & rotl64(x,18))) ^ rotl64(x,32);
    x ^= ((rotl64(x,46) & rotl64(x,3)) | (~rotl64(x,46) & rotl64(x,37))) ^ rotl64(x,49);
    x ^= rotl64(key, 13);
    return x;
}
