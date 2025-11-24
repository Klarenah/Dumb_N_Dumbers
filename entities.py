import pygame

from config import GRAVITY, WIDTH, HEIGHT


class Player:
    def __init__(self, x=100, y=300):
        self.x = float(x)
        self.y = float(y)
        self.w = 40
        self.h = 56
        self.vel_y = 0.0
        self.on_ground = False
        self.has_key = False
        self.speed = 4

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, keys, platforms):
        move_dir = 0
        if keys[pygame.K_LEFT]:
            move_dir -= 1
        if keys[pygame.K_RIGHT]:
            move_dir += 1
        move_x = move_dir * self.speed
        self.x += move_x

        player_rect = self.rect()
        for platform in platforms:
            if player_rect.colliderect(platform):
                if move_x > 0:
                    self.x = platform.left - self.w
                elif move_x < 0:
                    self.x = platform.right
                player_rect = self.rect()

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        self.vel_y += GRAVITY
        move_y = self.vel_y
        self.y += move_y

        player_rect = self.rect()
        self.on_ground = False
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

        self.x = max(0, min(self.x, WIDTH - self.w))
        self.y = min(self.y, HEIGHT - self.h)

    def draw(self, surface):
        pygame.draw.rect(surface, (30, 120, 255), (int(self.x), int(self.y), self.w, self.h))
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

    def update(self, player):
        if not self.collected and self.rect().colliderect(player.rect()):
            self.collected = True
            player.has_key = True
            self.attached_to_player = True


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
        label = font.render("Open" if self.open else "Door", True, (0, 0, 0))
        surface.blit(label, (self.x - 5, self.y - 28))

    def update(self, player):
        if self.rect().colliderect(player.rect()):
            if player.has_key and not self.open:
                self.open = True
                player.has_key = False

    def player_can_enter(self, player):
        return self.open and self.rect().colliderect(player.rect())

