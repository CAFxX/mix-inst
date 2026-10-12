// fz_chir_6: 6-stage pure chi replacement
#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;if(!r)return x;return (x<<r)|(x>>(64-r));}
static uint64_t chi64(uint64_t a,uint64_t b,uint64_t c){return a^((~b)&c);}
uint64_t mix_hash(uint64_t v,uint64_t k){
    uint64_t x=v^k;
    x=chi64(rotl64(x,3),rotl64(x,11),rotl64(x,23))^chi64(rotl64(x,31),rotl64(x,43),rotl64(x,53))^chi64(rotl64(x,7),rotl64(x,17),rotl64(x,29));
    x=chi64(rotl64(x,7),rotl64(x,17),rotl64(x,29))^chi64(rotl64(x,37),rotl64(x,47),rotl64(x,59))^chi64(rotl64(x,5),rotl64(x,13),rotl64(x,27));
    x=chi64(rotl64(x,5),rotl64(x,13),rotl64(x,27))^chi64(rotl64(x,41),rotl64(x,49),rotl64(x,61))^chi64(rotl64(x,9),rotl64(x,19),rotl64(x,33));
    x=chi64(rotl64(x,9),rotl64(x,19),rotl64(x,33))^chi64(rotl64(x,39),rotl64(x,51),rotl64(x,57))^chi64(rotl64(x,11),rotl64(x,23),rotl64(x,35));
    x=chi64(rotl64(x,11),rotl64(x,23),rotl64(x,35))^chi64(rotl64(x,45),rotl64(x,55),rotl64(x,63))^chi64(rotl64(x,13),rotl64(x,25),rotl64(x,37));
    x=chi64(rotl64(x,13),rotl64(x,25),rotl64(x,37))^chi64(rotl64(x,47),rotl64(x,57),rotl64(x,61))^chi64(rotl64(x,15),rotl64(x,27),rotl64(x,39));
    x^=rotl64(k,13);
    return x;
}
