#include <stdint.h>
static inline uint64_t r64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_hs4rc: 6-stage AND hetero-strength: rc on 0,1,3,4
uint64_t mix_hash(uint64_t v,uint64_t k){
    uint64_t x=v^k;
    x^=(r64(x,1)&r64(x,2))^r64(x,13);
    x^=(r64(x,7)&r64(x,19))^r64(x,5);
    x^=(r64(x,3)&r64(x,11));
    x^=(r64(x,17)&r64(x,31))^r64(x,7);
    x^=(r64(x,11)&r64(x,23))^r64(x,37);
    x^=(r64(x,19)&r64(x,41));
    x^=r64(k,13);
    return x;}
