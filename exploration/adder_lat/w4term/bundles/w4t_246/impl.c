#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_246: w4t 4-term rotl-xor linear (screen keep idx 246, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,44) & rotl64(x,41));
    x ^= (rotl64(x,33) & rotl64(x,35));
    x ^= rotl64(x,10) ^ rotl64(x,22) ^ rotl64(x,39) ^ rotl64(x,44);
    x ^= (rotl64(x,54) & rotl64(x,51));
    x ^= (rotl64(x,59) & rotl64(x,62));
    x ^= rotl64(x,10) ^ rotl64(x,22) ^ rotl64(x,39) ^ rotl64(x,44);
    x ^= (rotl64(x,13) & rotl64(x,17));
    x ^= (rotl64(x,30) & rotl64(x,29));
    x ^= rotl64(x,10) ^ rotl64(x,22) ^ rotl64(x,39) ^ rotl64(x,44);
    x ^= rotl64(key, 13);
    return x;
}
