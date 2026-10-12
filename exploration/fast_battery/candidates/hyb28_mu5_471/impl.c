#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_471: batch-28 MU5 MUX-gate 5-stage cascade (triage z=4.71)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,45) & rotl64(x,39)) | (~rotl64(x,45) & rotl64(x,27))) ^ rotl64(x,54);
    x ^= ((rotl64(x,41) & rotl64(x,18)) | (~rotl64(x,41) & rotl64(x,60))) ^ rotl64(x,20);
    x ^= ((rotl64(x,56) & rotl64(x,32)) | (~rotl64(x,56) & rotl64(x,20))) ^ rotl64(x,61);
    x ^= ((rotl64(x,62) & rotl64(x,28)) | (~rotl64(x,62) & rotl64(x,5))) ^ rotl64(x,23);
    x ^= ((rotl64(x,44) & rotl64(x,62)) | (~rotl64(x,44) & rotl64(x,41))) ^ rotl64(x,10);
    x ^= rotl64(key, 13);
    return x;
}
