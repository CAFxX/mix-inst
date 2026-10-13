#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_lane3b: 3+3 cross-fed dual-lane cascade, sched B
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t a = val ^ key, b = rotl64(key,29);
    { uint64_t an = a ^ (rotl64(a,3)&rotl64(a,4)) ^ rotl64(a,13);
      uint64_t bn = b ^ (rotl64(b,15)&rotl64(b,16)) ^ rotl64(b,43) ^ rotl64(a,23);
      a = an; b = bn; }
    { uint64_t an = a ^ (rotl64(a,7)&rotl64(a,8)) ^ rotl64(a,31);
      uint64_t bn = b ^ (rotl64(b,19)&rotl64(b,20)) ^ rotl64(b,27) ^ rotl64(a,7);
      a = an; b = bn; }
    { uint64_t an = a ^ (rotl64(a,11)&rotl64(a,12)) ^ rotl64(a,5);
      uint64_t bn = b ^ (rotl64(b,23)&rotl64(b,24)) ^ rotl64(b,9) ^ rotl64(a,37);
      a = an; b = bn; }
    return a ^ b ^ rotl64(key,13);
}
