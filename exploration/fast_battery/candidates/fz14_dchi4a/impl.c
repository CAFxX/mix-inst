#include <stdint.h>
/* fz14_dchi4a: gen_fused14.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    { uint64_t r[] = {1, 7, 13, 29, 5};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    { uint64_t r[] = {5, 13, 23, 41, 11};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    { uint64_t r[] = {11, 23, 33, 51, 17};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    { uint64_t r[] = {17, 31, 43, 59, 23};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ rotl64(x,r[4]); }
    x = x ^ rotl64(k, 13);
    return x;
}
