/* Extracted radio.c case-5 update; isolated random inputs. */
static int dword_800ABAF8=0,dword_800AB644=-1,meter_values[2],meter_index;
static int meter_random(void){return meter_values[meter_index++];}
void meter_reset(void){dword_800ABAF8=0;dword_800AB644=-1;}
int meter_step(int GV_Time,int r1,int r2){meter_values[0]=r1;meter_values[1]=r2;meter_index=0;
        if (!(GV_Time & 3))
        {
            if (meter_random() % 4 <= 0)
            {
                if (dword_800ABAF8 < 7)
                {
                    dword_800AB644 = 1;
                }
            }
            else
            {
                if (dword_800ABAF8 >= 7)
                {
                    dword_800AB644 = -1;
                }
            }
            if (!(meter_random() & 7))
            {
                dword_800AB644 = -dword_800AB644;
            }
            dword_800ABAF8 += dword_800AB644;
            if (dword_800ABAF8 >= 0xA)
            {
                dword_800ABAF8 = 9;
            }
            else if (dword_800ABAF8 < 6)
            {
                dword_800ABAF8 = 6;
            }
        }
return dword_800ABAF8;}
int meter_draw(int value){current.used=0;menu_radio_codec_helper_helper14_helper5_800402A0(&current,32,149,value);return current.used;}
