#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_328: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.28)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,21) & rotl64(x,19)) | (~rotl64(x,21) & rotl64(x,31))) ^ rotl64(x,24);
    x ^= ((rotl64(x,43) & rotl64(x,22)) | (~rotl64(x,43) & rotl64(x,32))) ^ rotl64(x,4);
    x ^= ((rotl64(x,22) & rotl64(x,30)) | (~rotl64(x,22) & rotl64(x,34))) ^ rotl64(x,5);
    x ^= ((rotl64(x,52) & rotl64(x,23)) | (~rotl64(x,52) & rotl64(x,60))) ^ rotl64(x,37);
    x ^= ((rotl64(x,58) & rotl64(x,62)) | (~rotl64(x,58) & rotl64(x,48))) ^ rotl64(x,11);
    x ^= rotl64(key, 13);
    return x;
}
