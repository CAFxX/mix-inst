#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t rk(uint64_t k,int j){static const uint64_t RC[8]={0x9E3779B97F4A7C15ULL,0x3C6EF372FE94F82AULL,0xDAA66D2C7DDF743FULL,0x78DDE6E5FD29F054ULL,0x2545F4914F6CDD1DULL,0x9E3779B97F4A7C15ULL^0xDEADBEEFULL,0x3C6EF372FE94F82AULL^0x12345678ULL,0xDAA66D2CDD6129B3EULL};return rotl64(k,13*(j+1))^RC[j%8];}

// t6_pxor6a: 6-stage parallel linear combine (control)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,5) & rotl64(x,17)) ^ (rotl64(x,29) & rotl64(x,41)) ^ (rotl64(x,53) & rotl64(x,61)) ^ rk(key,0);
    x ^= (rotl64(x,11) & rotl64(x,23)) ^ (rotl64(x,37) & rotl64(x,47)) ^ (rotl64(x,7) & rotl64(x,59)) ^ rk(key,1);
    x ^= (rotl64(x,3) & rotl64(x,19)) ^ (rotl64(x,31) & rotl64(x,43)) ^ (rotl64(x,57) & rotl64(x,9)) ^ rk(key,2);
    x ^= (rotl64(x,13) & rotl64(x,27)) ^ (rotl64(x,39) & rotl64(x,51)) ^ (rotl64(x,21) & rotl64(x,63)) ^ rk(key,3);
    x ^= (rotl64(x,1) & rotl64(x,15)) ^ (rotl64(x,25) & rotl64(x,35)) ^ (rotl64(x,45) & rotl64(x,55)) ^ rk(key,4);
    x ^= (rotl64(x,9) & rotl64(x,22)) ^ (rotl64(x,34) & rotl64(x,46)) ^ (rotl64(x,58) & rotl64(x,62)) ^ rk(key,5);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
