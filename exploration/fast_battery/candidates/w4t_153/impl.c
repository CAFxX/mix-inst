#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_153: w4t 4-term rotl-xor linear (screen keep idx 153, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,8) & rotl64(x,5));
    x ^= (rotl64(x,28) & rotl64(x,27));
    x ^= rotl64(x,9) ^ rotl64(x,10) ^ rotl64(x,16) ^ rotl64(x,21);
    x ^= (rotl64(x,22) & rotl64(x,19));
    x ^= (rotl64(x,15) & rotl64(x,13));
    x ^= rotl64(x,9) ^ rotl64(x,10) ^ rotl64(x,16) ^ rotl64(x,21);
    x ^= (rotl64(x,15) & rotl64(x,18));
    x ^= (rotl64(x,48) & rotl64(x,51));
    x ^= rotl64(x,9) ^ rotl64(x,10) ^ rotl64(x,16) ^ rotl64(x,21);
    x ^= rotl64(key, 13);
    return x;
}
