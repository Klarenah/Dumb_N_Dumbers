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


def create_stage_objects(stage, player_colors=None):
    platforms = get_platforms_for_stage(stage)
    # 기본 색상
    default_colors = [(30, 120, 255), (255, 80, 80), (80, 255, 80)]
    if player_colors is None:
        player_colors = default_colors
    
    # 플레이어 1: 방향키, 상호작용: DOWN
    player1 = Player(100, 320, color=player_colors[0], 
                     key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_up=pygame.K_UP,
                     key_interact=pygame.K_DOWN)
    # 플레이어 2: WASD, 상호작용: S
    player2 = Player(150, 320, color=player_colors[1] if len(player_colors) > 1 else default_colors[1],
                     key_left=pygame.K_a, key_right=pygame.K_d, key_up=pygame.K_w,
                     key_interact=pygame.K_s)
    # 플레이어 3: IJKL, 상호작용: K
    player3 = Player(200, 320, color=player_colors[2] if len(player_colors) > 2 else default_colors[2],
                     key_left=pygame.K_j, key_right=pygame.K_l, key_up=pygame.K_i,
                     key_interact=pygame.K_k)
    players = [player1, player2, player3]
    key_obj = KeyObj(520, 340)
    door_obj = Door(820, 240)
    return players, key_obj, door_obj, platforms


