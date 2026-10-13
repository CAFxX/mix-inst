#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.19 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,2)&rotl64(x,60))|((~rotl64(x,2))&rotl64(x,38))) ^ rotl64(x,29));
    x = x ^ rotl64(x,17) ^ rotl64(x,7) ^ rotl64(x,47) ^ rotl64(x,48);
    x = x ^ (((rotl64(x,21)&rotl64(x,17))|((~rotl64(x,21))&rotl64(x,3))) ^ rotl64(x,12));
    x = x ^ (((rotl64(x,1)&rotl64(x,22))|((~rotl64(x,1))&rotl64(x,12))) ^ rotl64(x,18));
    x = x ^ (((rotl64(x,32)&rotl64(x,11))|((~rotl64(x,32))&rotl64(x,23))) ^ rotl64(x,25));
    x ^= rotl64(key, 13);
    return x;
}
