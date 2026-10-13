#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.57 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,39)&rotl64(x,60))|((~rotl64(x,39))&rotl64(x,54))) ^ rotl64(x,9));
    x = x ^ (((rotl64(x,8)&rotl64(x,62))|((~rotl64(x,8))&rotl64(x,48))) ^ rotl64(x,38));
    x = x ^ (((rotl64(x,29)&rotl64(x,19))|((~rotl64(x,29))&rotl64(x,33))) ^ rotl64(x,29));
    x = x ^ (((rotl64(x,47)&rotl64(x,32))|((~rotl64(x,47))&rotl64(x,24))) ^ rotl64(x,30));
    x = x ^ rotl64(x,59) ^ rotl64(x,56) ^ rotl64(x,36) ^ rotl64(x,41);
    x ^= rotl64(key, 13);
    return x;
}
