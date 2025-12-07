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
        pygame.Rect(620, 580, 400, 60),  # 오른쪽 바닥 (중간 뚫림)
    ],
    4: [
        pygame.Rect(0, 580, 200, 60),  # 왼쪽 아래 바닥
        pygame.Rect(760, 200, 200, 60),  # 오른쪽 위 바닥
    ],
    5: [
        pygame.Rect(0, 600, WIDTH, 40),  # 왼쪽 아래 바닥
        pygame.Rect(0, 400, 800, 30),  # 오른쪽 위 바닥
        pygame.Rect(160, 200, 300, 30),  # 중간 뚫림
        pygame.Rect(680, 200, 300, 30)
    ],
    6: [
        pygame.Rect(0, 600, WIDTH, 60),  # 바닥
        pygame.Rect(160, 200, 30, 30),
        pygame.Rect(300, 280, 30, 30),  # 오른쪽 위 바닥
        pygame.Rect(440, 360, 30, 30),  # 중간 뚫림
        pygame.Rect(580, 440, 30, 30),
        pygame.Rect(720, 520, 30, 30),# 오른쪽 위 바닥
        pygame.Rect(300, 120, 300, 30),
        pygame.Rect(800, 120, 300, 30)
        
    ]
}


def get_platforms_for_stage(stage):
    return PLATFORMS_BY_STAGE.get(stage, PLATFORMS_BY_STAGE[1])



def create_stage_objects(stage, player_colors=None, player_count=2):
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
        bottom_spike = Spike(200, HEIGHT - 20, 760)  # x=200부터 560픽셀 너비 (200~760)
        return players, key_obj, door_obj, platforms, moving_platforms, bottom_spike
    
    elif stage == 6:
        # 6스테이지: 동기화된 플레이어 1개만 (4스테이지와 동일)
        synced_player = SyncedPlayer(100, 520, color=player_colors[0])
        players = [synced_player]
        # 열쇠와 문 위치 설정 (플랫폼 구조에 맞게)
        key_obj = KeyObj(50, 550)  # 왼쪽 아래
        door_obj = Door(900, 44)  # 오른쪽 위
        
        # 바닥에 5개의 가시를 x위치 160 간격으로 배치
        # x 위치: 0, 160, 320, 480, 640 (각 160 간격)
        # 바닥 y=600이므로 가시는 y=580에 배치
        spike_width = 40  # 각 가시의 너비
        floor_spikes = []
        for i in range(5):
            spike_x = i * 160
            spike = Spike(spike_x, 580, spike_width)
            floor_spikes.append(spike)
        
        # 가시들을 하나의 리스트로 관리 (충돌 체크용)
        # 모든 가시를 하나의 Spike 객체로 합치거나, 리스트로 관리
        # 간단하게 첫 번째 가시를 대표로 사용하고, 충돌 체크는 모든 가시에 대해 수행
        return players, key_obj, door_obj, platforms, [], floor_spikes
    
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
    elif stage == 5:
        player1_x = 50
        player2_x = 100
        player3_x = 150
        player_y = 580
    else:
        # 다른 스테이지: 왼쪽에서 시작
        player1_x = 20
        player2_x = 70
        player3_x = 120
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
        # 3명의 플레이어를 선택하면 열쇠의 y좌표가 200 더 위에 있도록
        key_y = 300 if player_count < 3 else 100  # 3명일 때 y=100 (300-200)
        key_obj = KeyObj(50, key_y)  # 왼쪽 위
        door_obj = Door(900, 480)  # 오른쪽 바닥 위
    elif stage == 3:
        # 스테이지 3: 바닥 중간이 뚫려있고 가시와 버튼이 있음
        key_obj = KeyObj(50, 550)  # 왼쪽 바닥 위
        door_obj = Door(900, 480)  # 오른쪽 바닥 위
        # 가시: 뚫려있는 곳 (400~560 사이)
        spike = Spike(400, 580, 220)  # x=400부터 220픽셀 너비
        # 버튼: 오른쪽 바닥 위에 배치
        floor_button = FloorButton(620, 550)
        return players, key_obj, door_obj, platforms, [], spike, floor_button
    elif stage == 5:
        key_obj = KeyObj(750, 180)
        door_obj = Door(320, 100)
        
        # 오른쪽 아래 움직이는 발판: 오른쪽 아래쪽에서 위아래로 움직임
        # y=500 (아래쪽 한계) ~ y=400 (위쪽 한계)
        right_bottom_platform = MovingPlatform(840, 500, 80, 20, 500, 400, speed=1)
        
        # 왼쪽 위 움직이는 발판: 왼쪽 위쪽에서 위아래로 움직임
        # y=200 (아래쪽 한계) ~ y=100 (위쪽 한계)
        left_top_platform = MovingPlatform(50, 400, 80, 20, 400, 200, speed=1)
        
        moving_platforms = [right_bottom_platform, left_top_platform]
        
        # 문 왼쪽에 가시 추가 (문 x=320, 문 왼쪽에 배치)
        door_spike = Spike(270, 185, 50)  # 문 왼쪽에 50픽셀 너비의 가시
        
        return players, key_obj, door_obj, platforms, moving_platforms, door_spike

    else:
        # 스테이지 1: 기본 설정
        key_obj = KeyObj(520, 340)
        door_obj = Door(820, 240)
    
    return players, key_obj, door_obj, platforms, []


