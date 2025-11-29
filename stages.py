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
    # 플레이어 1: 방향키 (파란색), 상호작용: DOWN
    player1 = Player(100, 320, color=(30, 120, 255), 
                     key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_up=pygame.K_UP,
                     key_interact=pygame.K_DOWN)
    # 플레이어 2: WASD (빨간색), 상호작용: S
    player2 = Player(150, 320, color=(255, 80, 80),
                     key_left=pygame.K_a, key_right=pygame.K_d, key_up=pygame.K_w,
                     key_interact=pygame.K_s)
    # 플레이어 3: IJKL (초록색), 상호작용: K
    player3 = Player(200, 320, color=(80, 255, 80),
                     key_left=pygame.K_j, key_right=pygame.K_l, key_up=pygame.K_i,
                     key_interact=pygame.K_k)
    players = [player1, player2, player3]
    key_obj = KeyObj(520, 340)
    door_obj = Door(820, 240)
    return players, key_obj, door_obj, platforms


