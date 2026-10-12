#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=2.83 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,15)&rotl64(x,21))|((~rotl64(x,15))&rotl64(x,13))) ^ rotl64(x,16));
    x = x ^ (((rotl64(x,58)&rotl64(x,5))|((~rotl64(x,58))&rotl64(x,33))) ^ rotl64(x,25));
    x = x ^ (((rotl64(x,33)&rotl64(x,47))|((~rotl64(x,33))&rotl64(x,27))) ^ rotl64(x,62));
    x = x ^ (((rotl64(x,1)&rotl64(x,41))|((~rotl64(x,1))&rotl64(x,47))) ^ rotl64(x,22));
    x = x ^ (((rotl64(x,8)&rotl64(x,9))|((~rotl64(x,8))&rotl64(x,23))) ^ rotl64(x,59));
    x ^= rotl64(key, 13);
    return x;
}
