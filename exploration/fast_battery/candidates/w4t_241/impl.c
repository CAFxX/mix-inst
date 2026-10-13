#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// w4t_241: w4t 4-term rotl-xor linear (screen keep idx 241, fr=63)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,33) & rotl64(x,37));
    x ^= (rotl64(x,51) & rotl64(x,53));
    x ^= rotl64(x,2) ^ rotl64(x,21) ^ rotl64(x,55) ^ rotl64(x,58);
    x ^= (rotl64(x,10) & rotl64(x,7));
    x ^= (rotl64(x,40) & rotl64(x,38));
    x ^= rotl64(x,2) ^ rotl64(x,21) ^ rotl64(x,55) ^ rotl64(x,58);
    x ^= (rotl64(x,54) & rotl64(x,50));
    x ^= (rotl64(x,29) & rotl64(x,32));
    x ^= rotl64(x,2) ^ rotl64(x,21) ^ rotl64(x,55) ^ rotl64(x,58);
    x ^= rotl64(key, 13);
    return x;
}
