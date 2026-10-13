/* best 1-round F differential prob (single-nibble input diffs), and
 * best 2-round Feistel trail via middle difference enumeration. */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>
static const uint8_t SB[16] = {0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10};
static uint32_t sboxL(uint32_t x){uint32_t r=0;for(int i=0;i<8;i++)r|=(uint32_t)SB[(x>>(4*i))&0xF]<<(4*i);return r;}
static uint32_t rotl32(uint32_t x,int n){return (x<<n)|(x>>(32-n));}
static uint32_t F0(uint32_t R){uint32_t t=sboxL(R);return t^rotl32(t,7)^rotl32(t,13);} /* rk=0 */
/* hashmap-lite: count top output diff for fixed input diff over N samples */
#define HSZ (1u<<20)
static uint32_t hkey[HSZ]; static uint32_t hcnt[HSZ]; static uint32_t hgen[HSZ]; static uint32_t curgen=1;
static void hreset(){curgen++; if(curgen==0){for(uint32_t i=0;i<HSZ;i++)hgen[i]=0;curgen=1;}}
static uint32_t hadd(uint32_t d){
    uint32_t h=(d*2654435761u)&(HSZ-1);
    while(hgen[h]==curgen && hkey[h]!=d) h=(h+1)&(HSZ-1);
    if(hgen[h]!=curgen){hgen[h]=curgen;hkey[h]=d;hcnt[h]=1;}
    else hcnt[h]++;
    return hcnt[h];
}
int main(void){
    const long N=1<<24; uint64_t s=0x12345;
    /* 1-round: 120 single-nibble input diffs */
    uint32_t bestd=0; long bestc=0; uint32_t bestdin=0;
    for(int nib=0;nib<8;nib++) for(int dv=1;dv<16;dv++){
        uint32_t din=(uint32_t)dv<<(4*nib);
        hreset(); long mx=0; uint32_t mxd=0;
        uint64_t ss=s;
        for(long i=0;i<N;i++){ss=ss*6364136223846793005ULL+1442695040888963407ULL;
            uint32_t R=(uint32_t)ss;
            uint32_t dd=F0(R)^F0(R^din);
            uint32_t c=hadd(dd); if(c>mx){mx=c;mxd=dd;}}
        if(mx>bestc){bestc=mx;bestd=mxd;bestdin=din;}
    }
    printf("1-round F: best din=%08x -> dout=%08x count=%ld/%ld p~2^%.2f\n",
           bestdin,bestd,bestc,N, log2((double)bestc/N));
    /* 2-round Feistel trail: input diff (0,bestdin). R1 out diff=(bestdin,d1).
       R2 in-R diff = d1; try to keep it going: measure best (d1->d2). */
    hreset(); long mx=0; uint32_t mxd=0;
    uint64_t ss=s;
    for(long i=0;i<N;i++){ss=ss*6364136223846793005ULL+1442695040888963407ULL;
        uint32_t R=(uint32_t)ss;
        uint32_t dd=F0(R)^F0(R^bestd);
        uint32_t c=hadd(dd); if(c>mx){mx=c;mxd=dd;}}
    printf("2nd-round F: best din=%08x -> dout=%08x count=%ld/%ld p~2^%.2f\n",
           bestd,mxd,mx,N, log2((double)mx/N));
    printf("2-round trail prob ~ 2^%.2f\n", log2((double)bestc/N)+log2((double)mx/N));
    return 0;
}
