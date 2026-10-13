#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}
// t6_wand3_5b: 5-stage AND3+spread, sched B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,3)&rotl64(x,4)&rotl64(x,5)) ^ rotl64(x,23) ^ rk(key,0);
    x ^= (rotl64(x,13)&rotl64(x,14)&rotl64(x,15)) ^ rotl64(x,41) ^ rk(key,1);
    x ^= (rotl64(x,7)&rotl64(x,8)&rotl64(x,9)) ^ rotl64(x,17) ^ rk(key,2);
    x ^= (rotl64(x,21)&rotl64(x,22)&rotl64(x,23)) ^ rotl64(x,11) ^ rk(key,3);
    x ^= (rotl64(x,29)&rotl64(x,30)&rotl64(x,31)) ^ rotl64(x,43) ^ rk(key,4);
    return x ^ rotl64(key,13);
}
