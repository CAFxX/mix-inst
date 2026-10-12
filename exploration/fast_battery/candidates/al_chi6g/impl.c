#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-stage chi cascade, avalanche-aware schedule G (random well-separated)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,31), rotl64(x,1), rotl64(x,44)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,4), rotl64(x,28), rotl64(x,34)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,5), rotl64(x,63), rotl64(x,40)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,20), rotl64(x,14), rotl64(x,42)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,8), rotl64(x,39), rotl64(x,55)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,45), rotl64(x,61), rotl64(x,21)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key, 13);
    return x;
}