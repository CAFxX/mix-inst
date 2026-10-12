#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb28_mu5_234: batch-28 MU5 MUX-gate 5-stage cascade (triage z=2.34)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,48) & rotl64(x,8)) | (~rotl64(x,48) & rotl64(x,49))) ^ rotl64(x,10);
    x ^= ((rotl64(x,42) & rotl64(x,41)) | (~rotl64(x,42) & rotl64(x,48))) ^ rotl64(x,55);
    x ^= ((rotl64(x,5) & rotl64(x,45)) | (~rotl64(x,5) & rotl64(x,43))) ^ rotl64(x,14);
    x ^= ((rotl64(x,49) & rotl64(x,12)) | (~rotl64(x,49) & rotl64(x,1))) ^ rotl64(x,63);
    x ^= ((rotl64(x,31) & rotl64(x,2)) | (~rotl64(x,31) & rotl64(x,16))) ^ rotl64(x,39);
    x ^= rotl64(key, 13);
    return x;
}
