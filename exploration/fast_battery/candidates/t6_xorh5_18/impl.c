#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.62 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,23) ^ rotl64(x,47) ^ rotl64(x,3) ^ rotl64(x,51);
    x = x ^ (((rotl64(x,50)&rotl64(x,38))|((~rotl64(x,50))&rotl64(x,46))) ^ rotl64(x,0));
    x = x ^ (((rotl64(x,13)&rotl64(x,26))|((~rotl64(x,13))&rotl64(x,62))) ^ rotl64(x,4));
    x = x ^ (((rotl64(x,13)&rotl64(x,50))|((~rotl64(x,13))&rotl64(x,25))) ^ rotl64(x,11));
    x = x ^ (((rotl64(x,53)&rotl64(x,45))|((~rotl64(x,53))&rotl64(x,57))) ^ rotl64(x,9));
    x ^= rotl64(key, 13);
    return x;
}
