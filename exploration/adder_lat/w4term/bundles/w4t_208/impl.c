#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_208: w4t 4-term rotl-xor linear (screen keep idx 208, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,45) & rotl64(x,49));
    x ^= (rotl64(x,13) & rotl64(x,12));
    x ^= rotl64(x,2) ^ rotl64(x,11) ^ rotl64(x,32) ^ rotl64(x,41);
    x ^= (rotl64(x,44) & rotl64(x,45));
    x ^= (rotl64(x,43) & rotl64(x,41));
    x ^= rotl64(x,2) ^ rotl64(x,11) ^ rotl64(x,32) ^ rotl64(x,41);
    x ^= (rotl64(x,40) & rotl64(x,39));
    x ^= (rotl64(x,20) & rotl64(x,16));
    x ^= rotl64(x,2) ^ rotl64(x,11) ^ rotl64(x,32) ^ rotl64(x,41);
    x ^= rotl64(key, 13);
    return x;
}
