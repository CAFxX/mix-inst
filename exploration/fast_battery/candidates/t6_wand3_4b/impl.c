#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_wand3_4b: 4-stage AND3+spread, al key schedule
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,1)&rotl64(x,2)&rotl64(x,3)) ^ rotl64(x,13);
    x ^= (rotl64(x,11)&rotl64(x,12)&rotl64(x,13)) ^ rotl64(x,5);
    x ^= (rotl64(x,5)&rotl64(x,6)&rotl64(x,7)) ^ rotl64(x,29);
    x ^= (rotl64(x,17)&rotl64(x,18)&rotl64(x,19)) ^ rotl64(x,7);
    return x ^ rotl64(key,13);
}
