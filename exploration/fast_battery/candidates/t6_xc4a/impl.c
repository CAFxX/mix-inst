#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}

// t6_xc4a: 4-stage cross-coupled cascade, aggressive probe
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t tp = 0;
    uint64_t t0 = (rotl64(x,5) & rotl64(x,17));
    x ^= t0 ^ rotl64(x,29) ^ rk(key,0) ^ rotl64(tp,7);
    tp = t0;
    uint64_t t1 = (rotl64(x,11) & rotl64(x,23));
    x ^= t1 ^ rotl64(x,37) ^ rk(key,1) ^ rotl64(tp,13);
    tp = t1;
    uint64_t t2 = (rotl64(x,3) & rotl64(x,19));
    x ^= t2 ^ rotl64(x,31) ^ rk(key,2) ^ rotl64(tp,19);
    tp = t2;
    uint64_t t3 = (rotl64(x,13) & rotl64(x,27));
    x ^= t3 ^ rotl64(x,39) ^ rk(key,3) ^ rotl64(tp,23);
    tp = t3;
    x ^= rotl64(key, 13) >> 32;
    return x;
}
