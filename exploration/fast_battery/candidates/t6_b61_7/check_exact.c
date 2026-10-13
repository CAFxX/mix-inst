#include <stdio.h>
#include <stdint.h>
#include "impl.c"
int main(void){uint64_t s=0x123456789abcdefULL;
for(int i=0;i<2000;i++){s=s*6364136223846793005ULL+1442695040888963407ULL;
uint64_t v=s;s=s*6364136223846793005ULL+1442695040888963407ULL;uint64_t k=s;
printf("%llx %llx %llx\n",(unsigned long long)v,(unsigned long long)k,
       (unsigned long long)mix_hash(v,k));}return 0;}
