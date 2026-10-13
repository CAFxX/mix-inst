#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_wand3_5d: 5-stage AND3+spread, al key schedule, sched B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,3)&rotl64(x,4)&rotl64(x,5)) ^ rotl64(x,23);
    x ^= (rotl64(x,13)&rotl64(x,14)&rotl64(x,15)) ^ rotl64(x,41);
    x ^= (rotl64(x,7)&rotl64(x,8)&rotl64(x,9)) ^ rotl64(x,17);
    x ^= (rotl64(x,21)&rotl64(x,22)&rotl64(x,23)) ^ rotl64(x,11);
    x ^= (rotl64(x,29)&rotl64(x,30)&rotl64(x,31)) ^ rotl64(x,43);
    return x ^ rotl64(key,13);
}
