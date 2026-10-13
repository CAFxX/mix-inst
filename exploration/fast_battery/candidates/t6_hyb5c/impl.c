#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j % 8]; }

// t6_hyb5c: 3 singles + 2 dual-AND (no re)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,23)) ^ rk(key,0);
    x ^= ((rotl64(x,17) & rotl64(x,29)) ^ rotl64(x,41)) ^ rk(key,1);
    x ^= ((rotl64(x,7) & rotl64(x,31)) ^ rotl64(x,47)) ^ rk(key,2);
    x ^= ((rotl64(x,7) & rotl64(x,31)) ^ (rotl64(x,47) & rotl64(x,59))) ^ rk(key,3);
    x ^= ((rotl64(x,23) & rotl64(x,43)) ^ (rotl64(x,5) & rotl64(x,61))) ^ rk(key,4);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
