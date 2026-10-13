#include <stdint.h>
static inline uint32_t rotl32(uint32_t x,int r){r&=31;return r?(x<<r)|(x>>(32-r)):x;}
// t6_feist4a: 4-round Feistel, F=2-stage 32-bit AND-cascade
static inline uint32_t F_and2(uint32_t R, uint32_t rk, int s0a,int s0b,int s0c,int s1a,int s1b,int s1c){
    uint32_t x=R;
    x ^= (rotl32(x,s0a)&rotl32(x,s0b))^rotl32(x,s0c);
    x ^= (rotl32(x,s1a)&rotl32(x,s1b))^rotl32(x,s1c);
    return x ^ rk;}
uint64_t mix_hash(uint64_t val,uint64_t key){
    uint32_t L=(val^key)>>32, R=(uint32_t)(val^key);
    uint32_t kh=key>>32, kl=(uint32_t)key;
    static const uint32_t RC[4]={0x9E3779B9u,0x3C6EF372u,0xDAA66D2Cu,0x78DDE6E5u};
    {uint32_t F=F_and2(R,(rotl32(kl,7)^RC[0]),5,13,29,11,23,7);
     uint32_t nL=R, nR=L^F; L=nL; R=nR;}
    {uint32_t F=F_and2(R,(rotl32(kl,14)^RC[1]),5,13,29,11,23,7);
     uint32_t nL=R, nR=L^F; L=nL; R=nR;}
    {uint32_t F=F_and2(R,(rotl32(kl,21)^RC[2]),5,13,29,11,23,7);
     uint32_t nL=R, nR=L^F; L=nL; R=nR;}
    {uint32_t F=F_and2(R,(rotl32(kl,28)^RC[3]),5,13,29,11,23,7);
     uint32_t nL=R, nR=L^F; L=nL; R=nR;}
    return (((uint64_t)R)<<32 | L) ^ key;}
