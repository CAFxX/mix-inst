#include <stdint.h>
static inline uint64_t r64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_and5ka: 5-stage AND-cascade + per-stage rk (sched A)
uint64_t mix_hash(uint64_t v,uint64_t k){
    static const uint64_t RC[5]={0x9E3779B97F4A7C15ull,0x3C6EF372FE94F82Aull,0xDAA66D2C7DDF743Full,0x78DDE6E5FD29F054ull,0x2545F4914F6CDD1Dull};
    uint64_t x=v^k;
    x^=(r64(x,1)&r64(x,2))^r64(x,13)^(r64(k,13)^RC[0]);
    x^=(r64(x,7)&r64(x,19))^r64(x,5)^(r64(k,26)^RC[1]);
    x^=(r64(x,3)&r64(x,11))^r64(x,29)^(r64(k,39)^RC[2]);
    x^=(r64(x,17)&r64(x,31))^r64(x,7)^(r64(k,52)^RC[3]);
    x^=(r64(x,11)&r64(x,23))^r64(x,37)^(r64(k,65)^RC[4]);
    x^=r64(k,13)>>32;
    return x;}
