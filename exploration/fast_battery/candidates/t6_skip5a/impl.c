#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_skip5a: 5-stage skip-coupled cascade (x-state residual)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key, xm1 = 0;
    { uint64_t xn = x ^ (rotl64(x,1)&rotl64(x,2)) ^ rotl64(x,7) ^ rotl64(xm1,13);
      xm1 = x; x = xn; }
    { uint64_t xn = x ^ (rotl64(x,5)&rotl64(x,6)) ^ rotl64(x,23) ^ rotl64(xm1,29);
      xm1 = x; x = xn; }
    { uint64_t xn = x ^ (rotl64(x,9)&rotl64(x,10)) ^ rotl64(x,41) ^ rotl64(xm1,3);
      xm1 = x; x = xn; }
    { uint64_t xn = x ^ (rotl64(x,13)&rotl64(x,14)) ^ rotl64(x,29) ^ rotl64(xm1,47);
      xm1 = x; x = xn; }
    { uint64_t xn = x ^ (rotl64(x,17)&rotl64(x,18)) ^ rotl64(x,11) ^ rotl64(xm1,59);
      xm1 = x; x = xn; }
    return x ^ rotl64(key,13);
}
