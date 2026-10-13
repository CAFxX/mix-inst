#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-44 andorM6 schedule (triage z=3.31)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,31) & rotl64(x,12)) ^ (rotl64(x,58) | rotl64(x,39));
    x ^= (rotl64(x,54) & rotl64(x,57)) ^ (rotl64(x,4) | rotl64(x,32));
    x ^= (rotl64(x,6) & rotl64(x,4)) ^ (rotl64(x,33) | rotl64(x,42));
    x ^= (rotl64(x,54) & rotl64(x,10)) ^ (rotl64(x,8) | rotl64(x,59));
    x ^= (rotl64(x,38) & rotl64(x,45)) ^ (rotl64(x,41) | rotl64(x,27));
    x ^= (rotl64(x,9) & rotl64(x,43)) ^ (rotl64(x,53) | rotl64(x,44));
    x ^= rotl64(key, 13);
    return x;
}
