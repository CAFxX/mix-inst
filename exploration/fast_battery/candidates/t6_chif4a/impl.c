#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
static uint64_t chi64(uint64_t x){uint64_t r1=rotl64(x,63),r2=rotl64(x,62);return x^((~r1)&r2);}
// t6_chif4a: 4-stage AND + chi-final
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1)&rotl64(x,2)) ^ rotl64(x,7);
    x ^= (rotl64(x,5)&rotl64(x,6)) ^ rotl64(x,23);
    x ^= (rotl64(x,9)&rotl64(x,10)) ^ rotl64(x,41);
    x ^= (rotl64(x,13)&rotl64(x,14)) ^ rotl64(x,29);
    return chi64(x) ^ rotl64(key,13);
}
