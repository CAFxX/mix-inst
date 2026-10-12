#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-stage chi cascade, avalanche-aware schedule F (random well-separated)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,10), rotl64(x,45), rotl64(x,35)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,59), rotl64(x,2), rotl64(x,49)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,34), rotl64(x,20), rotl64(x,42)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,6), rotl64(x,62), rotl64(x,17)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,57), rotl64(x,24), rotl64(x,11)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,23), rotl64(x,15), rotl64(x,61)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key, 13);
    return x;
}