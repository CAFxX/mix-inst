#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.43 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,29) ^ rotl64(x,7) ^ rotl64(x,42) ^ rotl64(x,55);
    x = x ^ (((rotl64(x,13)&rotl64(x,51))|((~rotl64(x,13))&rotl64(x,7))) ^ rotl64(x,46));
    x = x ^ (((rotl64(x,3)&rotl64(x,21))|((~rotl64(x,3))&rotl64(x,55))) ^ rotl64(x,56));
    x = x ^ (((rotl64(x,58)&rotl64(x,32))|((~rotl64(x,58))&rotl64(x,15))) ^ rotl64(x,14));
    x = x ^ (((rotl64(x,56)&rotl64(x,53))|((~rotl64(x,56))&rotl64(x,36))) ^ rotl64(x,15));
    x ^= rotl64(key, 13);
    return x;
}
