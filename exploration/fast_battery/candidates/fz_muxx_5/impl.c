// fz_muxx_5: 5-stage: x ^= MUX(x,ra,rb)^MUX(rc,rd,re)
#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;if(!r)return x;return (x<<r)|(x>>(64-r));}
static uint64_t mux64(uint64_t s,uint64_t a,uint64_t b){return (s&a)|(~s&b);}
uint64_t mix_hash(uint64_t v,uint64_t k){
    uint64_t x=v^k;
    x^=mux64(x,rotl64(x,3),rotl64(x,11))^mux64(rotl64(x,23),rotl64(x,31),rotl64(x,43));
    x^=mux64(x,rotl64(x,7),rotl64(x,17))^mux64(rotl64(x,29),rotl64(x,37),rotl64(x,47));
    x^=mux64(x,rotl64(x,5),rotl64(x,13))^mux64(rotl64(x,27),rotl64(x,41),rotl64(x,49));
    x^=mux64(x,rotl64(x,9),rotl64(x,19))^mux64(rotl64(x,33),rotl64(x,39),rotl64(x,51));
    x^=mux64(x,rotl64(x,11),rotl64(x,23))^mux64(rotl64(x,35),rotl64(x,45),rotl64(x,55));
    x^=rotl64(k,13);
    return x;
}
