#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_268: w4t 4-term rotl-xor linear (screen keep idx 268, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,32) & rotl64(x,33));
    x ^= (rotl64(x,5) & rotl64(x,4));
    x ^= rotl64(x,15) ^ rotl64(x,35) ^ rotl64(x,36) ^ rotl64(x,38);
    x ^= (rotl64(x,26) & rotl64(x,22));
    x ^= (rotl64(x,33) & rotl64(x,37));
    x ^= rotl64(x,15) ^ rotl64(x,35) ^ rotl64(x,36) ^ rotl64(x,38);
    x ^= (rotl64(x,16) & rotl64(x,12));
    x ^= (rotl64(x,54) & rotl64(x,52));
    x ^= rotl64(x,15) ^ rotl64(x,35) ^ rotl64(x,36) ^ rotl64(x,38);
    x ^= rotl64(key, 13);
    return x;
}
