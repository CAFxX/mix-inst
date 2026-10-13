#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_108: w4t 4-term rotl-xor linear (screen keep idx 108, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,48) & rotl64(x,47));
    x ^= (rotl64(x,27) & rotl64(x,26));
    x ^= rotl64(x,2) ^ rotl64(x,20) ^ rotl64(x,37) ^ rotl64(x,55);
    x ^= (rotl64(x,21) & rotl64(x,19));
    x ^= (rotl64(x,43) & rotl64(x,45));
    x ^= rotl64(x,2) ^ rotl64(x,20) ^ rotl64(x,37) ^ rotl64(x,55);
    x ^= (rotl64(x,24) & rotl64(x,27));
    x ^= (rotl64(x,29) & rotl64(x,31));
    x ^= rotl64(x,2) ^ rotl64(x,20) ^ rotl64(x,37) ^ rotl64(x,55);
    x ^= rotl64(key, 13);
    return x;
}
