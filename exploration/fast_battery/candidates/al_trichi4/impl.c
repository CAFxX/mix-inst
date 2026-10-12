#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 4-stage triple-chi: x ^= ((~ra)&rb)^((~rc)&rd)^((~re)&rf)^rg (fan-in 7)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[7] = {rotl64(x,1), rotl64(x,2), rotl64(x,4), rotl64(x,8), rotl64(x,16), rotl64(x,32), rotl64(x,7)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    { uint64_t r[7] = {rotl64(x,3), rotl64(x,9), rotl64(x,13), rotl64(x,19), rotl64(x,29), rotl64(x,5), rotl64(x,11)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    { uint64_t r[7] = {rotl64(x,11), rotl64(x,17), rotl64(x,23), rotl64(x,31), rotl64(x,41), rotl64(x,13), rotl64(x,17)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    { uint64_t r[7] = {rotl64(x,5), rotl64(x,15), rotl64(x,25), rotl64(x,37), rotl64(x,47), rotl64(x,7), rotl64(x,23)};
      x ^= ((~r[0]) & r[1]) ^ ((~r[2]) & r[3]) ^ ((~r[4]) & r[5]) ^ r[6]; }
    x ^= rotl64(key, 13);
    return x;
}