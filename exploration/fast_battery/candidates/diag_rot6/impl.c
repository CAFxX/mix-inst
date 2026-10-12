#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= rotl64(x,9) ^ rotl64(x,27);
    x ^= rotl64(x,15) ^ rotl64(x,33);
    x ^= rotl64(x,21) ^ rotl64(x,39);
    x ^= rotl64(x,27) ^ rotl64(x,45);
    x ^= rotl64(x,33) ^ rotl64(x,51);
    x ^= rotl64(x,39) ^ rotl64(x,57);
    x ^= rotl64(key, 13);
    return x;
}