#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
static const uint8_t SB0[16] = {0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6};
static const uint8_t PB[64] = {0,16,32,48,1,17,33,49,2,18,34,50,3,19,35,51,4,20,36,52,5,21,37,53,6,22,38,54,7,23,39,55,8,24,40,56,9,25,41,57,10,26,42,58,11,27,43,59,12,28,44,60,13,29,45,61,14,30,46,62,15,31,47,63};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j % 8]; }

// t6_hyb5e: 4 AND-stages + S-box+P-box super-stage last
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key, y, z;
    x ^= ((rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,23)) ^ rk(key,0);
    x ^= ((rotl64(x,17) & rotl64(x,29)) ^ rotl64(x,41)) ^ rk(key,1);
    x ^= ((rotl64(x,7) & rotl64(x,31)) ^ rotl64(x,47)) ^ rk(key,2);
    x ^= ((rotl64(x,23) & rotl64(x,43)) ^ rotl64(x,59)) ^ rk(key,3);
    x ^= rk(key,4); y = 0;
    for (int i = 0; i < 16; i++) y |= (uint64_t)SB0[(x >> (4*i)) & 0xF] << (4*i);
    z = 0; for (int i = 0; i < 64; i++) z |= ((y >> i) & 1ULL) << PB[i];
    x = z;
    x ^= rotl64(key, 13) >> 32;
    return x;
}
