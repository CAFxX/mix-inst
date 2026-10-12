#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 4-stage chi cascade + per-stage key fold: x ^= ((~ra)&rb) ^ rc ^ rk
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,1), rotl64(x,2), rotl64(x,13)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key,13 % 64) ^ 0x9E3779B97F4A7C15ULL;
    { uint64_t r[3] = {rotl64(x,7), rotl64(x,19), rotl64(x,5)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key,26 % 64) ^ 0x3C6EF372FE94F82AULL;
    { uint64_t r[3] = {rotl64(x,17), rotl64(x,31), rotl64(x,7)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key,39 % 64) ^ 0xDAA66D2C7DDF743FULL;
    { uint64_t r[3] = {rotl64(x,29), rotl64(x,43), rotl64(x,11)};
      x ^= ((~r[0]) & r[1]) ^ r[2]; }
    x ^= rotl64(key,52 % 64) ^ 0x78DDE6E5FD29F054ULL;
    x ^= rotl64(key, 13);
    return x;
}