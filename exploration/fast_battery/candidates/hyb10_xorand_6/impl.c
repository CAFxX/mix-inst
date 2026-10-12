// hyb10_xorand_6: 6-stage XOR-AND: x ^= ra ^ (rb & rc) (parallel structure)
#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra=rotl64(x,1),rb=rotl64(x,2),rc=rotl64(x,13);
      x ^= ra ^ (rb & rc); }
    { uint64_t ra=rotl64(x,7),rb=rotl64(x,19),rc=rotl64(x,5);
      x ^= ra ^ (rb & rc); }
    { uint64_t ra=rotl64(x,3),rb=rotl64(x,11),rc=rotl64(x,29);
      x ^= ra ^ (rb & rc); }
    { uint64_t ra=rotl64(x,17),rb=rotl64(x,31),rc=rotl64(x,7);
      x ^= ra ^ (rb & rc); }
    { uint64_t ra=rotl64(x,11),rb=rotl64(x,23),rc=rotl64(x,37);
      x ^= ra ^ (rb & rc); }
    { uint64_t ra=rotl64(x,19),rb=rotl64(x,41),rc=rotl64(x,23);
      x ^= ra ^ (rb & rc); }
    x ^= rotl64(key, 13);
    return x;
}
