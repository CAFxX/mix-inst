#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_250: w4t 4-term rotl-xor linear (screen keep idx 250, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,54) & rotl64(x,50));
    x ^= (rotl64(x,39) & rotl64(x,43));
    x ^= rotl64(x,4) ^ rotl64(x,32) ^ rotl64(x,55) ^ rotl64(x,63);
    x ^= (rotl64(x,37) & rotl64(x,35));
    x ^= (rotl64(x,10) & rotl64(x,8));
    x ^= rotl64(x,4) ^ rotl64(x,32) ^ rotl64(x,55) ^ rotl64(x,63);
    x ^= (rotl64(x,45) & rotl64(x,44));
    x ^= (rotl64(x,46) & rotl64(x,43));
    x ^= rotl64(x,4) ^ rotl64(x,32) ^ rotl64(x,55) ^ rotl64(x,63);
    x ^= rotl64(key, 13);
    return x;
}
