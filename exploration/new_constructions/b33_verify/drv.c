#include <stdio.h>
#include <stdint.h>
uint64_t mix_hash(uint64_t,uint64_t);
int main(void){uint64_t v,k;while(scanf("%llx %llx",(unsigned long long*)&v,(unsigned long long*)&k)==2)printf("%016llx\n",(unsigned long long)mix_hash(v,k));return 0;}
