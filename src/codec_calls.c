typedef unsigned char uint8_t; typedef short int16_t; typedef unsigned short uint16_t; typedef unsigned int uint32_t;
typedef struct {uint8_t r0,g0,b0,code;int16_t x0,y0,x1,y1,x2,y2,x3,y3;uint8_t u0,v0,u1,v1,u2,v2,u3,v3;uint16_t clut,tpage; int w,h;} POLY_FT4;
typedef struct {POLY_FT4 prims[256];int used;void *ot;} MenuPrim;
static POLY_FT4 *new_prim(MenuPrim*p){return &p->prims[p->used++];}
#define _NEW_PRIM(v,p) ((v)=new_prim(p))
#define LSTORE(v,p) do { uint32_t z=(v); unsigned char *b=(unsigned char *)(p); b[0]=z; b[1]=z>>8; b[2]=z>>16; b[3]=z>>24; } while(0)
#define setPolyFT4(p) ((p)->code=0x2c)
#define setSemiTrans(p,b) ((p)->code|=((b)?2:0))
#define addPrim(ot,p) ((void)0)
#define getTPage(d,a,x,y) (((d)<<7)|((a)<<5)|(((y)&256)>>4)|((x)>>6))
#define setUVWH(p,u,v,w,h) do{(p)->u0=(p)->u2=(u);(p)->u1=(p)->u3=(u)+(w);(p)->v0=(p)->v1=(v);(p)->v2=(p)->v3=(v)+(h);}while(0)
#define setXYWH(p,x,y,w,h) do{(p)->x0=(p)->x2=(x);(p)->x1=(p)->x3=(x)+(w);(p)->y0=(p)->y1=(y);(p)->y2=(p)->y3=(y)+(h);}while(0)
int dword_800ABB3C;
#include "recovered_frame.inc"

static MenuPrim current;
int frame_generate(int x,int y,int w,int h){current.used=0;radio_draw_face_frame(&current,x,y,w,h);return current.used;}
int frame_word(int i,int field){if(i<0||i>=current.used)return -999;POLY_FT4*p=&current.prims[i];switch(field){
case 0:return p->x0;case 1:return p->y0;case 2:return p->x3;case 3:return p->y3;
case 4:return p->u0;case 5:return p->v0;case 6:return p->u3;case 7:return p->v3;
case 8:return p->code;case 9:return p->clut;case 10:return p->tpage;case 11:return p->r0;default:return -999;}}
#ifndef __wasm__
#include <stdio.h>
int main(void){for(int side=0;side<2;side++)for(int w=6;w<=52;w+=46)for(int h=7;h<=89;h++){int n=frame_generate(side?237:31,30+(89-h)/2,w,h);printf("%d",n);for(int i=0;i<n;i++)for(int f=0;f<12;f++)printf(",%d",frame_word(i,f));puts("");}return 0;}
#endif

typedef struct {int id;} face_anim_image;
typedef struct {face_anim_image *field_4_face;face_anim_image *field_8_eyes[3];face_anim_image *field_14_mouth[3];} face_simple_anim;
typedef struct {int field_0_animState,field_E_eyesAnimFrame,field_4C_mouthAnimFrame;struct {face_simple_anim*simple_anim;} field_14_face_anim;} menu_chara_struct_sub;
static int layers[3],layer_count;static face_anim_image imgs[7]={{0},{1},{2},{3},{4},{5},{6}};
void LoadFaceAnimImage_80046B10(face_anim_image*im,int idx){(void)idx;if(im)layers[layer_count++]=im->id;}
#define NULL ((void*)0)
#include "recovered_animation.inc"
static menu_chara_struct_sub states[2];static face_simple_anim animations[2];
int anim_step(int side,int blink,int mouth){if(side<0||side>1||mouth<0||mouth>3)return -1;face_simple_anim*a=&animations[side];a->field_4_face=&imgs[0];for(int i=0;i<3;i++){a->field_8_eyes[i]=i<2?&imgs[i+1]:NULL;a->field_14_mouth[i]=i<2?&imgs[i+3]:NULL;}menu_chara_struct_sub*s=&states[side];s->field_0_animState=1;s->field_14_face_anim.simple_anim=a;if(blink)s->field_E_eyesAnimFrame=1;s->field_4C_mouthAnimFrame=mouth;layer_count=0;menu_radio_draw_face_helper2_800486F4(s,side);return layer_count;}
int anim_layer(int i){return i>=0&&i<layer_count?layers[i]:-1;}

