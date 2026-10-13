#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_201: w4t 4-term rotl-xor linear (screen keep idx 201, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,45) & rotl64(x,43));
    x ^= (rotl64(x,24) & rotl64(x,21));
    x ^= rotl64(x,19) ^ rotl64(x,23) ^ rotl64(x,31) ^ rotl64(x,36);
    x ^= (rotl64(x,46) & rotl64(x,42));
    x ^= (rotl64(x,7) & rotl64(x,11));
    x ^= rotl64(x,19) ^ rotl64(x,23) ^ rotl64(x,31) ^ rotl64(x,36);
    x ^= (rotl64(x,23) & rotl64(x,19));
    x ^= (rotl64(x,29) & rotl64(x,26));
    x ^= rotl64(x,19) ^ rotl64(x,23) ^ rotl64(x,31) ^ rotl64(x,36);
    x ^= rotl64(key, 13);
    return x;
}
