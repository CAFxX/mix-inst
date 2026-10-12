#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-stage chi cascade, schedule C
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,5), rotl64(x,11), rotl64(x,23)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,13), rotl64(x,29), rotl64(x,7)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,3), rotl64(x,17), rotl64(x,41)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,19), rotl64(x,37), rotl64(x,11)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,7), rotl64(x,23), rotl64(x,53)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,29), rotl64(x,47), rotl64(x,13)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key, 13);
    return x;
}