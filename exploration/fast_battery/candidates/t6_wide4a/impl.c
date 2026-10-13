#include <stdint.h>
static inline uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_wide4a: 4-stage WIDE AND-cascade x^=(ra&rb)^(rc&rd)^re
uint64_t mix_hash(uint64_t val,uint64_t key){
    uint64_t x = val ^ key;
    x ^= (rotl64(x,11)&rotl64(x,29))^(rotl64(x,47)&rotl64(x,5))^rotl64(x,23);
    x ^= (rotl64(x,23)&rotl64(x,41))^(rotl64(x,7)&rotl64(x,19))^rotl64(x,37);
    x ^= (rotl64(x,7)&rotl64(x,37))^(rotl64(x,19)&rotl64(x,53))^rotl64(x,13);
    x ^= (rotl64(x,17)&rotl64(x,43))^(rotl64(x,31)&rotl64(x,11))^rotl64(x,29);
    x ^= rotl64(key,13);
    return x;}
