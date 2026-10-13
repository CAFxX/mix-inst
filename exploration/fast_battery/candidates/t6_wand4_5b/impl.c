#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_wand4_5b: 5-stage AND4+spread, al key schedule
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1)&rotl64(x,2)&rotl64(x,3)&rotl64(x,4)) ^ rotl64(x,13);
    x ^= (rotl64(x,11)&rotl64(x,12)&rotl64(x,13)&rotl64(x,14)) ^ rotl64(x,29);
    x ^= (rotl64(x,21)&rotl64(x,22)&rotl64(x,23)&rotl64(x,24)) ^ rotl64(x,7);
    x ^= (rotl64(x,31)&rotl64(x,32)&rotl64(x,33)&rotl64(x,34)) ^ rotl64(x,37);
    x ^= (rotl64(x,41)&rotl64(x,42)&rotl64(x,43)&rotl64(x,44)) ^ rotl64(x,17);
    return x ^ rotl64(key,13);
}
