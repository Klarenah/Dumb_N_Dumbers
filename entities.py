import pygame

from config import GRAVITY, WIDTH, HEIGHT, PICO_TEXT_COLOR


class Player:
    def __init__(self, x=100, y=300, color=(30, 120, 255), key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_up=pygame.K_UP, key_interact=pygame.K_DOWN):

        self.x = float(x)
        self.y = float(y)
        self.w = 40
        self.h = 56
        self.vel_y = 0.0
        self.on_ground = False
        self.has_key = False
        self.speed = 4

        self.color = color
        self.key_left = key_left
        self.key_right = key_right
        self.key_up = key_up
        self.key_interact = key_interact
        self.interacted_with_door = False  # 문과 상호작용했는지 추적
        self.entered_door = False  # 문 안으로 들어갔는지 추적

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, keys, platforms, other_players=None, walls=None):
        if other_players is None:
            other_players = []
        if walls is None:
            walls = []
        
        # 문 안으로 들어간 플레이어는 움직이지 않음
        if self.entered_door:
            return
        
        move_dir = 0
        try:
            left_pressed = keys[self.key_left]
            right_pressed = keys[self.key_right]
        except (IndexError, TypeError):
            left_pressed = False
            right_pressed = False
        
        if left_pressed:
            move_dir -= 1
        if right_pressed:
            move_dir += 1
        move_x = move_dir * self.speed
        self.x += move_x

        player_rect = self.rect()
        # 플랫폼 충돌 처리
        for platform in platforms:
            # platform이 Rect인지 확인
            if isinstance(platform, pygame.Rect):
                if player_rect.colliderect(platform):
                    if move_x > 0:
                        self.x = platform.left - self.w
                    elif move_x < 0:
                        self.x = platform.right
                    player_rect = self.rect()
        
        # 벽과의 X축 충돌 처리 (밀고 있지 않을 때만)
        for wall in walls:
            wall_rect = wall.rect()
            if player_rect.colliderect(wall_rect):
                # 플레이어가 벽을 밀고 있는지 확인
                try:
                    is_pushing = False
                    if wall.move_direction == "right":
                        # 벽이 오른쪽으로 이동: 오른쪽 키를 누르고, 플레이어가 벽 왼쪽에 있음
                        if keys[self.key_right]:
                            player_center_x = player_rect.centerx
                            if player_center_x < wall_rect.left + 30:
                                is_pushing = True
                    elif wall.move_direction == "left":
                        # 벽이 왼쪽으로 이동: 왼쪽 키를 누르고, 플레이어가 벽 오른쪽에 있음
                        if keys[self.key_left]:
                            player_center_x = player_rect.centerx
                            if player_center_x > wall_rect.right - 30:
                                is_pushing = True
                    
                    # 밀고 있지 않으면 플레이어를 벽 밖으로 밀어냄
                    if not is_pushing:
                        if move_x > 0:
                            # 오른쪽으로 이동 중 벽에 충돌
                            self.x = wall_rect.left - self.w
                        elif move_x < 0:
                            # 왼쪽으로 이동 중 벽에 충돌
                            self.x = wall_rect.right
                        else:
                            # 정지 상태에서 벽과 겹침 - 가장 가까운 쪽으로 이동
                            if player_rect.centerx < wall_rect.centerx:
                                self.x = wall_rect.left - self.w
                            else:
                                self.x = wall_rect.right
                        player_rect = self.rect()
                except (IndexError, TypeError):
                    pass
        
        # 다른 플레이어와의 X축 충돌 처리 (문 안으로 들어간 플레이어는 제외)
        for other in other_players:
            if other is not self and not other.entered_door and player_rect.colliderect(other.rect()):
                if move_x > 0:
                    # 오른쪽으로 이동 중 충돌 → 왼쪽으로 밀어냄
                    self.x = other.rect().left - self.w
                elif move_x < 0:
                    # 왼쪽으로 이동 중 충돌 → 오른쪽으로 밀어냄
                    self.x = other.rect().right
                player_rect = self.rect()

        try:
            if keys[self.key_up] and self.on_ground:
                self.vel_y = -13
                self.on_ground = False
        except (IndexError, TypeError):
            pass

        self.vel_y += GRAVITY
        move_y = self.vel_y
        self.y += move_y

        player_rect = self.rect()
        self.on_ground = False
        # 플랫폼 충돌 처리
        for platform in platforms:
            if player_rect.colliderect(platform):
                if move_y > 0:
                    self.y = platform.top - self.h
                    self.vel_y = 0
                    self.on_ground = True
                elif move_y < 0:
                    self.y = platform.bottom
                    self.vel_y = 0
                player_rect = self.rect()

        # 벽과의 Y축 충돌 처리 (벽 위로 올라가지 않도록)
        for wall in walls:
            wall_rect = wall.rect()
            if player_rect.colliderect(wall_rect):
                # 벽은 플랫폼이 아니므로 위에 올라가지 못함
                if move_y < 0:
                    # 위로 이동 중 벽에 충돌 → 아래로 밀어냄
                    self.y = wall_rect.bottom
                    self.vel_y = 0
                # move_y > 0인 경우 (아래로 떨어지는 중)는 벽 위에 올라가지 않도록 처리하지 않음
                # 벽은 세로로 긴 장애물이므로 플레이어가 벽 위에 착지하지 못함
                player_rect = self.rect()
        
        # 다른 플레이어와의 Y축 충돌 처리 (문 안으로 들어간 플레이어는 제외)
        for other in other_players:
            if other is not self and not other.entered_door and player_rect.colliderect(other.rect()):
                if move_y > 0:
                    # 아래로 떨어지는 중 충돌 → 위로 밀어냄
                    self.y = other.rect().top - self.h
                    self.vel_y = 0
                    self.on_ground = True
                elif move_y < 0:
                    # 위로 이동 중 충돌 → 아래로 밀어냄
                    self.y = other.rect().bottom
                    self.vel_y = 0
                player_rect = self.rect()

        self.x = max(0, min(self.x, WIDTH - self.w))
        self.y = min(self.y, HEIGHT - self.h)

    def draw(self, surface):

        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.w, self.h))
        if self.has_key:
            pygame.draw.rect(
                surface, (255, 215, 0), (int(self.x + self.w + 6), int(self.y + 12), 18, 18)
            )


