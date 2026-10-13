#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.61 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,62) ^ rotl64(x,13) ^ rotl64(x,28) ^ rotl64(x,57);
    x = x ^ (((rotl64(x,52)&rotl64(x,31))|((~rotl64(x,52))&rotl64(x,9))) ^ rotl64(x,39));
    x = x ^ (((rotl64(x,9)&rotl64(x,50))|((~rotl64(x,9))&rotl64(x,20))) ^ rotl64(x,47));
    x = x ^ (((rotl64(x,18)&rotl64(x,39))|((~rotl64(x,18))&rotl64(x,29))) ^ rotl64(x,35));
    x = x ^ (((rotl64(x,5)&rotl64(x,30))|((~rotl64(x,5))&rotl64(x,25))) ^ rotl64(x,61));
    x ^= rotl64(key, 13);
    return x;
}
