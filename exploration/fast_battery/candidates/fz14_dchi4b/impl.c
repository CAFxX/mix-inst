#include <stdint.h>
/* fz14_dchi4b: gen_fused14.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    { uint64_t r[] = {2, 9, 17, 35, 7};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    { uint64_t r[] = {7, 15, 27, 45, 13};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    { uint64_t r[] = {13, 25, 37, 55, 19};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    { uint64_t r[] = {19, 33, 47, 61, 27};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    x = x ^ rotl64(k, 13);
    return x;
}
