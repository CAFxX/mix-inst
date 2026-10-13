#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31; return r ? (x << r) | (x >> (32 - r)) : x;
}
static inline uint16_t rotl16(uint16_t x, int r) {
    r &= 15; return r ? (uint16_t)(((uint32_t)x << r) | ((uint32_t)x >> (16 - r))) : x;
}
static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
static const uint8_t SB0[16] = {0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j % 8]; }

// t6_split3a: 3 super-stages, parallel 32-bit cascades + cross
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint32_t lo, hi;
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32);  // super-stage 0
    lo ^= (rotl32(lo,3) & rotl32(lo,11)) ^ rotl32(lo,23) ^ (uint32_t)rk(key,0);
    hi ^= (rotl32(hi,10) & rotl32(hi,18)) ^ rotl32(hi,30) ^ (uint32_t)rk(key,0);
    lo ^= (rotl32(lo,13) & rotl32(lo,29)) ^ rotl32(lo,7) ^ (uint32_t)rk(key,1);
    hi ^= (rotl32(hi,20) & rotl32(hi,4)) ^ rotl32(hi,14) ^ (uint32_t)rk(key,1);
    x = ((uint64_t)(lo ^ rotl32(hi,5) ^ (uint32_t)rk(key,6))) | (((uint64_t)(hi ^ rotl32(lo,9) ^ (uint32_t)rk(key,7))) << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32);  // super-stage 1
    lo ^= (rotl32(lo,17) & rotl32(lo,5)) ^ rotl32(lo,27) ^ (uint32_t)rk(key,2);
    hi ^= (rotl32(hi,24) & rotl32(hi,12)) ^ rotl32(hi,2) ^ (uint32_t)rk(key,2);
    lo ^= (rotl32(lo,23) & rotl32(lo,9)) ^ rotl32(lo,15) ^ (uint32_t)rk(key,3);
    hi ^= (rotl32(hi,30) & rotl32(hi,16)) ^ rotl32(hi,22) ^ (uint32_t)rk(key,3);
    x = ((uint64_t)(lo ^ rotl32(hi,11) ^ (uint32_t)rk(key,8))) | (((uint64_t)(hi ^ rotl32(lo,15) ^ (uint32_t)rk(key,9))) << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32);  // super-stage 2
    lo ^= (rotl32(lo,29) & rotl32(lo,13)) ^ rotl32(lo,3) ^ (uint32_t)rk(key,4);
    hi ^= (rotl32(hi,4) & rotl32(hi,20)) ^ rotl32(hi,10) ^ (uint32_t)rk(key,4);
    lo ^= (rotl32(lo,7) & rotl32(lo,19)) ^ rotl32(lo,25) ^ (uint32_t)rk(key,5);
    hi ^= (rotl32(hi,14) & rotl32(hi,26)) ^ rotl32(hi,0) ^ (uint32_t)rk(key,5);
    x = ((uint64_t)(lo ^ rotl32(hi,17) ^ (uint32_t)rk(key,10))) | (((uint64_t)(hi ^ rotl32(lo,21) ^ (uint32_t)rk(key,11))) << 32);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
