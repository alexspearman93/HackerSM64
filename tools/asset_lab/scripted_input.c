/* Mupen64Plus input replay. CSV: first_poll,last_poll,stick_x,stick_y,buttons.
 * Does not write emulated memory; optional telemetry reads the linked Mario state.
 */
#define M64P_PLUGIN_PROTOTYPES
#include "m64p_plugin.h"
#include "m64p_common.h"
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
static unsigned poll, address;
static unsigned (*read32)(unsigned);
static FILE *logfile, *skinlog;
static unsigned skinframe, skinprobe;
static struct { unsigned first,last,buttons; int x,y; } events[256];
static int count;
m64p_error PluginStartup(m64p_dynlib_handle core, void *ctx, void (*debug)(void*,int,const char*)) {
 read32=dlsym(core,"DebugMemRead32");
 const char *v=getenv("LAB_MARIO_POINTER"); address=v?strtoul(v,0,0):0;
 FILE *f=fopen(getenv("LAB_INPUT")?getenv("LAB_INPUT"):"input.csv","r");
 if(f){while(count<256 && fscanf(f,"%u,%u,%d,%d,%u",&events[count].first,&events[count].last,&events[count].x,&events[count].y,&events[count].buttons)==5)count++; fclose(f);}
 logfile=fopen(getenv("LAB_TRACE")?getenv("LAB_TRACE"):"trace.csv","w");
 if(logfile)fprintf(logfile,"poll,x,y,z,floor,action,coins\n");
 const char *sf=getenv("LAB_SKIN_FRAME"), *sp=getenv("LAB_SKIN_PROBE"), *sl=getenv("LAB_SKIN_TRACE");
 if(sf&&sp&&sl){skinframe=strtoul(sf,0,0);skinprobe=strtoul(sp,0,0);skinlog=fopen(sl,"w");}
 return M64ERR_SUCCESS;
}
m64p_error PluginShutdown(void){if(logfile)fclose(logfile);if(skinlog)fclose(skinlog);return M64ERR_SUCCESS;}
m64p_error PluginGetVersion(m64p_plugin_type*t,int*v,int*a,const char**n,int*c){if(t)*t=M64PLUGIN_INPUT;if(v)*v=0x10000;if(a)*a=0x20100;if(n)*n="Asset Lab replay";if(c)*c=0;return M64ERR_SUCCESS;}
void InitiateControllers(CONTROL_INFO c){for(int i=0;i<4;i++){c.Controls[i].Present=i==0;c.Controls[i].RawData=0;c.Controls[i].Plugin=PLUGIN_NONE;c.Controls[i].Type=CONT_TYPE_STANDARD;}}
int RomOpen(void){poll=0;return 1;} void RomClosed(void){}
static float f32(unsigned a){union{unsigned u;float f;}v={read32(a)};return v.f;}
void GetKeys(int c,BUTTONS*k){k->Value=0;if(c)return;poll++;
 for(int i=0;i<count;i++)if(poll>=events[i].first&&poll<=events[i].last){k->Value=events[i].buttons;k->X_AXIS=events[i].x;k->Y_AXIS=events[i].y;}
 if(skinlog&&read32){fprintf(skinlog,"%u,%u",poll,read32(skinframe));for(int i=0;i<30;i++)fprintf(skinlog,",%.6f",f32(skinprobe+i*4));fprintf(skinlog,"\n");}
 if(logfile&&read32&&address){unsigned m=read32(address);if(m>=0x80000000&&m<0x80800000)fprintf(logfile,"%u,%.3f,%.3f,%.3f,%.3f,%08x,%u\n",poll,f32(m+0x3c),f32(m+0x40),f32(m+0x44),f32(m+0x70),read32(m+0xc),read32(m+0xa8)>>16);}
}
void ControllerCommand(int c,unsigned char*b){} void ReadController(int c,unsigned char*b){}
void SDL_KeyDown(int a,int b){} void SDL_KeyUp(int a,int b){} void RenderCallback(void){}
