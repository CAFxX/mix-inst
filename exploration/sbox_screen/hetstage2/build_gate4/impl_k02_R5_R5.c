#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint64_t gfmul_c(uint64_t x, uint64_t C) {
    /* carryless multiply x*C, reduce mod z^64+z^4+z^3+z+1 */
    __uint128_t p = 0;
    uint64_t cc = C; int b = 0;
    while (cc) { if (cc & 1) p ^= (__uint128_t)x << b;
                 cc >>= 1; b++; }
    for (int i = 127; i >= 64; i--)
        if ((p >> i) & 1) p ^= (__uint128_t)0x1BU << (i - 64);
    return (uint64_t)p;
}
// hetstage2 gate4 k02_R5_R5
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,39) ^ rotl64(x,36);
    x = x ^ (((rotl64(x,7)&rotl64(x,1))|((~rotl64(x,7))&rotl64(x,63))) ^ rotl64(x,44));
    x = x ^ (((rotl64(x,62)&rotl64(x,51))|((~rotl64(x,62))&rotl64(x,20))) ^ rotl64(x,31));
    x = x ^ (((rotl64(x,21)&rotl64(x,32))|((~rotl64(x,21))&rotl64(x,39))) ^ rotl64(x,1));
    x = x ^ (((rotl64(x,17)&rotl64(x,32))|((~rotl64(x,17))&rotl64(x,53))) ^ rotl64(x,62));
    x ^= rotl64(key, 13);
    return x;
}
