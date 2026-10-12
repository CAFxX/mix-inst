#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_326: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.26)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,15) & rotl64(x,17)) | (~rotl64(x,15) & rotl64(x,6))) ^ rotl64(x,21);
    x ^= ((rotl64(x,44) & rotl64(x,12)) | (~rotl64(x,44) & rotl64(x,19))) ^ rotl64(x,8);
    x ^= ((rotl64(x,15) & rotl64(x,1)) | (~rotl64(x,15) & rotl64(x,31))) ^ rotl64(x,18);
    x ^= ((rotl64(x,7) & rotl64(x,36)) | (~rotl64(x,7) & rotl64(x,46))) ^ rotl64(x,55);
    x ^= ((rotl64(x,32) & rotl64(x,13)) | (~rotl64(x,32) & rotl64(x,52))) ^ rotl64(x,25);
    x ^= rotl64(key, 13);
    return x;
}
