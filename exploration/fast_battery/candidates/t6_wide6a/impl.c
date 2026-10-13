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

// t6_wide6a: 6-stage dual parallel AND terms + linear
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,3) & rotl64(x,11)) ^ (rotl64(x,23) & rotl64(x,37)) ^ rotl64(x,53)) ^ rk(key,0);
    x ^= ((rotl64(x,7) & rotl64(x,17)) ^ (rotl64(x,29) & rotl64(x,43)) ^ rotl64(x,59)) ^ rk(key,1);
    x ^= ((rotl64(x,13) & rotl64(x,27)) ^ (rotl64(x,41) & rotl64(x,5)) ^ rotl64(x,31)) ^ rk(key,2);
    x ^= ((rotl64(x,19) & rotl64(x,33)) ^ (rotl64(x,47) & rotl64(x,11)) ^ rotl64(x,61)) ^ rk(key,3);
    x ^= ((rotl64(x,23) & rotl64(x,39)) ^ (rotl64(x,53) & rotl64(x,17)) ^ rotl64(x,7)) ^ rk(key,4);
    x ^= ((rotl64(x,29) & rotl64(x,45)) ^ (rotl64(x,59) & rotl64(x,23)) ^ rotl64(x,13)) ^ rk(key,5);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
