#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_150: w4t 4-term rotl-xor linear (screen keep idx 150, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,36) & rotl64(x,33));
    x ^= (rotl64(x,21) & rotl64(x,19));
    x ^= rotl64(x,2) ^ rotl64(x,6) ^ rotl64(x,17) ^ rotl64(x,25);
    x ^= (rotl64(x,45) & rotl64(x,48));
    x ^= (rotl64(x,31) & rotl64(x,29));
    x ^= rotl64(x,2) ^ rotl64(x,6) ^ rotl64(x,17) ^ rotl64(x,25);
    x ^= (rotl64(x,32) & rotl64(x,31));
    x ^= (rotl64(x,47) & rotl64(x,51));
    x ^= rotl64(x,2) ^ rotl64(x,6) ^ rotl64(x,17) ^ rotl64(x,25);
    x ^= rotl64(key, 13);
    return x;
}
