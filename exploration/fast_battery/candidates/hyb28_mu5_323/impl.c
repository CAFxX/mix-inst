#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_323: batch-28 MU5 MUX-gate 5-stage cascade (triage z=3.23)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,30) & rotl64(x,57)) | (~rotl64(x,30) & rotl64(x,51))) ^ rotl64(x,25);
    x ^= ((rotl64(x,6) & rotl64(x,9)) | (~rotl64(x,6) & rotl64(x,47))) ^ rotl64(x,23);
    x ^= ((rotl64(x,33) & rotl64(x,60)) | (~rotl64(x,33) & rotl64(x,9))) ^ rotl64(x,58);
    x ^= ((rotl64(x,8) & rotl64(x,5)) | (~rotl64(x,8) & rotl64(x,36))) ^ rotl64(x,31);
    x ^= ((rotl64(x,27) & rotl64(x,16)) | (~rotl64(x,27) & rotl64(x,51))) ^ rotl64(x,37);
    x ^= rotl64(key, 13);
    return x;
}
