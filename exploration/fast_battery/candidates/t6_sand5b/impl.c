#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_sand5b: 5-stage AND-sandwich x^=ra^(rb&rc)^rd, sched B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= rotl64(x,5) ^ (rotl64(x,3)&rotl64(x,4)) ^ rotl64(x,13);
    x ^= rotl64(x,17) ^ (rotl64(x,7)&rotl64(x,8)) ^ rotl64(x,31);
    x ^= rotl64(x,29) ^ (rotl64(x,11)&rotl64(x,12)) ^ rotl64(x,5);
    x ^= rotl64(x,41) ^ (rotl64(x,15)&rotl64(x,16)) ^ rotl64(x,43);
    x ^= rotl64(x,9) ^ (rotl64(x,19)&rotl64(x,20)) ^ rotl64(x,27);
    return x ^ rotl64(key,13);
}
