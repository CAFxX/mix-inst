#include <stdint.h>
static uint64_t rotl64(uint64_t x,int r){r&=63;return r?(x<<r)|(x>>(64-r)):x;}
// t6_lane4a: 4+4 cross-fed dual-lane cascade, sched A
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t a = val ^ key, b = rotl64(key,29);
    { uint64_t an = a ^ (rotl64(a,1)&rotl64(a,2)) ^ rotl64(a,7);
      uint64_t bn = b ^ (rotl64(b,17)&rotl64(b,18)) ^ rotl64(b,11) ^ rotl64(a,3);
      a = an; b = bn; }
    { uint64_t an = a ^ (rotl64(a,5)&rotl64(a,6)) ^ rotl64(a,23);
      uint64_t bn = b ^ (rotl64(b,21)&rotl64(b,22)) ^ rotl64(b,37) ^ rotl64(a,17);
      a = an; b = bn; }
    { uint64_t an = a ^ (rotl64(a,9)&rotl64(a,10)) ^ rotl64(a,41);
      uint64_t bn = b ^ (rotl64(b,25)&rotl64(b,26)) ^ rotl64(b,3) ^ rotl64(a,31);
      a = an; b = bn; }
    { uint64_t an = a ^ (rotl64(a,13)&rotl64(a,14)) ^ rotl64(a,29);
      uint64_t bn = b ^ (rotl64(b,29)&rotl64(b,30)) ^ rotl64(b,19) ^ rotl64(a,43);
      a = an; b = bn; }
    return a ^ b ^ rotl64(key,13);
}
