#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint32_t rotl32(uint32_t x,int r){r&=31;return r?(x<<r)|(x>>(32-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}

// t6_twin4a: 4-stage twin-AND (density hypothesis)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1)&rotl64(x,2)) ^ (rotl64(x,5)&rotl64(x,6)) ^ rotl64(x,19) ^ rk(key,0);
    x ^= (rotl64(x,9)&rotl64(x,10)) ^ (rotl64(x,13)&rotl64(x,14)) ^ rotl64(x,33) ^ rk(key,1);
    x ^= (rotl64(x,3)&rotl64(x,4)) ^ (rotl64(x,17)&rotl64(x,18)) ^ rotl64(x,45) ^ rk(key,2);
    x ^= (rotl64(x,7)&rotl64(x,8)) ^ (rotl64(x,21)&rotl64(x,22)) ^ rotl64(x,55) ^ rk(key,3);
    return x ^ rotl64(key,13);
}
