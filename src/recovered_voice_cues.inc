static void do_paku( int index, int value )
{
    PAKU *chara;

    chara = &chara_work[ index ];
    if ( value == 4 )
    {
        chara->eye = 1;
    }
    else if ( value < 4 )
    {
        chara->mouth = value;
    }
}
static void set_id( int index, int id )
{
    PAKU *chara;

    chara = &chara_work[ 1 ];
    chara[ --index ].id = id;
}
static void do_motion( int a, int b )
{
    /* do nothing */
}
static inline void jimctrl_act_helper2_80038070(Work *work, int str_counter)
{
    int value;

    while (work->field_30 < str_counter)
    {
        work->field_30++;
        work->field_40--;

        while (work->field_40 < 1)
        {
            value = *work->field_38++;

            if (value & 0x80)
            {
                do_paku(work->field_3C, (value >> 4) & 0x7);
                work->field_40 = value & 0xF;
            }
            else
            {
                switch (value >> 4)
                {
                case 0:
                    printf("KUTIPAKU END\n");
                    do_paku(work->field_3C, 0);
                    work->field_38 = NULL;
                    return;

                case 1:
                    do_paku(work->field_3C, value & 0xF);
                    work->field_40 = *work->field_38++;
                    break;

                case 2:
                    set_id(value & 0xF, (work->field_38[0] << 8) | work->field_38[1]);
                    work->field_38 += 2;
                    break;

                case 4:
                    work->field_3C = value & 0xF;
                    break;

                case 5:
                    do_paku(work->field_3C, value & 0xF);
                    work->field_40 = (work->field_38[0] << 8) | work->field_38[1];
                    work->field_38 += 2;
                    break;

                case 6:
                    work->field_40 = *work->field_38++;
                    do_motion((work->field_38[0] << 8) | work->field_38[1], (work->field_38[2] << 8) | work->field_38[3]);
                    break;
                }
            }
        }
    }
}
unsigned int jimctrl_helper_80037F68(unsigned int header)
{
    u_short                  field_2_preClear;
    PAKU *pIter;
    u_char                 *pField;
    int                   i;

    pIter = &chara_work[1];
    i = 0;
    pField = &pIter->eye;
    for (; i < PAKU_MAX - 1; i++)
    {
        if (pIter->id == header)
        {
            field_2_preClear = *pField;
            *pField = 0;
            return (field_2_preClear << 8 | *++pField);
        }
        pField += sizeof(PAKU);
        pIter++;
    }

    return 0;
}