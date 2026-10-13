#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-37b two-lane repair (L=3), KEEP try hit1 (z=2.85) (no post-whiten)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t y = rotl64(val,45) ^ rotl64(key,32) ^ (rotl64(val,8) & rotl64(key,40));
    uint64_t xn, yn;
    xn = x ^ (rotl64(x,10) & rotl64(x,20)) ^ (rotl64(x,11) & rotl64(y,49)) ^ rotl64(x,61) ^ rotl64(x,8) ^ rotl64(x,4);
    yn = y ^ (rotl64(y,59) & rotl64(y,51)) ^ (rotl64(x,48) & rotl64(y,7)) ^ rotl64(y,46) ^ rotl64(y,31) ^ rotl64(y,40);
    x = xn; y = yn;
    xn = x ^ (rotl64(x,16) & rotl64(x,40)) ^ (rotl64(x,63) & rotl64(y,53)) ^ rotl64(x,25) ^ rotl64(x,16) ^ rotl64(x,1);
    yn = y ^ (rotl64(y,46) & rotl64(y,59)) ^ (rotl64(x,33) & rotl64(y,25)) ^ rotl64(y,12) ^ rotl64(y,39) ^ rotl64(y,25);
    x = xn; y = yn;
    xn = x ^ (rotl64(x,31) & rotl64(x,30)) ^ (rotl64(x,28) & rotl64(y,36)) ^ rotl64(x,45) ^ rotl64(x,32) ^ rotl64(x,52);
    yn = y ^ (rotl64(y,11) & rotl64(y,33)) ^ (rotl64(x,39) & rotl64(y,61)) ^ rotl64(y,20) ^ rotl64(y,41) ^ rotl64(y,33);
    x = xn; y = yn;
    return x ^ rotl64(y,22);
}