class KeyObj:
    def __init__(self, x=520, y=340):
        self.x = x
        self.y = y
        self.w = 18
        self.h = 18
        self.collected = False
        self.attached_to_player = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surface):
        if self.collected:
            return
        pygame.draw.rect(surface, (255, 215, 0), (self.x, self.y, self.w, self.h))

    def update(self, players):
        """players는 Player 객체의 리스트"""
        if self.collected:
            return
        for player in players:
            if self.rect().colliderect(player.rect()):
                self.collected = True
                player.has_key = True
                self.attached_to_player = True
                break


class Door:
    def __init__(self, x=760, y=240):
        self.x = x
        self.y = y
        self.w = 48
        self.h = 96
        self.open = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surface, font):
        color = (60, 200, 60) if self.open else (150, 90, 60)
        pygame.draw.rect(surface, color, (self.x, self.y, self.w, self.h))
        label = font.render("Open" if self.open else "Door", True, PICO_TEXT_COLOR)
        surface.blit(label, (self.x - 5, self.y - 28))

    def update(self, players):
        """players는 Player 객체의 리스트"""
        for player in players:
            if self.rect().colliderect(player.rect()):
                if player.has_key and not self.open:
                    self.open = True
                    player.has_key = False

    def check_interaction(self, players, keys):
        """플레이어들이 문과 상호작용했는지 확인하고 업데이트"""
        if not self.open:
            return
        door_rect = self.rect()
        for player in players:
            if door_rect.colliderect(player.rect()):
                try:
                    key_pressed = keys[player.key_interact] and not player.entered_door
                except (IndexError, TypeError):
                    key_pressed = False
                if key_pressed:
                    player.interacted_with_door = True
                    player.entered_door = True
                    # 플레이어를 문의 중앙으로 이동
                    player.x = self.x + (self.w - player.w) / 2
                    player.y = self.y + (self.h - player.h) / 2
                    player.vel_y = 0  # 속도 초기화

    def all_players_interacted(self, players):
        """모든 플레이어가 문과 상호작용했는지 확인"""
        if not self.open:
            return False
        for player in players:
            if not player.interacted_with_door:
                return False
        return True

    def reset_interactions(self, players):
        """플레이어들의 상호작용 상태 초기화"""
        for player in players:
            player.interacted_with_door = False
            player.entered_door = False


