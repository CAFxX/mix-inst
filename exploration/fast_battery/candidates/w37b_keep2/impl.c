#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-37b two-lane repair (L=3), KEEP try hit2 (z=5.76)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t y = rotl64(val,35) ^ rotl64(key,10) ^ (rotl64(val,24) & rotl64(key,1));
    uint64_t xn, yn;
    xn = x ^ (rotl64(x,39) & rotl64(x,29)) ^ (rotl64(x,29) & rotl64(y,53)) ^ rotl64(x,17) ^ rotl64(x,44) ^ rotl64(x,52);
    yn = y ^ (rotl64(y,28) & rotl64(y,41)) ^ (rotl64(x,29) & rotl64(y,5)) ^ rotl64(y,56) ^ rotl64(y,53) ^ rotl64(y,63);
    x = xn; y = yn;
    xn = x ^ (rotl64(x,34) & rotl64(x,2)) ^ (rotl64(x,36) & rotl64(y,15)) ^ rotl64(x,25) ^ rotl64(x,11) ^ rotl64(x,10);
    yn = y ^ (rotl64(y,12) & rotl64(y,14)) ^ (rotl64(x,46) & rotl64(y,7)) ^ rotl64(y,8) ^ rotl64(y,27) ^ rotl64(y,59);
    x = xn; y = yn;
    xn = x ^ (rotl64(x,62) & rotl64(x,47)) ^ (rotl64(x,4) & rotl64(y,41)) ^ rotl64(x,13) ^ rotl64(x,5) ^ rotl64(x,60);
    yn = y ^ (rotl64(y,11) & rotl64(y,33)) ^ (rotl64(x,42) & rotl64(y,59)) ^ rotl64(y,25) ^ rotl64(y,46) ^ rotl64(y,23);
    x = xn; y = yn;
    return x ^ rotl64(y,56) ^ rotl64(key, 13);
}
