#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_112: w4t 4-term rotl-xor linear (screen keep idx 112, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,41) & rotl64(x,42));
    x ^= (rotl64(x,6) & rotl64(x,7));
    x ^= rotl64(x,13) ^ rotl64(x,17) ^ rotl64(x,41) ^ rotl64(x,48);
    x ^= (rotl64(x,10) & rotl64(x,9));
    x ^= (rotl64(x,39) & rotl64(x,42));
    x ^= rotl64(x,13) ^ rotl64(x,17) ^ rotl64(x,41) ^ rotl64(x,48);
    x ^= (rotl64(x,45) & rotl64(x,41));
    x ^= (rotl64(x,43) & rotl64(x,40));
    x ^= rotl64(x,13) ^ rotl64(x,17) ^ rotl64(x,41) ^ rotl64(x,48);
    x ^= rotl64(key, 13);
    return x;
}
