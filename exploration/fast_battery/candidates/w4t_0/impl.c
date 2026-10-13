#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_0: w4t 4-term rotl-xor linear (screen keep idx 0, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,21) & rotl64(x,24));
    x ^= (rotl64(x,11) & rotl64(x,7));
    x ^= rotl64(x,4) ^ rotl64(x,7) ^ rotl64(x,17) ^ rotl64(x,23);
    x ^= (rotl64(x,55) & rotl64(x,53));
    x ^= (rotl64(x,42) & rotl64(x,44));
    x ^= rotl64(x,4) ^ rotl64(x,7) ^ rotl64(x,17) ^ rotl64(x,23);
    x ^= (rotl64(x,8) & rotl64(x,7));
    x ^= (rotl64(x,30) & rotl64(x,27));
    x ^= rotl64(x,4) ^ rotl64(x,7) ^ rotl64(x,17) ^ rotl64(x,23);
    x ^= rotl64(key, 13);
    return x;
}
