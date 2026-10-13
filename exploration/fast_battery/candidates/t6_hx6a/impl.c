#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {
    return (a & b) | (a & c) | (b & c);
}
// t6_hx6a: hetero x^= 6-stage simple: +MAJ
uint64_t mix_hash(uint64_t val, uint64_t key) {
    static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
    uint64_t x = val ^ key, nl;
    // stage 0: ANDXOR
    nl = (rotl64(x,11) & rotl64(x,29)) ^ rotl64(x,47);
    x ^= nl ^ (rotl64(key, 13) ^ RC[0]);
    // stage 1: ORXOR
    nl = (rotl64(x,23) | rotl64(x,41)) ^ rotl64(x,7);
    x ^= nl ^ (rotl64(key, 26) ^ RC[1]);
    // stage 2: MAJ
    nl = maj64(rotl64(x,7), rotl64(x,37), rotl64(x,19));
    x ^= nl ^ (rotl64(key, 39) ^ RC[2]);
    // stage 3: ANDXOR
    nl = (rotl64(x,19) & rotl64(x,53)) ^ rotl64(x,5);
    x ^= nl ^ (rotl64(key, 52) ^ RC[3]);
    // stage 4: ORXOR
    nl = (rotl64(x,5) | rotl64(x,31)) ^ rotl64(x,13);
    x ^= nl ^ (rotl64(key, 65) ^ RC[4]);
    // stage 5: MAJ
    nl = maj64(rotl64(x,13), rotl64(x,47), rotl64(x,23));
    x ^= nl ^ (rotl64(key, 78) ^ RC[5]);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
