#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.99 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,34)&rotl64(x,54))|((~rotl64(x,34))&rotl64(x,33))) ^ rotl64(x,5));
    x = x ^ (((rotl64(x,23)&rotl64(x,56))|((~rotl64(x,23))&rotl64(x,35))) ^ rotl64(x,36));
    x = x ^ (((rotl64(x,53)&rotl64(x,8))|((~rotl64(x,53))&rotl64(x,2))) ^ rotl64(x,42));
    x = x ^ (((rotl64(x,28)&rotl64(x,40))|((~rotl64(x,28))&rotl64(x,63))) ^ rotl64(x,20));
    x = x ^ rotl64(x,38) ^ rotl64(x,14) ^ rotl64(x,59) ^ rotl64(x,58);
    x ^= rotl64(key, 13);
    return x;
}
