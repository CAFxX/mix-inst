/* Collision-forcing advantage: for chosen input delta, distribution of (dx & 0xFF).
 * Reports P(dx&0xFF==0) vs 1/256 and top-8 most likely low-8 differences.
 * Usage: ./colladv <key_hex> <delta_hex> [log2N]
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
static const uint8_t SBOX[16] = {0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2};
static const uint64_t GOLDEN = 0x9E3779B97F4A7C15ULL;
static uint64_t rotl64(uint64_t x, unsigned r){ r&=63; return r?(x<<r)|(x>>(64-r)):x; }
static uint64_t sbox_layer(uint64_t x){ uint64_t y=0; for(int b=0;b<16;b++) y|=(uint64_t)SBOX[(x>>(4*b))&0xF]<<(4*b); return y; }
static uint64_t mix_hash(uint64_t val, uint64_t key){
    uint64_t x = val ^ key;
    for(int i=0;i<4;i++){ uint64_t rk=rotl64(key,13*(i+1))^((uint64_t)(i+1)*GOLDEN);
        x^=rk; x=sbox_layer(x); x=x^rotl64(x,11)^rotl64(x,37); }
    return x ^ (rotl64(key,13*5)^((uint64_t)5*GOLDEN));
}
int main(int argc, char **argv){
    uint64_t key = strtoull(argv[1], NULL, 16);
    uint64_t dl = strtoull(argv[2], NULL, 16);
    int logN = argc>3?atoi(argv[3]):22;
    uint64_t N=1ULL<<logN, npairs=0;
    static uint64_t h8[256]; /* static to avoid stack overflow */
    for(uint64_t x=0;x<N;x++){ if(x>(x^dl)) continue; npairs++;
        h8[(mix_hash(x,key)^mix_hash(x^dl,key))&0xFF]++; }
    double e=(double)npairs/256.0;
    printf("delta=0x%llx npairs=2^%d P(dx8==0)=%.6f (uniform %.6f) advantage=%.2fx\n",
        (unsigned long long)dl, logN-1, (double)h8[0]/(double)npairs, 1/256.0,
        ((double)h8[0]/(double)npairs)/(1/256.0));
    printf("top-8 dx8 values by count (expected %.0f):\n", e);
    for(int t=0;t<8;t++){ int bi=0; for(int i=0;i<256;i++) if(h8[i]>h8[bi]) bi=i;
        printf("  0x%02x: %llu (%.2fx)\n", bi, (unsigned long long)h8[bi], (double)h8[bi]/e);
        h8[bi]=0; }
    return 0;
}
