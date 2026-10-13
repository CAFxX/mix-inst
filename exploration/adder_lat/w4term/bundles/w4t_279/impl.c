#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_279: w4t 4-term rotl-xor linear (screen keep idx 279, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,6) & rotl64(x,8));
    x ^= (rotl64(x,51) & rotl64(x,53));
    x ^= rotl64(x,3) ^ rotl64(x,10) ^ rotl64(x,15) ^ rotl64(x,40);
    x ^= (rotl64(x,36) & rotl64(x,34));
    x ^= (rotl64(x,56) & rotl64(x,55));
    x ^= rotl64(x,3) ^ rotl64(x,10) ^ rotl64(x,15) ^ rotl64(x,40);
    x ^= (rotl64(x,59) & rotl64(x,58));
    x ^= (rotl64(x,59) & rotl64(x,56));
    x ^= rotl64(x,3) ^ rotl64(x,10) ^ rotl64(x,15) ^ rotl64(x,40);
    x ^= rotl64(key, 13);
    return x;
}
