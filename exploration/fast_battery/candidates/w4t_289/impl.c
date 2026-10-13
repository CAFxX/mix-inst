#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_289: w4t 4-term rotl-xor linear (screen keep idx 289, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,45) & rotl64(x,49));
    x ^= (rotl64(x,45) & rotl64(x,42));
    x ^= rotl64(x,14) ^ rotl64(x,27) ^ rotl64(x,28) ^ rotl64(x,31);
    x ^= (rotl64(x,22) & rotl64(x,20));
    x ^= (rotl64(x,44) & rotl64(x,40));
    x ^= rotl64(x,14) ^ rotl64(x,27) ^ rotl64(x,28) ^ rotl64(x,31);
    x ^= (rotl64(x,33) & rotl64(x,35));
    x ^= (rotl64(x,34) & rotl64(x,36));
    x ^= rotl64(x,14) ^ rotl64(x,27) ^ rotl64(x,28) ^ rotl64(x,31);
    x ^= rotl64(key, 13);
    return x;
}