class MovableWall:
    """밀 수 있는 벽"""
    def __init__(self, x, y, width, height, required_players=1, move_direction="right", min_x=None, max_x=None):
        self.x = float(x)
        self.y = float(y)
        self.w = width
        self.h = height
        self.required_players = required_players  # 벽을 움직이는데 필요한 플레이어 수
        self.move_direction = move_direction  # "left" or "right"
        self.min_x = min_x if min_x is not None else 0
        self.max_x = max_x if max_x is not None else WIDTH
        self.speed = 4  # 벽 이동 속도 (플레이어 속도와 동일)
        
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
    
    def update(self, players, keys, active_players_count=None):
        """플레이어들이 벽을 밀고 있는지 확인하고 이동"""
        wall_rect = self.rect()
        pushing_players = []
        
        # 벽과 접촉하고 있는 플레이어 확인
        for player in players:
            if player.entered_door:
                continue
            player_rect = player.rect()
            if wall_rect.colliderect(player_rect):
                # 플레이어가 벽을 향해 이동하고 있는지 확인
                try:
                    if self.move_direction == "right":
                        # 벽이 오른쪽으로 이동: 왼쪽에서 밀기 (오른쪽 키를 누르고, 플레이어가 벽 왼쪽에 있음)
                        if keys[player.key_right]:
                            # 플레이어의 중심이 벽의 왼쪽에 있는지 확인
                            player_center_x = player_rect.centerx
                            wall_left = wall_rect.left
                            if player_center_x < wall_left + 30:  # 여유 공간 증가
                                pushing_players.append(player)
                    elif self.move_direction == "left":
                        # 벽이 왼쪽으로 이동: 오른쪽에서 밀기 (왼쪽 키를 누르면서 벽 오른쪽에 접촉)
                        if keys[player.key_left]:
                            # 플레이어가 벽 오른쪽에 있는지 확인 (플레이어 중심이 벽 오른쪽에 있음)
                            player_center_x = player_rect.centerx
                            wall_right = wall_rect.right
                            if player_center_x > wall_right - 30:  # 여유 공간 증가
                                pushing_players.append(player)
                except (IndexError, TypeError):
                    pass
        
        # 필요한 플레이어 수만큼 밀고 있으면 벽 이동
        # required_players가 -1이면 모든 활성 플레이어가 필요
        if self.required_players == -1:
            required = active_players_count if active_players_count is not None else len(players)
        else:
            required = self.required_players
        if len(pushing_players) >= required:
            if self.move_direction == "right":
                new_x = min(self.x + self.speed, self.max_x - self.w)
            else:  # left
                new_x = max(self.x - self.speed, self.min_x)
            
            # 벽 이동
            move_amount = new_x - self.x
            self.x = new_x
            
            # 벽을 밀고 있는 플레이어들도 함께 이동
            for player in pushing_players:
                player.x += move_amount
                # 플레이어가 화면 밖으로 나가지 않도록
                player.x = max(0, min(player.x, WIDTH - player.w))
    
    def draw(self, surface, font=None, active_players_count=None):
        """벽 그리기"""
        pygame.draw.rect(surface, (100, 100, 100), (int(self.x), int(self.y), self.w, self.h))
        pygame.draw.rect(surface, (0, 0, 0), (int(self.x), int(self.y), self.w, self.h), 2)
        
        # 필요한 플레이어 수 표시
        if font:
            if self.required_players == -1:
                # 모든 플레이어가 필요한 경우
                required = active_players_count if active_players_count is not None else 3
                text = f"{required}"
            else:
                text = f"{self.required_players}"
            
            text_surface = font.render(text, True, (255, 255, 255))
            # 벽 중앙에 텍스트 표시
            text_x = int(self.x + self.w / 2 - text_surface.get_width() / 2)
            text_y = int(self.y + self.h / 2 - text_surface.get_height() / 2)
            surface.blit(text_surface, (text_x, text_y))


class MovingPlatform:
    """움직이는 발판 클래스"""
    def __init__(self, x, y, w, h, min_y, max_y, speed=2):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.min_y = min_y  # 아래쪽 한계 (큰 Y 값)
        self.max_y = max_y  # 위쪽 한계 (작은 Y 값)
        self.speed = speed
        # 초기 방향: min_y에서 시작하면 위로, max_y에서 시작하면 아래로
        if y >= (min_y + max_y) / 2:
            self.direction = -1  # 위로 시작 (y 감소)
        else:
            self.direction = 1  # 아래로 시작 (y 증가)
        self.start_y = float(y)
    
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
    
    def update(self):
        """발판 이동 업데이트"""
        self.y += self.speed * self.direction
        
        # Y 좌표계: 위쪽이 작은 값, 아래쪽이 큰 값
        # max_y는 위쪽(작은 값), min_y는 아래쪽(큰 값)
        if self.direction == 1:  # 아래로 이동 중 (y 증가)
            if self.y >= self.min_y:  # 아래쪽 한계에 도달
                self.y = self.min_y
                self.direction = -1  # 위로 방향 전환
        else:  # 위로 이동 중 (y 감소)
            if self.y <= self.max_y:  # 위쪽 한계에 도달
                self.y = self.max_y
                self.direction = 1  # 아래로 방향 전환
    
    def draw(self, surface):
        """발판 그리기"""
        pygame.draw.rect(surface, (150, 150, 150), (int(self.x), int(self.y), self.w, self.h))
        pygame.draw.rect(surface, (0, 0, 0), (int(self.x), int(self.y), self.w, self.h), 2)


