#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_182: w4t 4-term rotl-xor linear (screen keep idx 182, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,48) & rotl64(x,50));
    x ^= (rotl64(x,21) & rotl64(x,22));
    x ^= rotl64(x,3) ^ rotl64(x,7) ^ rotl64(x,30) ^ rotl64(x,31);
    x ^= (rotl64(x,5) & rotl64(x,9));
    x ^= (rotl64(x,7) & rotl64(x,10));
    x ^= rotl64(x,3) ^ rotl64(x,7) ^ rotl64(x,30) ^ rotl64(x,31);
    x ^= (rotl64(x,36) & rotl64(x,34));
    x ^= (rotl64(x,51) & rotl64(x,47));
    x ^= rotl64(x,3) ^ rotl64(x,7) ^ rotl64(x,30) ^ rotl64(x,31);
    x ^= rotl64(key, 13);
    return x;
}
