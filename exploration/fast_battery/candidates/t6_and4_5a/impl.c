#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}
// t6_and4_5a: 5-stage AND4 cascade (order-4 density probe)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1)&rotl64(x,2)&rotl64(x,3)&rotl64(x,4)) ^ rk(key,0);
    x ^= (rotl64(x,11)&rotl64(x,12)&rotl64(x,13)&rotl64(x,14)) ^ rk(key,1);
    x ^= (rotl64(x,21)&rotl64(x,22)&rotl64(x,23)&rotl64(x,24)) ^ rk(key,2);
    x ^= (rotl64(x,31)&rotl64(x,32)&rotl64(x,33)&rotl64(x,34)) ^ rk(key,3);
    x ^= (rotl64(x,41)&rotl64(x,42)&rotl64(x,43)&rotl64(x,44)) ^ rk(key,4);
    return x ^ rotl64(key,13);
}
