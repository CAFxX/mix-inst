#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_50: w4t 4-term rotl-xor linear (screen keep idx 50, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,38) & rotl64(x,34));
    x ^= (rotl64(x,35) & rotl64(x,34));
    x ^= rotl64(x,5) ^ rotl64(x,39) ^ rotl64(x,58) ^ rotl64(x,61);
    x ^= (rotl64(x,23) & rotl64(x,21));
    x ^= (rotl64(x,56) & rotl64(x,57));
    x ^= rotl64(x,5) ^ rotl64(x,39) ^ rotl64(x,58) ^ rotl64(x,61);
    x ^= (rotl64(x,16) & rotl64(x,12));
    x ^= (rotl64(x,17) & rotl64(x,16));
    x ^= rotl64(x,5) ^ rotl64(x,39) ^ rotl64(x,58) ^ rotl64(x,61);
    x ^= rotl64(key, 13);
    return x;
}
