
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

    def update(self, keys, platforms, other_players=None):
        if other_players is None:
            other_players = []
        
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
            if player_rect.colliderect(platform):
                if move_x > 0:
                    self.x = platform.left - self.w
                elif move_x < 0:
                    self.x = platform.right
                player_rect = self.rect()
        
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

