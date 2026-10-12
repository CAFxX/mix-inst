#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// al_linchi3: 3 rounds of (lin + chi)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    // Round 1: lin(5,13) then chi(1,2,13)
    x ^= rotl64(x, 5) ^ rotl64(x, 13);
    x ^= ((~rotl64(x, 1)) & rotl64(x, 2)) ^ rotl64(x, 13);
    // Round 2: lin(11,29) then chi(7,19,5)
    x ^= rotl64(x, 11) ^ rotl64(x, 29);
    x ^= ((~rotl64(x, 7)) & rotl64(x, 19)) ^ rotl64(x, 5);
    // Round 3: lin(7,23) then chi(3,11,29)
    x ^= rotl64(x, 7) ^ rotl64(x, 23);
    x ^= ((~rotl64(x, 3)) & rotl64(x, 11)) ^ rotl64(x, 29);
    x ^= rotl64(key, 13);
    return x;
}
