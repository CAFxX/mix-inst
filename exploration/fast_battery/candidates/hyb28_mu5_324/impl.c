#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_324: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.24)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,62) & rotl64(x,50)) | (~rotl64(x,62) & rotl64(x,55))) ^ rotl64(x,2);
    x ^= ((rotl64(x,48) & rotl64(x,58)) | (~rotl64(x,48) & rotl64(x,23))) ^ rotl64(x,30);
    x ^= ((rotl64(x,44) & rotl64(x,45)) | (~rotl64(x,44) & rotl64(x,7))) ^ rotl64(x,40);
    x ^= ((rotl64(x,49) & rotl64(x,26)) | (~rotl64(x,49) & rotl64(x,32))) ^ rotl64(x,35);
    x ^= ((rotl64(x,46) & rotl64(x,51)) | (~rotl64(x,46) & rotl64(x,43))) ^ rotl64(x,44);
    x ^= rotl64(key, 13);
    return x;
}
