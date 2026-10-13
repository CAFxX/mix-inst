#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_95: w4t 4-term rotl-xor linear (screen keep idx 95, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,19) & rotl64(x,22));
    x ^= (rotl64(x,2) & rotl64(x,5));
    x ^= rotl64(x,3) ^ rotl64(x,38) ^ rotl64(x,52) ^ rotl64(x,60);
    x ^= (rotl64(x,58) & rotl64(x,54));
    x ^= (rotl64(x,38) & rotl64(x,42));
    x ^= rotl64(x,3) ^ rotl64(x,38) ^ rotl64(x,52) ^ rotl64(x,60);
    x ^= (rotl64(x,55) & rotl64(x,58));
    x ^= (rotl64(x,44) & rotl64(x,42));
    x ^= rotl64(x,3) ^ rotl64(x,38) ^ rotl64(x,52) ^ rotl64(x,60);
    x ^= rotl64(key, 13);
    return x;
}
