#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_74: w4t 4-term rotl-xor linear (screen keep idx 74, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,26) & rotl64(x,23));
    x ^= (rotl64(x,6) & rotl64(x,10));
    x ^= rotl64(x,9) ^ rotl64(x,15) ^ rotl64(x,37) ^ rotl64(x,38);
    x ^= (rotl64(x,33) & rotl64(x,35));
    x ^= (rotl64(x,61) & rotl64(x,59));
    x ^= rotl64(x,9) ^ rotl64(x,15) ^ rotl64(x,37) ^ rotl64(x,38);
    x ^= (rotl64(x,37) & rotl64(x,34));
    x ^= (rotl64(x,18) & rotl64(x,14));
    x ^= rotl64(x,9) ^ rotl64(x,15) ^ rotl64(x,37) ^ rotl64(x,38);
    x ^= rotl64(key, 13);
    return x;
}