class SyncedPlayer:
    """4스테이지용 동기화된 플레이어 (모든 플레이어가 같은 입력을 해야 움직임)"""
    def __init__(self, x=100, y=300, color=(30, 120, 255)):
        self.x = float(x)
        self.y = float(y)
        self.w = 40
        self.h = 56
        self.vel_y = 0.0
        self.on_ground = False
        self.has_key = False
        self.speed = 4
        self.color = color
        self.interacted_with_door = False
        self.entered_door = False
    
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
    
    def update(self, keys, platforms, other_platforms=None, all_players_keys=None):
        """모든 플레이어가 같은 입력을 했을 때만 움직임"""
        if other_platforms is None:
            other_platforms = []
        if all_players_keys is None or len(all_players_keys) == 0:
            return
        
        # 각 플레이어의 입력 확인
        player_inputs = []
        for keys_dict in all_players_keys:
            # 각 플레이어의 왼쪽/오른쪽/위 입력 확인
            left = keys_dict.get(pygame.K_LEFT, False) or keys_dict.get(pygame.K_a, False) or keys_dict.get(pygame.K_j, False)
            right = keys_dict.get(pygame.K_RIGHT, False) or keys_dict.get(pygame.K_d, False) or keys_dict.get(pygame.K_l, False)
            up = keys_dict.get(pygame.K_UP, False) or keys_dict.get(pygame.K_w, False) or keys_dict.get(pygame.K_i, False)
            player_inputs.append((left, right, up))
        
        # 모든 플레이어가 같은 입력을 했는지 확인
        if len(player_inputs) == 0:
            return
        
        all_left = all(p[0] for p in player_inputs) and not any(p[1] for p in player_inputs)
        all_right = all(p[1] for p in player_inputs) and not any(p[0] for p in player_inputs)
        all_up = all(p[2] for p in player_inputs)
        
        if self.entered_door:
            return
        
        move_dir = 0
        if all_left and not all_right:
            move_dir = -1
        elif all_right and not all_left:
            move_dir = 1
        move_x = move_dir * self.speed
        self.x += move_x
        
        # 플랫폼 충돌 처리
        player_rect = self.rect()
        all_platforms = platforms + other_platforms
        for platform in all_platforms:
            if player_rect.colliderect(platform):
                if move_x > 0:
                    self.x = platform.left - self.w
                elif move_x < 0:
                    self.x = platform.right
                player_rect = self.rect()
        
        # 점프 처리
        if all_up and self.on_ground:
            self.vel_y = -13
            self.on_ground = False
        
        # 중력 적용
        self.vel_y += GRAVITY
        move_y = self.vel_y
        self.y += move_y
        
        # 플랫폼 충돌 처리
        player_rect = self.rect()
        self.on_ground = False
        for platform in all_platforms:
            if player_rect.colliderect(platform):
                if move_y > 0:
                    self.y = platform.top - self.h
                    self.vel_y = 0
                    self.on_ground = True
                elif move_y < 0:
                    self.y = platform.bottom
                    self.vel_y = 0
                player_rect = self.rect()
        
        self.x = max(0, min(self.x, WIDTH - self.w))
        self.y = min(self.y, HEIGHT - self.h)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.w, self.h))
        if self.has_key:
            pygame.draw.rect(surface, (255, 215, 0), (int(self.x + self.w + 6), int(self.y + 12), 18, 18))


class Spike:
    """가시 클래스 - 플레이어가 닿으면 게임 오버"""
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
    
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        """가시 그리기 (삼각형 모양)"""
        # 가시 색상 (빨간색)
        color = (200, 0, 0)
        # 삼각형 가시 여러 개 그리기
        spike_count = self.width // 20
        for i in range(spike_count):
            spike_x = self.x + i * 20
            # 삼각형 꼭짓점
            points = [
                (spike_x + 10, self.y),
                (spike_x, self.y + self.height),
                (spike_x + 20, self.y + self.height)
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (150, 0, 0), points, 2)
    
    def check_collision(self, players):
        """플레이어와 충돌 확인"""
        spike_rect = self.rect()
        for player in players:
            if spike_rect.colliderect(player.rect()):
                return True
        return False


class FloorButton:
    """바닥을 생성하는 버튼"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 60
        self.h = 20
        self.pressed = False
        self.color = (100, 200, 100)  # 초록색
    
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def draw(self, surface, font):
        """버튼 그리기"""
        if self.pressed:
            color = (60, 150, 60)  # 눌린 상태: 더 어두운 초록색
        else:
            color = self.color
        pygame.draw.rect(surface, color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h), 2)
        
        # 버튼 텍스트
        label = font.render("Button", True, (0, 0, 0))
        surface.blit(label, (self.x + 5, self.y - 25))
    
    def update(self, players):
        """플레이어가 버튼을 눌렀는지 확인"""
        button_rect = self.rect()
        for player in players:
            if button_rect.colliderect(player.rect()):
                if not self.pressed:
                    self.pressed = True
                    return True
        return False

