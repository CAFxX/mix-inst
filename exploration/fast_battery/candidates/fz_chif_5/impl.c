// fz_chif_5: 5-stage fused chi: x ^= chi(x,ra,rb)^chi(rc,rd,re)^chi(rf,rg,rh)
#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;if(!r)return x;return (x<<r)|(x>>(64-r));}
static uint64_t chi64(uint64_t a,uint64_t b,uint64_t c){return a^((~b)&c);}
uint64_t mix_hash(uint64_t v,uint64_t k){
    uint64_t x=v^k;
    x^=chi64(x,rotl64(x,3),rotl64(x,11))^chi64(rotl64(x,23),rotl64(x,31),rotl64(x,43))^chi64(rotl64(x,53),rotl64(x,3),rotl64(x,23));
    x^=chi64(x,rotl64(x,7),rotl64(x,17))^chi64(rotl64(x,29),rotl64(x,37),rotl64(x,47))^chi64(rotl64(x,59),rotl64(x,7),rotl64(x,29));
    x^=chi64(x,rotl64(x,5),rotl64(x,13))^chi64(rotl64(x,27),rotl64(x,41),rotl64(x,49))^chi64(rotl64(x,61),rotl64(x,5),rotl64(x,27));
    x^=chi64(x,rotl64(x,9),rotl64(x,19))^chi64(rotl64(x,33),rotl64(x,39),rotl64(x,51))^chi64(rotl64(x,57),rotl64(x,9),rotl64(x,33));
    x^=chi64(x,rotl64(x,11),rotl64(x,23))^chi64(rotl64(x,35),rotl64(x,45),rotl64(x,55))^chi64(rotl64(x,63),rotl64(x,11),rotl64(x,35));
    x^=rotl64(k,13);
    return x;
}
