#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j % 8]; }

// t6_par5b: parallel dual 5-stage cascade + AND-combine, B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t a = val, b = key;
    a ^= ((rotl64(a,5) & rotl64(a,13)) ^ rotl64(a,29)) ^ rk(key,0);
    a ^= ((rotl64(a,19) & rotl64(a,31)) ^ rotl64(a,43)) ^ rk(key,1);
    a ^= ((rotl64(a,11) & rotl64(a,23)) ^ rotl64(a,47)) ^ rk(key,2);
    a ^= ((rotl64(a,29) & rotl64(a,41)) ^ rotl64(a,61)) ^ rk(key,3);
    a ^= ((rotl64(a,7) & rotl64(a,17)) ^ rotl64(a,53)) ^ rk(key,4);
    b ^= ((rotl64(b,5) & rotl64(b,13)) ^ rotl64(b,29)) ^ rk(val,0);
    b ^= ((rotl64(b,19) & rotl64(b,31)) ^ rotl64(b,43)) ^ rk(val,1);
    b ^= ((rotl64(b,11) & rotl64(b,23)) ^ rotl64(b,47)) ^ rk(val,2);
    b ^= ((rotl64(b,29) & rotl64(b,41)) ^ rotl64(b,61)) ^ rk(val,3);
    b ^= ((rotl64(b,7) & rotl64(b,17)) ^ rotl64(b,53)) ^ rk(val,4);
    uint64_t rkC = rotl64(val ^ key, 77) ^ RC[7];
    uint64_t out = a ^ b ^ (a & b) ^ rkC;
    out ^= rotl64(val ^ key, 13) >> 32;
    return out;
}
