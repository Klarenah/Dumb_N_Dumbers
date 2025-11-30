import pygame

from config import WIDTH, HEIGHT
from entities import Player, KeyObj, Door, MovingPlatform, SyncedPlayer, Spike, FloorButton


PLATFORMS_BY_STAGE = {
    1: [
        pygame.Rect(0, 580, WIDTH, 60),  # 바닥
        pygame.Rect(180, 460, 220, 20),
        pygame.Rect(520, 380, 240, 20),
    ],
    2: [
        pygame.Rect(0, 580, WIDTH, 60),  # 바닥
    ],
    3: [
        pygame.Rect(0, 580, 400, 60),  # 왼쪽 바닥
        pygame.Rect(640, 580, 400, 60),  # 오른쪽 바닥 (중간 뚫림)
    ],
    4: [
        pygame.Rect(0, 580, 200, 60),  # 왼쪽 아래 바닥
        pygame.Rect(760, 200, 200, 60),  # 오른쪽 위 바닥
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
    
    # 스테이지별 설정
    if stage == 4:
        # 4스테이지: 동기화된 플레이어 1개만
        synced_player = SyncedPlayer(100, 520, color=player_colors[0])
        players = [synced_player]
        # 왼쪽 아래 바닥 위에 열쇠
        key_obj = KeyObj(50, 550)
        # 오른쪽 위 바닥 위에 문
        door_obj = Door(800, 44)
        # 움직이는 발판 3개
        # 플레이어 점프 높이 계산 (vel_y = -13, 중력 0.6)
        jump_height = 13 * 13 / (2 * 0.6)  # 약 140픽셀
        floor_y = 580
        top_floor_y = 200
        
        # 첫번째 발판: 왼쪽 아래 바닥까지 내려왔다가 점프 높이만큼 올라감
        platform1_min_y = floor_y - 20  # 바닥 위 20픽셀 (아래쪽 한계)
        platform1_max_y = platform1_min_y - jump_height  # 위쪽 한계
        platform1 = MovingPlatform(250, platform1_min_y, 80, 20, platform1_min_y, platform1_max_y, speed=1)
        
        # 두번째 발판: 첫번째 발판의 최대 높이까지 내려갔다가 점프 높이만큼 올라감
        platform2_min_y = platform1_max_y - 20  # 아래쪽 한계
        platform2_max_y = platform2_min_y - jump_height  # 위쪽 한계
        platform2 = MovingPlatform(400, platform2_min_y, 80, 20, platform2_min_y, platform2_max_y, speed=2)
        
        # 세번째 발판: 두번째 발판의 최대 높이까지 내려갔다가 오른쪽 위 바닥까지 올라감
        platform3_min_y = platform2_max_y - 20  # 아래쪽 한계
        platform3_max_y = top_floor_y - 20  # 위쪽 한계
        platform3 = MovingPlatform(550, platform3_min_y, 80, 20, platform3_min_y, platform3_max_y, speed=1)
        
        moving_platforms = [platform1, platform2, platform3]
        # 가장 아래에 가시 배치 (왼쪽 바닥과 오른쪽 바닥 사이)
        bottom_spike = Spike(200, HEIGHT - 20, 560)  # x=200부터 560픽셀 너비 (200~760)
        return players, key_obj, door_obj, platforms, moving_platforms, bottom_spike
    
    # 스테이지별 플레이어 시작 위치 설정
    if stage == 2:
        # 스테이지 2: 가운데에서 시작, 바닥 위
        center_x = WIDTH // 2
        player1_x = center_x - 50
        player2_x = center_x
        player3_x = center_x + 50
        player_y = 524  # 바닥 높이 580 - 플레이어 높이 56
    elif stage == 3:
        # 스테이지 3: 왼쪽 바닥 위에서 시작
        player1_x = 100
        player2_x = 150
        player3_x = 200
        player_y = 524  # 왼쪽 바닥 높이 580 - 플레이어 높이 56
    else:
        # 다른 스테이지: 왼쪽에서 시작
        player1_x = 100
        player2_x = 150
        player3_x = 200
        player_y = 320
    
    # 플레이어 1: 방향키, 상호작용: DOWN
    player1 = Player(player1_x, player_y, color=player_colors[0], 
                     key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_up=pygame.K_UP,
                     key_interact=pygame.K_DOWN)
    # 플레이어 2: WASD, 상호작용: S
    player2 = Player(player2_x, player_y, color=player_colors[1] if len(player_colors) > 1 else default_colors[1],
                     key_left=pygame.K_a, key_right=pygame.K_d, key_up=pygame.K_w,
                     key_interact=pygame.K_s)
    # 플레이어 3: IJKL, 상호작용: K
    player3 = Player(player3_x, player_y, color=player_colors[2] if len(player_colors) > 2 else default_colors[2],
                     key_left=pygame.K_j, key_right=pygame.K_l, key_up=pygame.K_i,
                     key_interact=pygame.K_k)
    players = [player1, player2, player3]
    
    # 스테이지별 오브젝트 설정
    if stage == 2:
        # 스테이지 2: 문이 오른쪽 바닥 위, 열쇠는 왼쪽 위
        key_obj = KeyObj(50, 300)  # 왼쪽 위
        door_obj = Door(900, 480)  # 오른쪽 바닥 위
    elif stage == 3:
        # 스테이지 3: 바닥 중간이 뚫려있고 가시와 버튼이 있음
        key_obj = KeyObj(50, 550)  # 왼쪽 바닥 위
        door_obj = Door(900, 480)  # 오른쪽 바닥 위
        # 가시: 뚫려있는 곳 (400~560 사이)
        spike = Spike(400, 580, 260)  # x=400부터 160픽셀 너비
        # 버튼: 오른쪽 바닥 위에 배치
        floor_button = FloorButton(600, 550)
        return players, key_obj, door_obj, platforms, [], spike, floor_button
    else:
        # 스테이지 1: 기본 설정
        key_obj = KeyObj(520, 340)
        door_obj = Door(820, 240)
    
    return players, key_obj, door_obj, platforms, []


