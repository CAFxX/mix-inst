#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 3-stage triple-chi, spread rotations: x ^= ((~ra)&rb)^((~rc)&rd)^((~re)&rf)^rg
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[7] = {rotl64(x,4), rotl64(x,18), rotl64(x,6), rotl64(x,50), rotl64(x,27), rotl64(x,54), rotl64(x,58)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    { uint64_t r[7] = {rotl64(x,56), rotl64(x,25), rotl64(x,35), rotl64(x,22), rotl64(x,11), rotl64(x,9), rotl64(x,45)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    { uint64_t r[7] = {rotl64(x,16), rotl64(x,1), rotl64(x,39), rotl64(x,47), rotl64(x,29), rotl64(x,43), rotl64(x,37)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    x ^= rotl64(key, 13);
    return x;
}