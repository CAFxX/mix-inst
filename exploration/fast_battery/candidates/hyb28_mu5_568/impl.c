#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_568: batch-28 MU5 MUX-gate 5-stage cascade (triage z=5.68)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,4) & rotl64(x,60)) | (~rotl64(x,4) & rotl64(x,54))) ^ rotl64(x,56);
    x ^= ((rotl64(x,38) & rotl64(x,46)) | (~rotl64(x,38) & rotl64(x,13))) ^ rotl64(x,21);
    x ^= ((rotl64(x,38) & rotl64(x,29)) | (~rotl64(x,38) & rotl64(x,40))) ^ rotl64(x,6);
    x ^= ((rotl64(x,26) & rotl64(x,1)) | (~rotl64(x,26) & rotl64(x,49))) ^ rotl64(x,56);
    x ^= ((rotl64(x,51) & rotl64(x,30)) | (~rotl64(x,51) & rotl64(x,44))) ^ rotl64(x,61);
    x ^= rotl64(key, 13);
    return x;
}
