#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_218: w4t 4-term rotl-xor linear (screen keep idx 218, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,12) & rotl64(x,15));
    x ^= (rotl64(x,24) & rotl64(x,20));
    x ^= rotl64(x,10) ^ rotl64(x,13) ^ rotl64(x,21) ^ rotl64(x,33);
    x ^= (rotl64(x,18) & rotl64(x,15));
    x ^= (rotl64(x,35) & rotl64(x,32));
    x ^= rotl64(x,10) ^ rotl64(x,13) ^ rotl64(x,21) ^ rotl64(x,33);
    x ^= (rotl64(x,55) & rotl64(x,54));
    x ^= (rotl64(x,56) & rotl64(x,52));
    x ^= rotl64(x,10) ^ rotl64(x,13) ^ rotl64(x,21) ^ rotl64(x,33);
    x ^= rotl64(key, 13);
    return x;
}