typedef POLY_FT4 LINE_F4;typedef POLY_FT4 TILE;
typedef struct {char coords[7][4];unsigned int color1,color2;} RadioUnknown;
#define setLineF4(p) ((p)->code=0x48)
#define setTile(p) ((p)->code=0x60)
char gDigit7Segment_8009E60C[]={0x77,0x24,0x5d,0x6d,0x2e,0x6b,0x7b,0x25,0x7f,0x6f,0,0};
char dword_800AB610[]={2,4,3,1,4,3,1,0};
char dword_8009E660[]={10,10,15,12,0};
RadioUnknown dword_8009E618={{{1,0,7,2},{0,1,2,7},{7,1,2,7},{1,7,7,2},{0,9,2,7},{7,9,2,7},{1,15,7,2}},0x3d472e,0};
RadioUnknown dword_8009E63C={{{1,0,5,2},{0,1,2,6},{5,1,2,6},{1,6,5,2},{0,8,2,6},{5,8,2,6},{1,13,5,2}},0x3d472e,0};
#include "recovered_panel.inc"
int panel_generate(int frequency){current.used=0;menu_radio_codec_helper_helper14_helper_80040034(&current,141,80,frequency);menu_radio_codec_helper_helper14_helper5_800402A0(&current,122,51,-1);return current.used;}
int panel_word(int i,int f){POLY_FT4*p=&current.prims[i];switch(f){case 0:return p->code;case 1:return p->x0;case 2:return p->y0;case 3:return p->x1;case 4:return p->y1;case 5:return p->x2;case 6:return p->y2;case 7:return p->x3;case 8:return p->y3;case 9:return p->w;case 10:return p->h;case 11:return p->r0|p->g0<<8|p->b0<<16;}return -1;}

int panel_active(int frequency,int meter){current.used=0;menu_radio_codec_helper_helper14_helper_80040034(&current,141,80,frequency);menu_radio_codec_helper_helper14_helper5_800402A0(&current,122,51,meter);return current.used;}

typedef unsigned short u_short;typedef unsigned char u_char;
#define PAKU_MAX 7
#define printf(...) ((void)0)
typedef struct {unsigned short id;unsigned char eye,mouth;} PAKU;
static PAKU chara_work[7];
typedef struct {int field_30,field_40,field_3C;char*field_38;} Work;
static Work cue_work;static char cue_bytes[65536];
#include "recovered_voice_cues.inc"
void voice_byte(int index,int value){if(index>=0&&index<65536)cue_bytes[index]=(char)value;}
void voice_reset(void){for(int i=0;i<7;i++){chara_work[i].id=0;chara_work[i].eye=0;chara_work[i].mouth=0;}cue_work.field_30=0;cue_work.field_40=0;cue_work.field_3C=0;cue_work.field_38=cue_bytes;}
void voice_tick(int counter){if(cue_work.field_38&&counter>=0&&counter<100000)jimctrl_act_helper2_80038070(&cue_work,counter);}
int voice_pose(int id){return jimctrl_helper_80037F68(id);}

void voice_begin(int start){voice_reset();cue_work.field_30=start;}
void anim_reset(void){for(int s=0;s<2;s++){states[s].field_E_eyesAnimFrame=0;states[s].field_4C_mouthAnimFrame=0;}}

#include "recovered_meter.inc"
