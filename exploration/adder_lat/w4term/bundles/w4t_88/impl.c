#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_88: w4t 4-term rotl-xor linear (screen keep idx 88, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,50) & rotl64(x,53));
    x ^= (rotl64(x,48) & rotl64(x,52));
    x ^= rotl64(x,24) ^ rotl64(x,31) ^ rotl64(x,52) ^ rotl64(x,53);
    x ^= (rotl64(x,42) & rotl64(x,40));
    x ^= (rotl64(x,33) & rotl64(x,31));
    x ^= rotl64(x,24) ^ rotl64(x,31) ^ rotl64(x,52) ^ rotl64(x,53);
    x ^= (rotl64(x,48) & rotl64(x,51));
    x ^= (rotl64(x,22) & rotl64(x,25));
    x ^= rotl64(x,24) ^ rotl64(x,31) ^ rotl64(x,52) ^ rotl64(x,53);
    x ^= rotl64(key, 13);
    return x;
}
