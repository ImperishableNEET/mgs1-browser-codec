void menu_radio_draw_face_helper2_800486F4(menu_chara_struct_sub *pSub, int idx)
{
    face_anim_image *mouth_image;
    face_anim_image *eyes_image;
    mouth_image = eyes_image = NULL;
    if (pSub->field_0_animState == 1)
    {
        // if the eyes animation is not idle
        if (pSub->field_E_eyesAnimFrame > 0)
        {
            eyes_image = pSub->field_14_face_anim.simple_anim->field_8_eyes[(pSub->field_E_eyesAnimFrame + 1) / 2 - 1];
            pSub->field_E_eyesAnimFrame++;
            // Reset the eyes frame to 0 after 6 blinking frames
            if (pSub->field_E_eyesAnimFrame > 6)
            {
                pSub->field_E_eyesAnimFrame = 0;
            }
        }

        // if the mouth animation is not idle
        if (pSub->field_4C_mouthAnimFrame > 0)
        {
            mouth_image = pSub->field_14_face_anim.simple_anim->field_14_mouth[pSub->field_4C_mouthAnimFrame - 1];
        }
        // Draw the base codec portrait
        LoadFaceAnimImage_80046B10(pSub->field_14_face_anim.simple_anim->field_4_face, idx);
        if (mouth_image)
        {
            LoadFaceAnimImage_80046B10(mouth_image, idx);
        }
        if (eyes_image)
        {
            LoadFaceAnimImage_80046B10(eyes_image, idx);
        }
    }
}