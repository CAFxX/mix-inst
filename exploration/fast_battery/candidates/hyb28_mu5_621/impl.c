#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_621: batch-28 MU5 MUX-gate 5-stage cascade (triage z=6.21)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,29) & rotl64(x,13)) | (~rotl64(x,29) & rotl64(x,17))) ^ rotl64(x,8);
    x ^= ((rotl64(x,46) & rotl64(x,33)) | (~rotl64(x,46) & rotl64(x,51))) ^ rotl64(x,2);
    x ^= ((rotl64(x,62) & rotl64(x,17)) | (~rotl64(x,62) & rotl64(x,32))) ^ rotl64(x,35);
    x ^= ((rotl64(x,19) & rotl64(x,3)) | (~rotl64(x,19) & rotl64(x,29))) ^ rotl64(x,9);
    x ^= ((rotl64(x,37) & rotl64(x,30)) | (~rotl64(x,37) & rotl64(x,36))) ^ rotl64(x,35);
    x ^= rotl64(key, 13);
    return x;
}
