#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.29 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,19) ^ rotl64(x,26) ^ rotl64(x,20) ^ rotl64(x,42);
    x = x ^ (((rotl64(x,63)&rotl64(x,35))|((~rotl64(x,63))&rotl64(x,47))) ^ rotl64(x,51));
    x = x ^ (((rotl64(x,56)&rotl64(x,43))|((~rotl64(x,56))&rotl64(x,63))) ^ rotl64(x,9));
    x = x ^ (((rotl64(x,18)&rotl64(x,56))|((~rotl64(x,18))&rotl64(x,15))) ^ rotl64(x,20));
    x = x ^ (((rotl64(x,57)&rotl64(x,2))|((~rotl64(x,57))&rotl64(x,31))) ^ rotl64(x,54));
    x ^= rotl64(key, 13);
    return x;
}
