#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint32_t rotl32(uint32_t x,int r){r&=31;return r?(x<<r)|(x>>(32-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}

// t6_split6a: Split 32-bit parallel cascade (3+3) + bijective cross
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint32_t hi = (uint32_t)(x >> 32), lo = (uint32_t)x;
    int j;
    static const int S[3][3]={{1,2,9},{5,6,17},{3,4,25}};
    for (j=0;j<3;j++) hi ^= (rotl32(hi,S[j][0])&rotl32(hi,S[j][1]))^rotl32(hi,S[j][2])^(uint32_t)rk(key,j);
    for (j=0;j<3;j++) lo ^= (rotl32(lo,S[j][0])&rotl32(lo,S[j][1]))^rotl32(lo,S[j][2])^(uint32_t)rk(key,3+j);
    hi ^= lo; lo ^= rotl32(hi,7);
    for (j=0;j<3;j++) hi ^= (rotl32(hi,S[j][0])&rotl32(hi,S[j][1]))^rotl32(hi,S[j][2])^(uint32_t)rk(key,6+j);
    for (j=0;j<3;j++) lo ^= (rotl32(lo,S[j][0])&rotl32(lo,S[j][1]))^rotl32(lo,S[j][2])^(uint32_t)rk(key,9+j);
    x = ((uint64_t)hi << 32) | lo;
    return x ^ rotl64(key,13);
}
