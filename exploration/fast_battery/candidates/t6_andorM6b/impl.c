#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-44 andorM6 schedule (triage z=9.13)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,3) & rotl64(x,30)) ^ (rotl64(x,58) | rotl64(x,5));
    x ^= (rotl64(x,62) & rotl64(x,35)) ^ (rotl64(x,52) | rotl64(x,23));
    x ^= (rotl64(x,13) & rotl64(x,20)) ^ (rotl64(x,44) | rotl64(x,43));
    x ^= (rotl64(x,13) & rotl64(x,51)) ^ (rotl64(x,41) | rotl64(x,25));
    x ^= (rotl64(x,35) & rotl64(x,47)) ^ (rotl64(x,63) | rotl64(x,34));
    x ^= (rotl64(x,30) & rotl64(x,19)) ^ (rotl64(x,12) | rotl64(x,59));
    x ^= rotl64(key, 13);
    return x;
}
