#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-round 32-bit Feistel, F(y)=y^((~ra)&rb)^rc^rk
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint32_t L = (uint32_t)(val >> 32), R = (uint32_t)val;
    { uint32_t rk = (uint32_t)(rotl64(key,13 % 64) ^ 0x9E3779B97F4A7C15ULL);
      uint32_t F = R ^ ((~rotl32(R,1)) & rotl32(R,2)) ^ rotl32(R,7) ^ rk;
      L ^= F; uint32_t t = L; L = R; R = t; }
    { uint32_t rk = (uint32_t)(rotl64(key,26 % 64) ^ 0x3C6EF372FE94F82AULL);
      uint32_t F = R ^ ((~rotl32(R,3)) & rotl32(R,11)) ^ rotl32(R,5) ^ rk;
      L ^= F; uint32_t t = L; L = R; R = t; }
    { uint32_t rk = (uint32_t)(rotl64(key,39 % 64) ^ 0xDAA66D2C7DDF743FULL);
      uint32_t F = R ^ ((~rotl32(R,7)) & rotl32(R,19)) ^ rotl32(R,13) ^ rk;
      L ^= F; uint32_t t = L; L = R; R = t; }
    { uint32_t rk = (uint32_t)(rotl64(key,52 % 64) ^ 0x78DDE6E5FD29F054ULL);
      uint32_t F = R ^ ((~rotl32(R,2)) & rotl32(R,9)) ^ rotl32(R,17) ^ rk;
      L ^= F; uint32_t t = L; L = R; R = t; }
    { uint32_t rk = (uint32_t)(rotl64(key,65 % 64) ^ 0x2545F4914F6CDD1DULL);
      uint32_t F = R ^ ((~rotl32(R,5)) & rotl32(R,17)) ^ rotl32(R,23) ^ rk;
      L ^= F; uint32_t t = L; L = R; R = t; }
    { uint32_t rk = (uint32_t)(rotl64(key,78 % 64) ^ 0x9E3779B9A1E7C2FAULL);
      uint32_t F = R ^ ((~rotl32(R,11)) & rotl32(R,23)) ^ rotl32(R,29) ^ rk;
      L ^= F; uint32_t t = L; L = R; R = t; }
    return ((uint64_t)L << 32) | R;
}