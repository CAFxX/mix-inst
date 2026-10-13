#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_255: w4t 4-term rotl-xor linear (screen keep idx 255, fr=62)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,36) & rotl64(x,33));
    x ^= (rotl64(x,37) & rotl64(x,34));
    x ^= rotl64(x,22) ^ rotl64(x,40) ^ rotl64(x,46) ^ rotl64(x,51);
    x ^= (rotl64(x,29) & rotl64(x,33));
    x ^= (rotl64(x,49) & rotl64(x,53));
    x ^= rotl64(x,22) ^ rotl64(x,40) ^ rotl64(x,46) ^ rotl64(x,51);
    x ^= (rotl64(x,34) & rotl64(x,37));
    x ^= (rotl64(x,44) & rotl64(x,47));
    x ^= rotl64(x,22) ^ rotl64(x,40) ^ rotl64(x,46) ^ rotl64(x,51);
    x ^= rotl64(key, 13);
    return x;
}
