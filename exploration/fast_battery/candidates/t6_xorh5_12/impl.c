#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=3.02 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,41)&rotl64(x,49))|((~rotl64(x,41))&rotl64(x,1))) ^ rotl64(x,32));
    x = x ^ rotl64(x,34) ^ rotl64(x,37) ^ rotl64(x,3) ^ rotl64(x,9);
    x = x ^ (((rotl64(x,53)&rotl64(x,42))|((~rotl64(x,53))&rotl64(x,0))) ^ rotl64(x,6));
    x = x ^ (((rotl64(x,63)&rotl64(x,56))|((~rotl64(x,63))&rotl64(x,4))) ^ rotl64(x,20));
    x = x ^ (((rotl64(x,26)&rotl64(x,20))|((~rotl64(x,26))&rotl64(x,2))) ^ rotl64(x,38));
    x ^= rotl64(key, 13);
    return x;
}
