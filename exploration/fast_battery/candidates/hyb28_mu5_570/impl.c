#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_570: batch-28 MU5 MUX-gate 5-stage cascade (triage z=5.70)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,10) & rotl64(x,29)) | (~rotl64(x,10) & rotl64(x,11))) ^ rotl64(x,6);
    x ^= ((rotl64(x,6) & rotl64(x,37)) | (~rotl64(x,6) & rotl64(x,54))) ^ rotl64(x,21);
    x ^= ((rotl64(x,56) & rotl64(x,62)) | (~rotl64(x,56) & rotl64(x,48))) ^ rotl64(x,1);
    x ^= ((rotl64(x,26) & rotl64(x,39)) | (~rotl64(x,26) & rotl64(x,46))) ^ rotl64(x,13);
    x ^= ((rotl64(x,1) & rotl64(x,38)) | (~rotl64(x,1) & rotl64(x,53))) ^ rotl64(x,32);
    x ^= rotl64(key, 13);
    return x;
}
