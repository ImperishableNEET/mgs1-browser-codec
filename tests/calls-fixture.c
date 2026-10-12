#define main original_frame_main
#include "../src/codec_calls.c"
#undef main
#undef printf
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char**argv){
 if(argc!=5)return 2;
 FILE*f=fopen(argv[1],"rb");if(!f)return 3;
 unsigned char d[65536];int n=(int)fread(d,1,sizeof(d),f);fclose(f);
 for(int i=0;i<n;i++)voice_byte(i,d[i]);
 int start=atoi(argv[2]),stop=atoi(argv[3]),id=atoi(argv[4]);voice_begin(start);
 for(int t=start;t<=stop;t++){voice_tick(t);unsigned short v=(unsigned short)voice_pose(id);fwrite(&v,2,1,stdout);}
 return 0;
}
