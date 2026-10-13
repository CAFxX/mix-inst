#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.89 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,22)&rotl64(x,14))|((~rotl64(x,22))&rotl64(x,61))) ^ rotl64(x,47));
    x = x ^ rotl64(x,12) ^ rotl64(x,35) ^ rotl64(x,14) ^ rotl64(x,55);
    x = x ^ (((rotl64(x,10)&rotl64(x,60))|((~rotl64(x,10))&rotl64(x,30))) ^ rotl64(x,60));
    x = x ^ (((rotl64(x,37)&rotl64(x,7))|((~rotl64(x,37))&rotl64(x,54))) ^ rotl64(x,25));
    x = x ^ (((rotl64(x,54)&rotl64(x,47))|((~rotl64(x,54))&rotl64(x,17))) ^ rotl64(x,37));
    x ^= rotl64(key, 13);
    return x;
}
