#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.26 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,7) ^ rotl64(x,60) ^ rotl64(x,28) ^ rotl64(x,40);
    x = x ^ (((rotl64(x,48)&rotl64(x,42))|((~rotl64(x,48))&rotl64(x,39))) ^ rotl64(x,48));
    x = x ^ (((rotl64(x,45)&rotl64(x,28))|((~rotl64(x,45))&rotl64(x,59))) ^ rotl64(x,23));
    x = x ^ (((rotl64(x,56)&rotl64(x,2))|((~rotl64(x,56))&rotl64(x,15))) ^ rotl64(x,13));
    x = x ^ (((rotl64(x,33)&rotl64(x,41))|((~rotl64(x,33))&rotl64(x,20))) ^ rotl64(x,61));
    x ^= rotl64(key, 13);
    return x;
}
