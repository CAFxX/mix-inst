#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}

// t6_xc4c: 4-stage cross-coupled, close AND pairs, alt schedule
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t tp = 0;
    uint64_t t0 = (rotl64(x,2) & rotl64(x,3));
    x ^= t0 ^ rotl64(x,17) ^ rk(key,0) ^ rotl64(tp,11);
    tp = t0;
    uint64_t t1 = (rotl64(x,9) & rotl64(x,10));
    x ^= t1 ^ rotl64(x,25) ^ rk(key,1) ^ rotl64(tp,5);
    tp = t1;
    uint64_t t2 = (rotl64(x,4) & rotl64(x,6));
    x ^= t2 ^ rotl64(x,41) ^ rk(key,2) ^ rotl64(tp,17);
    tp = t2;
    uint64_t t3 = (rotl64(x,15) & rotl64(x,16));
    x ^= t3 ^ rotl64(x,33) ^ rk(key,3) ^ rotl64(tp,29);
    tp = t3;
    x ^= rotl64(key, 13) >> 32;
    return x;
}
