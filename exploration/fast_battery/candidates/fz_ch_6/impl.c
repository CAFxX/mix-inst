/* Fused candidate fz_ch_6: 6-stage Ch replacement */
#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; if (!r) return x;
    return (x << r) | (x >> (64 - r));
}
#define CH(x,y,z) (((x)&(y))|((~(x))&(z)))
uint64_t mix(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    { uint64_t ra=rotl64(x,3),rb=rotl64(x,11),rc=rotl64(x,23),rd=rotl64(x,31),re=rotl64(x,43),rf=rotl64(x,53),rg=rotl64(x,7),rh=rotl64(x,17),ri=rotl64(x,29);
      x = CH(x,ra,rb) ^ CH(rc,rd,re) ^ CH(rf,rg,rh); }
    { uint64_t ra=rotl64(x,7),rb=rotl64(x,17),rc=rotl64(x,29),rd=rotl64(x,37),re=rotl64(x,47),rf=rotl64(x,59),rg=rotl64(x,5),rh=rotl64(x,13),ri=rotl64(x,27);
      x = CH(x,ra,rb) ^ CH(rc,rd,re) ^ CH(rf,rg,rh); }
    { uint64_t ra=rotl64(x,5),rb=rotl64(x,13),rc=rotl64(x,27),rd=rotl64(x,41),re=rotl64(x,49),rf=rotl64(x,61),rg=rotl64(x,9),rh=rotl64(x,19),ri=rotl64(x,33);
      x = CH(x,ra,rb) ^ CH(rc,rd,re) ^ CH(rf,rg,rh); }
    { uint64_t ra=rotl64(x,9),rb=rotl64(x,19),rc=rotl64(x,33),rd=rotl64(x,39),re=rotl64(x,51),rf=rotl64(x,57),rg=rotl64(x,11),rh=rotl64(x,23),ri=rotl64(x,35);
      x = CH(x,ra,rb) ^ CH(rc,rd,re) ^ CH(rf,rg,rh); }
    { uint64_t ra=rotl64(x,11),rb=rotl64(x,23),rc=rotl64(x,35),rd=rotl64(x,45),re=rotl64(x,55),rf=rotl64(x,63),rg=rotl64(x,13),rh=rotl64(x,25),ri=rotl64(x,37);
      x = CH(x,ra,rb) ^ CH(rc,rd,re) ^ CH(rf,rg,rh); }
    { uint64_t ra=rotl64(x,13),rb=rotl64(x,25),rc=rotl64(x,37),rd=rotl64(x,47),re=rotl64(x,57),rf=rotl64(x,61),rg=rotl64(x,15),rh=rotl64(x,27),ri=rotl64(x,39);
      x = CH(x,ra,rb) ^ CH(rc,rd,re) ^ CH(rf,rg,rh); }
    x ^= rotl64(k, 13);
    return x;
}