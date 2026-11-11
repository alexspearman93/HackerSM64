// flame.inc.c

void bhv_moving_flame_loop(void) {
    if (GET_BPARAM2(o->oBehParams) == MOVING_FLAME_BP_1FRAME) {
        if (o->oTimer > 0) {
            obj_mark_for_deletion(o);
        } else {
            f32 rnd = random_float() - 0.5f;

            o->header.gfx.scale[1] = o->header.gfx.scale[2] * (1.0f + 0.7f * rnd);
            o->header.gfx.scale[0] = o->header.gfx.scale[2] * (0.9f - 0.5f * rnd);

            o->oAnimState = random_u16();
        }
    } else {
        cur_obj_update_floor_and_walls();

        if (approach_f32_ptr(&o->oSmallPiranhaFlameStartSpeed, o->oSmallPiranhaFlameEndSpeed, 0.6f)) {
            cur_obj_rotate_yaw_toward(o->oAngleToMario, 0x200);
        }

        obj_compute_vel_from_move_pitch(o->oSmallPiranhaFlameStartSpeed);
        cur_obj_move_standard(-78);
        spawn_object_with_scale(o, o->oSmallPiranhaFlameModel, bhvMovingFlame,
                                0.4f * o->header.gfx.scale[0]);

        if (o->oTimer > o->oSmallPiranhaFlameNextFlameTimer) {
            spawn_object_relative_with_scale(1, 0, o->oGraphYOffset, 0, o->header.gfx.scale[0], o,
                                             o->oSmallPiranhaFlameModel, bhvMovingFlameEmber);
            o->oSmallPiranhaFlameNextFlameTimer = random_linear_offset(8, 15);
            o->oTimer = 0;
        }

        obj_check_attacks(&sPiranhaPlantFireHitbox, o->oAction);
        o->oSmallPiranhaFlameSpeed += o->oSmallPiranhaFlameStartSpeed;

        if (o->oSmallPiranhaFlameSpeed > 1500.0f
            || (o->oMoveFlags & (OBJ_MOVE_HIT_WALL | OBJ_MOVE_MASK_IN_WATER))) {
            obj_die_if_health_non_positive();
        }
    }

    o->oGraphYOffset = 15.0f * o->header.gfx.scale[1];
}

void bhv_moving_flame_particle_loop(void) {
    cur_obj_move_using_fvel_and_gravity();

    if (approach_f32_ptr(&o->header.gfx.scale[0], 0.0f, 0.6f)) {
        obj_mark_for_deletion(o);
    }

    cur_obj_scale(o->header.gfx.scale[0]);
}

/* Mario's pistol projectile. Reuses the verified destructive collision behavior. */
static struct ObjectHitbox sMarioFireballHitbox = {
    /* interactType:      */ INTERACT_NONE,
    /* downOffset:        */ 0,
    /* damageOrCoinValue: */ 1,
    /* health:            */ 0,
    /* numLootCoins:      */ 0,
    /* radius:            */ 45,
    /* height:            */ 90,
    /* hurtboxRadius:     */ 45,
    /* hurtboxHeight:     */ 90,
};

void bhv_mario_fireball_init(void) {
    obj_set_hitbox(o, &sMarioFireballHitbox);
    cur_obj_scale(2.5f);
    o->oGravity = 0.0f;
    o->oBuoyancy = 0.0f;
}

void bhv_mario_fireball_loop(void) {
    s32 i;
    struct Object *target;
    f32 dx, dy, dz;

    if (o->oTimer > 28) {
        obj_mark_for_deletion(o);
        return;
    }

    /* Keep the first rendered bullet at the muzzle for one update. */
    if (o->oTimer == 0) return;
    o->oPosX += sins(o->oMoveAngleYaw) * o->oForwardVel;
    o->oPosZ += coss(o->oMoveAngleYaw) * o->oForwardVel;

    for (i = 0; i < o->numCollidedObjs; i++) {
        target = o->collidedObjs[i];
        if (target == NULL || target == gMarioObject || target == o
            || target->oInteractType == INTERACT_NONE
            || target->oInteractType == INTERACT_COIN
            || target->oInteractType == INTERACT_STAR_OR_KEY) {
            continue;
        }
        target->oInteractStatus |= INT_STATUS_INTERACTED | INT_STATUS_WAS_ATTACKED | INT_KICK;
        obj_mark_for_deletion(o);
        return;
    }

    if (o->oPosY < find_floor_height(o->oPosX, o->oPosY + 100.0f, o->oPosZ)) {
        obj_mark_for_deletion(o);
        return;
    }
    dx = o->oPosX - gMarioObject->oPosX;
    dy = o->oPosY - gMarioObject->oPosY;
    dz = o->oPosZ - gMarioObject->oPosZ;
    if (dx * dx + dy * dy + dz * dz > 6250000.0f) {
        obj_mark_for_deletion(o);
    }
}
