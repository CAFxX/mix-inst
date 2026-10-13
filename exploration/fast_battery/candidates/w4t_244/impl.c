#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_244: w4t 4-term rotl-xor linear (screen keep idx 244, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,23) & rotl64(x,20));
    x ^= (rotl64(x,14) & rotl64(x,12));
    x ^= rotl64(x,29) ^ rotl64(x,40) ^ rotl64(x,47) ^ rotl64(x,48);
    x ^= (rotl64(x,14) & rotl64(x,11));
    x ^= (rotl64(x,36) & rotl64(x,37));
    x ^= rotl64(x,29) ^ rotl64(x,40) ^ rotl64(x,47) ^ rotl64(x,48);
    x ^= (rotl64(x,42) & rotl64(x,43));
    x ^= (rotl64(x,31) & rotl64(x,28));
    x ^= rotl64(x,29) ^ rotl64(x,40) ^ rotl64(x,47) ^ rotl64(x,48);
    x ^= rotl64(key, 13);
    return x;
}
