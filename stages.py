import pygame

from config import WIDTH
from entities import Player, KeyObj, Door


PLATFORMS_BY_STAGE = {
    1: [
        pygame.Rect(0, 580, WIDTH, 60),
        pygame.Rect(180, 460, 220, 20),
        pygame.Rect(520, 380, 240, 20),
    ],
    2: [
        pygame.Rect(0, 580, WIDTH, 60),
        pygame.Rect(120, 480, 180, 20),
        pygame.Rect(420, 420, 160, 20),
        pygame.Rect(680, 320, 160, 20),
    ],
}


def get_platforms_for_stage(stage):
    return PLATFORMS_BY_STAGE.get(stage, PLATFORMS_BY_STAGE[1])


def create_stage_objects(stage):
    platforms = get_platforms_for_stage(stage)
    player = Player(100, 320)
    key_obj = KeyObj(520, 340)
    door_obj = Door(820, 240)
    return player, key_obj, door_obj, platforms

