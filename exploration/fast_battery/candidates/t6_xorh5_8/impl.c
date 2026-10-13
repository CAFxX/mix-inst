#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.93 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,47) ^ rotl64(x,35) ^ rotl64(x,36) ^ rotl64(x,9);
    x = x ^ (((rotl64(x,23)&rotl64(x,46))|((~rotl64(x,23))&rotl64(x,58))) ^ rotl64(x,18));
    x = x ^ (((rotl64(x,37)&rotl64(x,12))|((~rotl64(x,37))&rotl64(x,41))) ^ rotl64(x,14));
    x = x ^ (((rotl64(x,34)&rotl64(x,52))|((~rotl64(x,34))&rotl64(x,61))) ^ rotl64(x,19));
    x = x ^ (((rotl64(x,53)&rotl64(x,42))|((~rotl64(x,53))&rotl64(x,1))) ^ rotl64(x,22));
    x ^= rotl64(key, 13);
    return x;
}
