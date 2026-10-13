#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31; return r ? (x << r) | (x >> (32 - r)) : x;
}
static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j % 8]; }

// t6_xcas6b: 6-stage cross-cascade (cross-AND halves), sched B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key, rkj;
    uint32_t lo, hi, nlo, nhi;
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32); rkj = rk(key,0);
    nlo = lo ^ ((rotl32(lo,5) & rotl32(hi,13)) ^ rotl32(lo,11) ^ (uint32_t)rkj);
    nhi = hi ^ ((rotl32(hi,19) & rotl32(lo,7)) ^ rotl32(hi,23) ^ (uint32_t)(rkj >> 32));
    x = (uint64_t)nlo | ((uint64_t)nhi << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32); rkj = rk(key,1);
    nlo = lo ^ ((rotl32(lo,23) & rotl32(hi,3)) ^ rotl32(lo,17) ^ (uint32_t)rkj);
    nhi = hi ^ ((rotl32(hi,11) & rotl32(lo,27)) ^ rotl32(hi,5) ^ (uint32_t)(rkj >> 32));
    x = (uint64_t)nlo | ((uint64_t)nhi << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32); rkj = rk(key,2);
    nlo = lo ^ ((rotl32(lo,13) & rotl32(hi,29)) ^ rotl32(lo,7) ^ (uint32_t)rkj);
    nhi = hi ^ ((rotl32(hi,3) & rotl32(lo,15)) ^ rotl32(hi,29) ^ (uint32_t)(rkj >> 32));
    x = (uint64_t)nlo | ((uint64_t)nhi << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32); rkj = rk(key,3);
    nlo = lo ^ ((rotl32(lo,9) & rotl32(hi,21)) ^ rotl32(lo,25) ^ (uint32_t)rkj);
    nhi = hi ^ ((rotl32(hi,17) & rotl32(lo,11)) ^ rotl32(hi,7) ^ (uint32_t)(rkj >> 32));
    x = (uint64_t)nlo | ((uint64_t)nhi << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32); rkj = rk(key,4);
    nlo = lo ^ ((rotl32(lo,27) & rotl32(hi,7)) ^ rotl32(lo,3) ^ (uint32_t)rkj);
    nhi = hi ^ ((rotl32(hi,23) & rotl32(lo,19)) ^ rotl32(hi,15) ^ (uint32_t)(rkj >> 32));
    x = (uint64_t)nlo | ((uint64_t)nhi << 32);
    lo = (uint32_t)x; hi = (uint32_t)(x >> 32); rkj = rk(key,5);
    nlo = lo ^ ((rotl32(lo,15) & rotl32(hi,25)) ^ rotl32(lo,19) ^ (uint32_t)rkj);
    nhi = hi ^ ((rotl32(hi,7) & rotl32(lo,3)) ^ rotl32(hi,27) ^ (uint32_t)(rkj >> 32));
    x = (uint64_t)nlo | ((uint64_t)nhi << 32);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
