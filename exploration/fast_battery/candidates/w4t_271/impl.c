#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_271: w4t 4-term rotl-xor linear (screen keep idx 271, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,42) & rotl64(x,40));
    x ^= (rotl64(x,51) & rotl64(x,52));
    x ^= rotl64(x,6) ^ rotl64(x,20) ^ rotl64(x,39) ^ rotl64(x,47);
    x ^= (rotl64(x,5) & rotl64(x,7));
    x ^= (rotl64(x,52) & rotl64(x,54));
    x ^= rotl64(x,6) ^ rotl64(x,20) ^ rotl64(x,39) ^ rotl64(x,47);
    x ^= (rotl64(x,46) & rotl64(x,44));
    x ^= (rotl64(x,51) & rotl64(x,48));
    x ^= rotl64(x,6) ^ rotl64(x,20) ^ rotl64(x,39) ^ rotl64(x,47);
    x ^= rotl64(key, 13);
    return x;
}
