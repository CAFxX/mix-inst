#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=9.44, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,3)&rotl64(x,14))|((~rotl64(x,3))&rotl64(x,23))) ^ rotl64(x,52));
    x = x ^ (rotl64(x,37) & rotl64(x,30)) ^ rotl64(x,14);
    x = x ^ (((rotl64(x,48)&rotl64(x,38))|((~rotl64(x,48))&rotl64(x,17))) ^ rotl64(x,21));
    x = x ^ (((rotl64(x,16)&rotl64(x,21))|((~rotl64(x,16))&rotl64(x,56))) ^ rotl64(x,26));
    x = x ^ (((rotl64(x,15)&rotl64(x,19))|((~rotl64(x,15))&rotl64(x,40))) ^ rotl64(x,36));
    x ^= rotl64(key, 13);
    return x;
}
