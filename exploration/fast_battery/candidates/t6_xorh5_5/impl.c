#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.73 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,19) ^ rotl64(x,20) ^ rotl64(x,58) ^ rotl64(x,28);
    x = x ^ (((rotl64(x,29)&rotl64(x,55))|((~rotl64(x,29))&rotl64(x,28))) ^ rotl64(x,1));
    x = x ^ (((rotl64(x,30)&rotl64(x,28))|((~rotl64(x,30))&rotl64(x,0))) ^ rotl64(x,41));
    x = x ^ (((rotl64(x,15)&rotl64(x,59))|((~rotl64(x,15))&rotl64(x,57))) ^ rotl64(x,19));
    x = x ^ (((rotl64(x,18)&rotl64(x,28))|((~rotl64(x,18))&rotl64(x,63))) ^ rotl64(x,10));
    x ^= rotl64(key, 13);
    return x;
}
