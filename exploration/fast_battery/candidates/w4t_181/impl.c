#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_181: w4t 4-term rotl-xor linear (screen keep idx 181, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,44) & rotl64(x,40));
    x ^= (rotl64(x,41) & rotl64(x,44));
    x ^= rotl64(x,23) ^ rotl64(x,31) ^ rotl64(x,35) ^ rotl64(x,52);
    x ^= (rotl64(x,17) & rotl64(x,14));
    x ^= (rotl64(x,46) & rotl64(x,50));
    x ^= rotl64(x,23) ^ rotl64(x,31) ^ rotl64(x,35) ^ rotl64(x,52);
    x ^= (rotl64(x,29) & rotl64(x,33));
    x ^= (rotl64(x,5) & rotl64(x,8));
    x ^= rotl64(x,23) ^ rotl64(x,31) ^ rotl64(x,35) ^ rotl64(x,52);
    x ^= rotl64(key, 13);
    return x;
}
