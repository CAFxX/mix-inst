#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-stage chi cascade, avalanche-aware schedule E (random well-separated)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,20), rotl64(x,28), rotl64(x,35)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,11), rotl64(x,4), rotl64(x,46)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,56), rotl64(x,43), rotl64(x,16)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,17), rotl64(x,50), rotl64(x,5)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,44), rotl64(x,29), rotl64(x,62)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,36), rotl64(x,54), rotl64(x,61)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key, 13);
    return x;
}