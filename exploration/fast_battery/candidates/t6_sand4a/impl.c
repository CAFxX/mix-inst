#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_sand4a: 4-stage AND-sandwich, sched C (wall probe)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= rotl64(x,7) ^ (rotl64(x,1)&rotl64(x,2)) ^ rotl64(x,19);
    x ^= rotl64(x,23) ^ (rotl64(x,5)&rotl64(x,6)) ^ rotl64(x,11);
    x ^= rotl64(x,39) ^ (rotl64(x,9)&rotl64(x,10)) ^ rotl64(x,3);
    x ^= rotl64(x,15) ^ (rotl64(x,13)&rotl64(x,14)) ^ rotl64(x,47);
    return x ^ rotl64(key,13);
}
