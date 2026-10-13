#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.56 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,56) ^ rotl64(x,37) ^ rotl64(x,20) ^ rotl64(x,13);
    x = x ^ (((rotl64(x,29)&rotl64(x,35))|((~rotl64(x,29))&rotl64(x,28))) ^ rotl64(x,12));
    x = x ^ (((rotl64(x,60)&rotl64(x,36))|((~rotl64(x,60))&rotl64(x,49))) ^ rotl64(x,21));
    x = x ^ (((rotl64(x,57)&rotl64(x,45))|((~rotl64(x,57))&rotl64(x,2))) ^ rotl64(x,6));
    x = x ^ (((rotl64(x,41)&rotl64(x,39))|((~rotl64(x,41))&rotl64(x,26))) ^ rotl64(x,22));
    x ^= rotl64(key, 13);
    return x;
}
