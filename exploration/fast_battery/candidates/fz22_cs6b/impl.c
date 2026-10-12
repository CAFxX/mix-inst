#include <stdint.h>
/* fz22_cs6b: gen_fused22.py */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t s = v ^ k;
    uint64_t c = rotl64(k, 13);
    { uint64_t ra = rotl64(s, 3), rb = rotl64(c, 13);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra ^ rb;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 9), rb = rotl64(c, 23);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra ^ rb;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 15), rb = rotl64(c, 33);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra ^ rb;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 21), rb = rotl64(c, 41);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra ^ rb;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 27), rb = rotl64(c, 49);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra ^ rb;
       c = rotl64(m, 1); }
    { uint64_t ra = rotl64(s, 35), rb = rotl64(c, 53);
       uint64_t m = (s & c) | (s & ra) | (c & ra);
       s = s ^ c ^ ra ^ rb;
       c = rotl64(m, 1); }
    uint64_t sc = s ^ c;
    return sc ^ rotl64(sc, 17);
}
