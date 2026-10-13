#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_275: w4t 4-term rotl-xor linear (screen keep idx 275, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,21) & rotl64(x,17));
    x ^= (rotl64(x,15) & rotl64(x,11));
    x ^= rotl64(x,6) ^ rotl64(x,22) ^ rotl64(x,58) ^ rotl64(x,59);
    x ^= (rotl64(x,9) & rotl64(x,5));
    x ^= (rotl64(x,61) & rotl64(x,57));
    x ^= rotl64(x,6) ^ rotl64(x,22) ^ rotl64(x,58) ^ rotl64(x,59);
    x ^= (rotl64(x,60) & rotl64(x,58));
    x ^= (rotl64(x,52) & rotl64(x,49));
    x ^= rotl64(x,6) ^ rotl64(x,22) ^ rotl64(x,58) ^ rotl64(x,59);
    x ^= rotl64(key, 13);
    return x;
}
