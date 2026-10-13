#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.55 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,38)&rotl64(x,3))|((~rotl64(x,38))&rotl64(x,16))) ^ rotl64(x,24));
    x = x ^ rotl64(x,38) ^ rotl64(x,28) ^ rotl64(x,18) ^ rotl64(x,57);
    x = x ^ (((rotl64(x,25)&rotl64(x,57))|((~rotl64(x,25))&rotl64(x,37))) ^ rotl64(x,25));
    x = x ^ (((rotl64(x,12)&rotl64(x,30))|((~rotl64(x,12))&rotl64(x,50))) ^ rotl64(x,33));
    x = x ^ (((rotl64(x,54)&rotl64(x,36))|((~rotl64(x,54))&rotl64(x,47))) ^ rotl64(x,7));
    x ^= rotl64(key, 13);
    return x;
}
