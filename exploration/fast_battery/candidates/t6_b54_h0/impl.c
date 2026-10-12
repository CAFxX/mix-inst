#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=2.96, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,7)&rotl64(x,8))|((~rotl64(x,7))&rotl64(x,17))) ^ rotl64(x,51));
    x = x ^ (rotl64(x,3) & rotl64(x,16)) ^ rotl64(x,63);
    x = x ^ (((rotl64(x,14)&rotl64(x,11))|((~rotl64(x,14))&rotl64(x,36))) ^ rotl64(x,28));
    x = x ^ (((rotl64(x,54)&rotl64(x,62))|((~rotl64(x,54))&rotl64(x,29))) ^ rotl64(x,40));
    x = x ^ (((rotl64(x,55)&rotl64(x,24))|((~rotl64(x,55))&rotl64(x,53))) ^ rotl64(x,33));
    x ^= rotl64(key, 13);
    return x;
}
