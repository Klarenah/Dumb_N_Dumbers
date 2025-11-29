import pygame


def has_korean(text):
    """텍스트에 한글이 포함되어 있는지 확인"""
    return any('\uAC00' <= char <= '\uD7A3' for char in text)


class Button:
    def __init__(self, x, y, w, h, text, color=(200, 200, 200), hover=(220, 220, 220)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, surface, font, korean_font=None, shadow=False):
        """
        버튼 그리기
        Args:
            surface: 화면 surface
            font: 기본 폰트 (영어용)
            korean_font: 한글 폰트 (선택사항, None이면 자동 감지)
            shadow: 그림자 효과 사용 여부 (기본값: True)
        """
        mx, my = pygame.mouse.get_pos()
        current_color = self.hover if self.rect.collidepoint(mx, my) else self.color
        
        # 그림자 효과 (입체감)
        if shadow:
            shadow_offset = 5
            shadow_rect = pygame.Rect(
                self.rect.x + shadow_offset,
                self.rect.y + shadow_offset,
                self.rect.w,
                self.rect.h
            )
            # 반투명 검은색 그림자
            shadow_surface = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 80), (0, 0, shadow_rect.w, shadow_rect.h))
            surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
        
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # 한글 폰트가 제공되고 텍스트에 한글이 있으면 한글 폰트 사용
        use_font = korean_font if (korean_font and has_korean(self.text)) else font
            
        label = use_font.render(self.text, True, (0, 0, 0))
        surface.blit(
            label,
            (
                self.rect.x + self.rect.w / 2 - label.get_width() / 2,
                self.rect.y + self.rect.h / 2 - label.get_height() / 2,
            ),
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Slider:
    def __init__(self, x, y, width, start=0.5):
        self.x = x
        self.y = y
        self.w = width
        self.value = start
        self.handle_x = self.x + self.w * self.value
        self.dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), (self.x, self.y, self.w, 8))
        pygame.draw.circle(surface, (0, 160, 255), (int(self.handle_x), self.y + 4), 12)
        return self.value

    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs(mx - self.handle_x) <= 15 and abs(my - (self.y + 4)) <= 15:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            nx = max(self.x, min(mx, self.x + self.w))
            self.handle_x = nx
            self.value = (self.handle_x - self.x) / self.w


def draw_text_center(surface, text, font, color, x, y, korean_font=None):
    """
    텍스트를 중앙 정렬하여 그리기
    Args:
        surface: 화면 surface
        text: 표시할 텍스트
        font: 기본 폰트 (영어용)
        color: 텍스트 색상
        x: X 좌표 (중앙)
        y: Y 좌표
        korean_font: 한글 폰트 (선택사항, None이면 자동 감지)
    """
    # 한글 폰트가 제공되고 텍스트에 한글이 있으면 한글 폰트 사용
    use_font = korean_font if (korean_font and has_korean(text)) else font
        
    label = use_font.render(text, True, color)
    surface.blit(label, (x - label.get_width() // 2, y))

