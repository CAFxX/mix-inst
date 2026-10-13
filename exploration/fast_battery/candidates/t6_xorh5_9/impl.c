#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.95 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,53)&rotl64(x,61))|((~rotl64(x,53))&rotl64(x,59))) ^ rotl64(x,54));
    x = x ^ (((rotl64(x,1)&rotl64(x,14))|((~rotl64(x,1))&rotl64(x,56))) ^ rotl64(x,44));
    x = x ^ (((rotl64(x,36)&rotl64(x,39))|((~rotl64(x,36))&rotl64(x,26))) ^ rotl64(x,54));
    x = x ^ (((rotl64(x,45)&rotl64(x,48))|((~rotl64(x,45))&rotl64(x,55))) ^ rotl64(x,58));
    x = x ^ rotl64(x,46) ^ rotl64(x,3) ^ rotl64(x,20) ^ rotl64(x,13);
    x ^= rotl64(key, 13);
    return x;
}
