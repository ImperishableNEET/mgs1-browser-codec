void sub_8003FD50(MenuPrim *pMenuPrim, int xoff, int yoff, int param_4, RadioUnknown *pRadioUnknown, int abe)
{
    int          bit;
    int          iVar1;
    int          i;
    unsigned int color;
    LINE_F4     *pLine;
    char        *pCoords;
    int          iVar2;

    bit = 1;
    iVar1 = gDigit7Segment_8009E60C[param_4];

    for (i = 0; i < 7; i++, bit <<= 1)
    {
        if (iVar1 & bit)
        {
            color = pRadioUnknown->color1;
        }
        else
        {
            color = pRadioUnknown->color2;

            if (color == 0)
            {
                continue;
            }
        }

        _NEW_PRIM(pLine, pMenuPrim);
        LSTORE(color, &pLine->r0);

        pCoords = pRadioUnknown->coords[i];
        pLine->x0 = pCoords[0] + xoff;
        pLine->y0 = pCoords[1] + yoff;

        iVar2 = dword_800AB610[i];

        if (iVar2 < 3)
        {
            pLine->x1 = pLine->x0 + pCoords[2] - 1;
            pLine->y1 = pLine->y0;
            pLine->x2 = pLine->x1;
            pLine->y2 = pLine->y0 + pCoords[3] - 1;
            pLine->x3 = pLine->x0;
            pLine->y3 = pLine->y2;

            if (iVar2 == 1)
            {
                pLine->x0++;
                pLine->x1--;
            }
            else
            {
                pLine->x2--;
                pLine->x3++;
            }
        }
        else
        {
            pLine->x1 = pLine->x0;
            pLine->y1 = pLine->y0 + pCoords[3] - 1;
            pLine->x2 = pLine->x1 + pCoords[2] - 1;
            pLine->y2 = pLine->y1;
            pLine->x3 = pLine->x2;
            pLine->y3 = pLine->y0;

            if (iVar2 == 3)
            {
                pLine->y0++;
                pLine->y1--;
            }
            else
            {
                pLine->y2--;
                pLine->y3++;
            }
        }

        setLineF4(pLine);
        setSemiTrans(pLine, abe);
        addPrim(pMenuPrim->ot, pLine);
    }
}
void sub_8003FFB0(MenuPrim *pGlue, int x0, int y0, int rgb)
{
    TILE *pPrim;

    _NEW_PRIM(pPrim, pGlue);

    pPrim->w = 2;
    pPrim->h = 2;
    LSTORE(rgb, &pPrim->r0);
    pPrim->x0 = x0 + 11;
    pPrim->y0 = y0 + 15;

    setTile(pPrim);
    addPrim(pGlue->ot, pPrim);
}
void menu_radio_codec_helper_helper14_helper_80040034(MenuPrim *pGlue, int x, int y, int param_4)
{
    int           color;
    int           idx;
    int           count;
    RadioUnknown *pRadioUnknown;

    color = 0x3D472E;

    pRadioUnknown = &dword_8009E63C;
    pRadioUnknown->color1 = color;
    pRadioUnknown->color2 = 0;

    idx = 0;
    count = 10000;

    while (count > 0)
    {
        sub_8003FD50(pGlue, x, y, (param_4 / count) % 10, pRadioUnknown, 0);

        if (count == 100)
        {
            sub_8003FFB0(pGlue, x, y, color);
        }
        else if (count == 1000)
        {
            pRadioUnknown = &dword_8009E618;
            pRadioUnknown->color1 = color;
            pRadioUnknown->color2 = 0;
            y -= 2;
        }

        count /= 10;
        x += dword_8009E660[idx++];
    }
}
void menu_radio_codec_helper_helper14_helper5_800402A0(MenuPrim *pGlue, int xoff, int yoff, int param_4)
{
    int   color, color2;
    int   i;
    TILE *pTile;
    int   width;

    color2 = (param_4 < 0) ? 0x3D472E : 0;
    param_4 *= 5;

    for (i = 1; i < 44; i++)
    {
        if ((i % 5) == 0)
        {
            continue;
        }

        if (param_4 > (44 - i))
        {
            color = 0x3D472E;
        }
        else
        {
            color = color2;

            if (color == 0)
            {
                continue;
            }
        }

        _NEW_PRIM(pTile, pGlue);

        pTile->x0 = xoff;
        pTile->y0 = yoff + i;

        width = 300;
        width /= i;
        width += 3;

        if (width > 76)
        {
            width = 76;
        }

        pTile->w = width;
        pTile->h = 1;
        LSTORE(color, &pTile->r0);

        setTile(pTile);
        addPrim(pGlue->ot, pTile);
    }
}