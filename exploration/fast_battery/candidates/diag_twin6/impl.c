#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1) & rotl64(x,2)) ^ (rotl64(x,7) & rotl64(x,19));
    x ^= (rotl64(x,7) & rotl64(x,19)) ^ (rotl64(x,3) & rotl64(x,11));
    x ^= (rotl64(x,3) & rotl64(x,11)) ^ (rotl64(x,17) & rotl64(x,31));
    x ^= (rotl64(x,17) & rotl64(x,31)) ^ (rotl64(x,11) & rotl64(x,23));
    x ^= (rotl64(x,11) & rotl64(x,23)) ^ (rotl64(x,19) & rotl64(x,41));
    x ^= (rotl64(x,19) & rotl64(x,41)) ^ (rotl64(x,1) & rotl64(x,2));
    x ^= rotl64(key, 13);
    return x;
}