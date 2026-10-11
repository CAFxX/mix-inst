#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// 8-stage cascaded AND-rotation
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    // Stage rotations: (a,b,c) per stage
    const int RA[8] = {1,3,7,2,5,13,11,19};
    const int RB[8] = {8,11,19,9,17,29,23,37};
    const int RC[8] = {2,5,13,4,11,7,17,23};
    for (int i = 0; i < 8; i++) {
        x ^= (rotl64(x, RA[i]) & rotl64(x, RB[i])) ^ rotl64(x, RC[i]);
    }
    x ^= rotl64(key, 13);
    return x;
}
