#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.46 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,13)&rotl64(x,54))|((~rotl64(x,13))&rotl64(x,23))) ^ rotl64(x,25));
    x = x ^ (((rotl64(x,53)&rotl64(x,47))|((~rotl64(x,53))&rotl64(x,9))) ^ rotl64(x,44));
    x = x ^ (((rotl64(x,60)&rotl64(x,63))|((~rotl64(x,60))&rotl64(x,53))) ^ rotl64(x,12));
    x = x ^ (((rotl64(x,4)&rotl64(x,15))|((~rotl64(x,4))&rotl64(x,42))) ^ rotl64(x,61));
    x = x ^ rotl64(x,15) ^ rotl64(x,21) ^ rotl64(x,5) ^ rotl64(x,24);
    x ^= rotl64(key, 13);
    return x;
}
