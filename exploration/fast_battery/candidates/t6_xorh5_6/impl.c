#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.87 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,8)&rotl64(x,5))|((~rotl64(x,8))&rotl64(x,10))) ^ rotl64(x,46));
    x = x ^ (((rotl64(x,5)&rotl64(x,30))|((~rotl64(x,5))&rotl64(x,8))) ^ rotl64(x,32));
    x = x ^ (((rotl64(x,6)&rotl64(x,19))|((~rotl64(x,6))&rotl64(x,4))) ^ rotl64(x,60));
    x = x ^ (((rotl64(x,47)&rotl64(x,23))|((~rotl64(x,47))&rotl64(x,44))) ^ rotl64(x,48));
    x = x ^ rotl64(x,22) ^ rotl64(x,42) ^ rotl64(x,41) ^ rotl64(x,27);
    x ^= rotl64(key, 13);
    return x;
}
