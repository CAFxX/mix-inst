#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_sand5a: 5-stage AND-sandwich x^=ra^(rb&rc)^rd, sched A
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= rotl64(x,3) ^ (rotl64(x,1)&rotl64(x,2)) ^ rotl64(x,7);
    x ^= rotl64(x,11) ^ (rotl64(x,5)&rotl64(x,6)) ^ rotl64(x,23);
    x ^= rotl64(x,19) ^ (rotl64(x,9)&rotl64(x,10)) ^ rotl64(x,41);
    x ^= rotl64(x,27) ^ (rotl64(x,13)&rotl64(x,14)) ^ rotl64(x,29);
    x ^= rotl64(x,35) ^ (rotl64(x,17)&rotl64(x,18)) ^ rotl64(x,11);
    return x ^ rotl64(key,13);
}
