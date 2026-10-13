#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.96 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,62) ^ rotl64(x,30) ^ rotl64(x,60) ^ rotl64(x,13);
    x = x ^ (((rotl64(x,6)&rotl64(x,51))|((~rotl64(x,6))&rotl64(x,7))) ^ rotl64(x,63));
    x = x ^ (((rotl64(x,12)&rotl64(x,50))|((~rotl64(x,12))&rotl64(x,32))) ^ rotl64(x,25));
    x = x ^ (((rotl64(x,30)&rotl64(x,48))|((~rotl64(x,30))&rotl64(x,1))) ^ rotl64(x,62));
    x = x ^ (((rotl64(x,16)&rotl64(x,28))|((~rotl64(x,16))&rotl64(x,31))) ^ rotl64(x,56));
    x ^= rotl64(key, 13);
    return x;
}
