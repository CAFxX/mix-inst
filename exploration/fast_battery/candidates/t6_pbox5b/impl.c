#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t chi64(uint64_t x){uint64_t r1=rotl64(x,63),r2=rotl64(x,62);return x^((~r1)&r2);}
// t6_pbox5b: 5-stage AND + byte-transpose diffusion
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    static const int PB[64] = {0,8,16,24,32,40,48,56,9,17,25,33,41,49,57,1,18,26,34,42,50,58,2,10,27,35,43,51,59,3,11,19,36,44,52,60,4,12,20,28,45,53,61,5,13,21,29,37,54,62,6,14,22,30,38,46,63,7,15,23,31,39,47,55};
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
