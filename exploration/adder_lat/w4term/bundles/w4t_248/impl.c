#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_248: w4t 4-term rotl-xor linear (screen keep idx 248, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,7) & rotl64(x,9));
    x ^= (rotl64(x,45) & rotl64(x,47));
    x ^= rotl64(x,9) ^ rotl64(x,18) ^ rotl64(x,54) ^ rotl64(x,60);
    x ^= (rotl64(x,20) & rotl64(x,23));
    x ^= (rotl64(x,34) & rotl64(x,36));
    x ^= rotl64(x,9) ^ rotl64(x,18) ^ rotl64(x,54) ^ rotl64(x,60);
    x ^= (rotl64(x,58) & rotl64(x,60));
    x ^= (rotl64(x,30) & rotl64(x,32));
    x ^= rotl64(x,9) ^ rotl64(x,18) ^ rotl64(x,54) ^ rotl64(x,60);
    x ^= rotl64(key, 13);
    return x;
}
