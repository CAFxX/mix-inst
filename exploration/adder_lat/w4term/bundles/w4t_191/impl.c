#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_191: w4t 4-term rotl-xor linear (screen keep idx 191, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,21) & rotl64(x,24));
    x ^= (rotl64(x,22) & rotl64(x,21));
    x ^= rotl64(x,5) ^ rotl64(x,7) ^ rotl64(x,25) ^ rotl64(x,28);
    x ^= (rotl64(x,15) & rotl64(x,12));
    x ^= (rotl64(x,36) & rotl64(x,33));
    x ^= rotl64(x,5) ^ rotl64(x,7) ^ rotl64(x,25) ^ rotl64(x,28);
    x ^= (rotl64(x,2) & rotl64(x,3));
    x ^= (rotl64(x,14) & rotl64(x,15));
    x ^= rotl64(x,5) ^ rotl64(x,7) ^ rotl64(x,25) ^ rotl64(x,28);
    x ^= rotl64(key, 13);
    return x;
}
