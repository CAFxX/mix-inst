#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}
// t6_dual5b: 5-stage dual-AND, sched B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,3)&rotl64(x,4)) ^ (rotl64(x,11)&rotl64(x,12)) ^ rk(key,0);
    x ^= (rotl64(x,7)&rotl64(x,8)) ^ (rotl64(x,33)&rotl64(x,34)) ^ rk(key,1);
    x ^= (rotl64(x,15)&rotl64(x,16)) ^ (rotl64(x,41)&rotl64(x,42)) ^ rk(key,2);
    x ^= (rotl64(x,19)&rotl64(x,20)) ^ (rotl64(x,49)&rotl64(x,50)) ^ rk(key,3);
    x ^= (rotl64(x,27)&rotl64(x,28)) ^ (rotl64(x,53)&rotl64(x,54)) ^ rk(key,4);
    return x ^ rotl64(key,13);
}
