#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.00 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,17) ^ rotl64(x,35) ^ rotl64(x,37) ^ rotl64(x,29);
    x = x ^ (((rotl64(x,39)&rotl64(x,63))|((~rotl64(x,39))&rotl64(x,12))) ^ rotl64(x,61));
    x = x ^ (((rotl64(x,50)&rotl64(x,48))|((~rotl64(x,50))&rotl64(x,5))) ^ rotl64(x,18));
    x = x ^ (((rotl64(x,33)&rotl64(x,55))|((~rotl64(x,33))&rotl64(x,1))) ^ rotl64(x,5));
    x = x ^ (((rotl64(x,10)&rotl64(x,33))|((~rotl64(x,10))&rotl64(x,7))) ^ rotl64(x,28));
    x ^= rotl64(key, 13);
    return x;
}
