#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-stage AND-rotation cascade, avalanche-aware schedule H
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,1), rotl64(x,35), rotl64(x,26)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,5), rotl64(x,14), rotl64(x,53)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,7), rotl64(x,29), rotl64(x,57)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,41), rotl64(x,58), rotl64(x,9)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,31), rotl64(x,45), rotl64(x,18)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,32), rotl64(x,50), rotl64(x,17)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    x ^= rotl64(key, 13);
    return x;
}