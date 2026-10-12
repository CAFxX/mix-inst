// hyb20_dm4a: batch-20 fused maj+chi [dm4]: dm(47,26,63,62,7,8) -> dm(63,47,4,59,25,45) -> dm(45,43,18,11,49,62) -> dm(47,11,53,34,10,23) (hill-climbed proxy z=6.6, est=18.80u)
#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {
    return (a & b) | (b & c) | (a & c); }
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra=rotl64(x,47),rb=rotl64(x,26),rc=rotl64(x,63),rd=rotl64(x,62),re=rotl64(x,7),rf=rotl64(x,8);
      x ^= maj64(x,ra,rb) ^ rc ^ maj64(x,rd,re) ^ rf; }
    { uint64_t ra=rotl64(x,63),rb=rotl64(x,47),rc=rotl64(x,4),rd=rotl64(x,59),re=rotl64(x,25),rf=rotl64(x,45);
      x ^= maj64(x,ra,rb) ^ rc ^ maj64(x,rd,re) ^ rf; }
    { uint64_t ra=rotl64(x,45),rb=rotl64(x,43),rc=rotl64(x,18),rd=rotl64(x,11),re=rotl64(x,49),rf=rotl64(x,62);
      x ^= maj64(x,ra,rb) ^ rc ^ maj64(x,rd,re) ^ rf; }
    { uint64_t ra=rotl64(x,47),rb=rotl64(x,11),rc=rotl64(x,53),rd=rotl64(x,34),re=rotl64(x,10),rf=rotl64(x,23);
      x ^= maj64(x,ra,rb) ^ rc ^ maj64(x,rd,re) ^ rf; }
    return x;
}
