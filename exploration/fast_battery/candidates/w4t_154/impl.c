#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_154: w4t 4-term rotl-xor linear (screen keep idx 154, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,12) & rotl64(x,8));
    x ^= (rotl64(x,31) & rotl64(x,29));
    x ^= rotl64(x,32) ^ rotl64(x,39) ^ rotl64(x,49) ^ rotl64(x,63);
    x ^= (rotl64(x,4) & rotl64(x,2));
    x ^= (rotl64(x,55) & rotl64(x,51));
    x ^= rotl64(x,32) ^ rotl64(x,39) ^ rotl64(x,49) ^ rotl64(x,63);
    x ^= (rotl64(x,8) & rotl64(x,5));
    x ^= (rotl64(x,15) & rotl64(x,13));
    x ^= rotl64(x,32) ^ rotl64(x,39) ^ rotl64(x,49) ^ rotl64(x,63);
    x ^= rotl64(key, 13);
    return x;
}
