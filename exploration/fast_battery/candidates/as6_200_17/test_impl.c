#include <stdio.h>
#include <stdint.h>
uint64_t mix_hash(uint64_t,uint64_t);
int main(){uint64_t vs[4]={0,1,0x123456789ABCDEF0ULL,0xFFFFFFFFFFFFFFFFULL};
uint64_t ks[2]={0x123456789ABCDEF0ULL,0};
for(int i=0;i<4;i++)for(int j=0;j<2;j++)printf("%llx\n",(unsigned long long)mix_hash(vs[i],ks[j]));return 0;}
