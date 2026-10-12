#include <stdint.h>
/* fz14_tchi3a: gen_fused14.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    { uint64_t r[] = {1, 7, 13, 19, 29, 37, 5};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ (rotl64(x,r[4]) & rotl64(x,r[5])) ^ rotl64(x,r[6]); }
    { uint64_t r[] = {7, 15, 25, 35, 45, 55, 13};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ (rotl64(x,r[4]) & rotl64(x,r[5])) ^ rotl64(x,r[6]); }
    { uint64_t r[] = {13, 23, 33, 43, 53, 61, 21};
      x = x ^ (rotl64(x,r[0]) & rotl64(x,r[1])) ^ (rotl64(x,r[2]) & rotl64(x,r[3])) ^ (rotl64(x,r[4]) & rotl64(x,r[5])) ^ rotl64(x,r[6]); }
    x = x ^ rotl64(k, 13);
    return x;
}
