#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_266b: batch-28 MU5 MUX-gate 5-stage cascade (triage z=2.66)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,56) & rotl64(x,27)) | (~rotl64(x,56) & rotl64(x,53))) ^ rotl64(x,29);
    x ^= ((rotl64(x,48) & rotl64(x,23)) | (~rotl64(x,48) & rotl64(x,15))) ^ rotl64(x,20);
    x ^= ((rotl64(x,7) & rotl64(x,47)) | (~rotl64(x,7) & rotl64(x,2))) ^ rotl64(x,37);
    x ^= ((rotl64(x,31) & rotl64(x,16)) | (~rotl64(x,31) & rotl64(x,57))) ^ rotl64(x,30);
    x ^= ((rotl64(x,2) & rotl64(x,53)) | (~rotl64(x,2) & rotl64(x,21))) ^ rotl64(x,43);
    x ^= rotl64(key, 13);
    return x;
}
