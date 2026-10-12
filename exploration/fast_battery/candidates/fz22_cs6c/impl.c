#include <stdint.h>
/* fz22_cs6c: gen_fused22.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t s = v ^ k;
    uint64_t c = rotl64(k, 13);
    { uint64_t ra = rotl64(s, 11);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 19);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 29);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 37);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 43);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 47);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra;
       c = rotl64(m, 1); }
    uint64_t sc = s ^ c;
    return sc ^ rotl64(sc, 17);
}
