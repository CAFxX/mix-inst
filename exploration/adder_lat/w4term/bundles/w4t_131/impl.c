#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_131: w4t 4-term rotl-xor linear (screen keep idx 131, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,29) & rotl64(x,33));
    x ^= (rotl64(x,5) & rotl64(x,8));
    x ^= rotl64(x,7) ^ rotl64(x,8) ^ rotl64(x,28) ^ rotl64(x,39);
    x ^= (rotl64(x,37) & rotl64(x,36));
    x ^= (rotl64(x,18) & rotl64(x,21));
    x ^= rotl64(x,7) ^ rotl64(x,8) ^ rotl64(x,28) ^ rotl64(x,39);
    x ^= (rotl64(x,35) & rotl64(x,37));
    x ^= (rotl64(x,39) & rotl64(x,41));
    x ^= rotl64(x,7) ^ rotl64(x,8) ^ rotl64(x,28) ^ rotl64(x,39);
    x ^= rotl64(key, 13);
    return x;
}
