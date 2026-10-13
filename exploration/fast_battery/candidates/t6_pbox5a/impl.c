#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t chi64(uint64_t x){uint64_t r1=rotl64(x,63),r2=rotl64(x,62);return x^((~r1)&r2);}
// t6_pbox5a: 5-stage AND + bit-reversal diffusion
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    static const int PB[64] = {63,62,61,60,59,58,57,56,55,54,53,52,51,50,49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0};
    { uint64_t px=0; for(int i=0;i<64;i++) px |= ((x>>PB[i])&1ULL)<<i;
      x ^= (rotl64(x,1)&rotl64(x,2)) ^ px; }
    { uint64_t px=0; for(int i=0;i<64;i++) px |= ((x>>PB[i])&1ULL)<<i;
      x ^= (rotl64(x,5)&rotl64(x,6)) ^ px; }
    { uint64_t px=0; for(int i=0;i<64;i++) px |= ((x>>PB[i])&1ULL)<<i;
      x ^= (rotl64(x,9)&rotl64(x,10)) ^ px; }
    { uint64_t px=0; for(int i=0;i<64;i++) px |= ((x>>PB[i])&1ULL)<<i;
      x ^= (rotl64(x,13)&rotl64(x,14)) ^ px; }
    { uint64_t px=0; for(int i=0;i<64;i++) px |= ((x>>PB[i])&1ULL)<<i;
      x ^= (rotl64(x,17)&rotl64(x,18)) ^ px; }
    return x ^ rotl64(key,13);
}
