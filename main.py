import sys
import os
import platform
import pygame

from config import WIDTH, HEIGHT, TITLE, FPS, BACKGROUND_COLOR, MAX_STAGE
from stages import create_stage_objects
from ui import Button, Slider, draw_text_center


STATE_MAIN = "main"
STATE_MENU = "menu"  # Game Start, Settings, Exit 버튼이 있는 메뉴 화면
STATE_SELECT_PLAYER = "select_player"
STATE_STAGE_SELECT = "stage_select"
STATE_GAME = "game"
STATE_CLEAR = "clear"
STATE_SETTINGS = "settings"  # 메뉴에서 들어온 설정 창
STATE_PAUSE = "pause"  # 게임 중 ESC로 들어온 일시정지 창


def create_stage_buttons(total_stages):
    buttons = []
    for i in range(total_stages):
        bx = 150 + (i % 3) * 240
        by = 200 + (i // 3) * 180
        buttons.append(Button(bx, by, 180, 110, f"Stage {i + 1}"))
    return buttons


def initialize_buttons():
    return {
        # 메뉴 화면 버튼들 (건메이헴 스타일 - 좌우 배치)
        "game_start": Button(200, 260, 220, 80, "GAME START", color=(180, 220, 255), hover=(200, 240, 255)),
        "settings": Button(540, 260, 220, 80, "SETTINGS", color=(255, 220, 180), hover=(255, 240, 200)),
        "exit": Button(370, 380, 220, 80, "EXIT", color=(255, 200, 200), hover=(255, 220, 220)),
        # Exit 확인 팝업 버튼들
        "exit_yes": Button(320, 360, 150, 60, "YES", color=(255, 150, 150), hover=(255, 170, 170)),
        "exit_no": Button(490, 360, 150, 60, "NO", color=(200, 200, 200), hover=(220, 220, 220)),
        # 기타 버튼들
        "left": Button(300, 200, 60, 60, "<"),
        "right": Button(600, 200, 60, 60, ">"),
        "start": Button(380, 360, 200, 70, "START"),
        # Settings 창 버튼
        "go_back": Button(360, 480, 240, 70, "GO BACK", color=(200, 200, 200), hover=(220, 220, 220)),
        # Pause 창 버튼들
        "resume": Button(360, 380, 240, 70, "RESUME", color=(180, 255, 180), hover=(200, 255, 200)),
        "back_to_menu": Button(360, 470, 240, 70, "GO BACK TO MAIN MENU", color=(200, 220, 255), hover=(220, 240, 255)),
        "quit_game": Button(360, 560, 240, 70, "QUIT GAME", color=(255, 200, 200), hover=(255, 220, 220)),
        "next": Button(360, 420, 220, 70, "NEXT", color=(200, 255, 200), hover=(180, 255, 180)),
    }


def initialize_sliders():
    return Slider(320, 240, 360, start=0.6), Slider(320, 340, 360, start=0.5)


def load_font_file(font_path, size):
    """
    외부 폰트 파일(.ttf) 로드
    크로스 플랫폼 지원
    """
    try:
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
    except Exception as e:
        print(f"Warning: 폰트 파일 로드 실패 ({font_path}): {e}")
    return None


def get_korean_font(size, bold=False):
    """
    한글 폰트 가져오기 (DungGeunMo.ttf만 사용)
    
    Args:
        size: 폰트 크기
        bold: 굵은 폰트 사용 여부 (기본: False, DungGeunMo는 bold 파라미터 무시)
    """
    # 외부 폰트 파일 시도 (프로젝트/fonts 폴더)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir_local = os.path.join(script_dir, "fonts")  # Dumb_N_Dumbers/fonts/
    fonts_dir_root = os.path.join(os.path.dirname(script_dir), "fonts")  # 프로젝트 루트/fonts/
    
    # 두 위치 모두 확인
    fonts_dirs = [fonts_dir_local, fonts_dir_root]
    
    # DungGeunMo.ttf만 사용
    for fonts_dir in fonts_dirs:
        font_path = os.path.join(fonts_dir, "DungGeunMo.ttf")
        font = load_font_file(font_path, size)
        if font:
            return font
    
    # 폰트 파일을 찾을 수 없으면 기본 폰트 반환 (한글 깨짐 가능)
    print(f"Warning: DungGeunMo.ttf를 찾을 수 없습니다. 기본 폰트를 사용합니다. (한글이 깨질 수 있습니다)")
    return pygame.font.Font(None, size)


def get_english_font(size):
    """
    영어용 기본 폰트 (피코파크 스타일 유지)
    """
    return pygame.font.Font(None, size)


def has_korean(text):
    """
    텍스트에 한글이 포함되어 있는지 확인
    """
    return any('\uAC00' <= char <= '\uD7A3' for char in text)


def get_font_for_text(text, size, korean_font, english_font):
    """
    텍스트 내용에 따라 적절한 폰트 반환
    한글이 있으면 한글 폰트, 영어만 있으면 기본 폰트
    """
    if has_korean(text):
        return korean_font
    else:
        return english_font


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)

    # 폰트 초기화
    # 영어: 피코파크 스타일 기본 폰트 사용
    # 한글: 굵은 한글 폰트 사용 (외부 폰트 파일 우선)
    font = get_english_font(36)  # 영어 기본 폰트
    korean_font = get_korean_font(36, bold=True)  # 한글 굵은 폰트
    big_font = get_english_font(64)
    korean_big_font = get_korean_font(64, bold=True)
    title_font = get_english_font(100)  # 메인 타이틀용 큰 폰트 (영어)
    korean_title_font = get_korean_font(100, bold=True)  # 한글 타이틀용
    clock = pygame.time.Clock()

    buttons = initialize_buttons()
    stage_buttons = create_stage_buttons(MAX_STAGE)
    sound_slider, sfx_slider = initialize_sliders()

    state = STATE_MAIN
    selected_player_count = 1
    current_stage = 1
    show_exit_confirm = False  # Exit 확인 팝업 표시 여부 (오버레이 방식)
    pause_quit_confirm = False  # Pause 창에서 Quit Game 확인 팝업
    # 슬라이더 원래 위치 저장 (Settings 창 복원용)
    slider_orig_positions = None
    player, key_obj, door_obj, platforms = create_stage_objects(current_stage)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == STATE_GAME:
                        state = STATE_PAUSE  # 게임 중 ESC → Pause 창
                    elif state == STATE_PAUSE:
                        if pause_quit_confirm:
                            pause_quit_confirm = False  # Quit Game 확인 팝업 닫기
                        else:
                            # Pause 창에서 나갈 때 슬라이더 위치 복원
                            if slider_orig_positions:
                                sound_slider.x, sound_slider.y, sound_slider.w = slider_orig_positions['sound']
                                sound_slider.handle_x = sound_slider.x + sound_slider.w * sound_slider.value
                                sfx_slider.x, sfx_slider.y, sfx_slider.w = slider_orig_positions['sfx']
                                sfx_slider.handle_x = sfx_slider.x + sfx_slider.w * sfx_slider.value
                                slider_orig_positions = None
                            state = STATE_GAME  # Pause 창에서 ESC → 게임 재개
                    elif state == STATE_SETTINGS:
                        state = STATE_MENU  # Settings 창에서 ESC → 메뉴로 돌아가기
                    elif show_exit_confirm and state == STATE_MENU:
                        show_exit_confirm = False  # Exit 확인 팝업에서 ESC로 취소
                    else:
                        state = STATE_MAIN
                elif event.key == pygame.K_DOWN and state == STATE_GAME:
                    if door_obj.player_can_enter(player):
                        state = STATE_CLEAR

            # Settings와 Pause 창 모두에서 슬라이더 처리
            if state == STATE_SETTINGS or state == STATE_PAUSE:
                sound_slider.handle_event(event)
                sfx_slider.handle_event(event)

            if state == STATE_MAIN:
                # 피코파크 스타일: 아무 키나 누르거나 마우스 클릭하면 메뉴 화면으로
                if event.type == pygame.KEYDOWN:
                    if event.key != pygame.K_ESCAPE:  # ESC 키는 제외
                        state = STATE_MENU
                elif event.type == pygame.MOUSEBUTTONUP:
                    # MOUSEBUTTONUP만 처리하여 버튼과 겹치는 문제 해결
                    # 마우스를 뗄 때만 전환하므로 다음 프레임에서 처리되어 안전함
                    state = STATE_MENU

            elif state == STATE_MENU:
                # Exit 확인 팝업이 떠있으면 팝업 버튼만 처리
                if show_exit_confirm:
                    if buttons["exit_yes"].handle_event(event):
                        running = False  # 게임 종료
                    if buttons["exit_no"].handle_event(event):
                        show_exit_confirm = False  # 팝업 닫기
                else:
                    # 메뉴 화면 버튼 처리
                    if buttons["game_start"].handle_event(event):
                        state = STATE_SELECT_PLAYER
                    if buttons["settings"].handle_event(event):
                        state = STATE_SETTINGS
                    if buttons["exit"].handle_event(event):
                        show_exit_confirm = True  # Exit 확인 팝업 표시

            elif state == STATE_SELECT_PLAYER:
                if buttons["left"].handle_event(event):
                    selected_player_count = max(1, selected_player_count - 1)
                if buttons["right"].handle_event(event):
                    selected_player_count = min(4, selected_player_count + 1)
                if buttons["start"].handle_event(event):
                    state = STATE_STAGE_SELECT

            elif state == STATE_STAGE_SELECT:
                for idx, button in enumerate(stage_buttons):
                    if button.handle_event(event):
                        current_stage = idx + 1
                        player, key_obj, door_obj, platforms = create_stage_objects(current_stage)
                        state = STATE_GAME
                        break

            elif state == STATE_SETTINGS:
                if buttons["go_back"].handle_event(event):
                    state = STATE_MENU  # 메뉴 화면으로 돌아가기
            
            elif state == STATE_PAUSE:
                if pause_quit_confirm:
                    # Quit Game 확인 팝업 처리
                    if buttons["exit_yes"].handle_event(event):
                        running = False  # 게임 종료
                    if buttons["exit_no"].handle_event(event):
                        pause_quit_confirm = False  # 팝업 닫기
                else:
                    # Pause 창 버튼 처리
                    if buttons["resume"].handle_event(event):
                        # 슬라이더 위치 복원
                        if slider_orig_positions:
                            sound_slider.x, sound_slider.y, sound_slider.w = slider_orig_positions['sound']
                            sound_slider.handle_x = sound_slider.x + sound_slider.w * sound_slider.value
                            sfx_slider.x, sfx_slider.y, sfx_slider.w = slider_orig_positions['sfx']
                            sfx_slider.handle_x = sfx_slider.x + sfx_slider.w * sfx_slider.value
                            slider_orig_positions = None
                        state = STATE_GAME  # 게임 재개
                    if buttons["back_to_menu"].handle_event(event):
                        # 슬라이더 위치 복원
                        if slider_orig_positions:
                            sound_slider.x, sound_slider.y, sound_slider.w = slider_orig_positions['sound']
                            sound_slider.handle_x = sound_slider.x + sound_slider.w * sound_slider.value
                            sfx_slider.x, sfx_slider.y, sfx_slider.w = slider_orig_positions['sfx']
                            sfx_slider.handle_x = sfx_slider.x + sfx_slider.w * sfx_slider.value
                            slider_orig_positions = None
                        state = STATE_MENU  # 메뉴로 돌아가기
                    if buttons["quit_game"].handle_event(event):
                        pause_quit_confirm = True  # Quit Game 확인 팝업 표시

            elif state == STATE_CLEAR:
                if buttons["next"].handle_event(event):
                    state = STATE_STAGE_SELECT

        screen.fill(BACKGROUND_COLOR)

        if state == STATE_MAIN:
            # 큰 제목 표시
            draw_text_center(screen, "DUMB N DUMBERS", title_font, (20, 20, 20), WIDTH // 2, HEIGHT // 2 - 100)
            # 피코파크 스타일: Press Any Buttons 메시지
            draw_text_center(screen, "PRESS ANY BUTTONS", font, (50, 50, 50), WIDTH // 2, HEIGHT // 2 + 100)

        elif state == STATE_MENU:
            # 메뉴 화면 디자인: 건메이헴 스타일
            # 배경 장식 요소 추가
            pygame.draw.rect(screen, (230, 230, 235), (50, 50, WIDTH - 100, HEIGHT - 100))
            pygame.draw.rect(screen, (200, 200, 210), (50, 50, WIDTH - 100, HEIGHT - 100), 3)
            
            # Game Start, Settings, Exit 버튼 (건메이헴 스타일 배치)
            buttons["game_start"].draw(screen, font, korean_font)
            buttons["settings"].draw(screen, font, korean_font)
            buttons["exit"].draw(screen, font, korean_font)
            
            # Exit 확인 팝업 오버레이 (메뉴 화면 위에 표시)
            if show_exit_confirm:
                # 반투명 배경 오버레이
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                # 팝업 창 배경
                popup_rect = pygame.Rect(280, 250, 400, 200)
                pygame.draw.rect(screen, (240, 240, 240), popup_rect)
                pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)
                
                # 메시지 표시 (한글 폰트 자동 사용)
                draw_text_center(screen, "정말 종료하시겠습니까?", font, (30, 30, 30), WIDTH // 2, 290, korean_font)
                
                # YES, NO 버튼 (영어만 있으므로 기본 폰트)
                buttons["exit_yes"].draw(screen, font)
                buttons["exit_no"].draw(screen, font)

        elif state == STATE_SELECT_PLAYER:
            draw_text_center(screen, "Select Player Count", font, (30, 30, 30), WIDTH // 2, 110)
            draw_text_center(screen, str(selected_player_count), big_font, (10, 10, 10), WIDTH // 2, 200)
            buttons["left"].draw(screen, font)
            buttons["right"].draw(screen, font)
            buttons["start"].draw(screen, font)

        elif state == STATE_STAGE_SELECT:
            draw_text_center(screen, "Select Stage", font, (30, 30, 30), WIDTH // 2, 60)
            for button in stage_buttons:
                button.draw(screen, font)

        elif state == STATE_GAME or state == STATE_PAUSE:
            # 게임 화면 렌더링 (Pause일 때도 게임 화면을 먼저 그림)
            for platform in platforms:
                pygame.draw.rect(screen, (150, 150, 150), platform)

            # 게임 로직 업데이트 (Pause일 때는 업데이트 안 함)
            if state == STATE_GAME:
                keys = pygame.key.get_pressed()
                player.update(keys, platforms)
                key_obj.update(player)
                door_obj.update(player)
                
                if key_obj.collected and not player.has_key:
                    key_obj.attached_to_player = False
                
                if door_obj.player_can_enter(player):
                    hint = font.render("Press(DOWN) key to enter", True, (0, 0, 0))
                    screen.blit(hint, (door_obj.x - 60, door_obj.y - 40))

            # 게임 화면 그리기 (Pause일 때도 표시)
            for platform in platforms:
                pygame.draw.rect(screen, (120, 120, 120), platform)
            player.draw(screen)
            key_obj.draw(screen)
            door_obj.draw(screen, font)

            stage_label = font.render(f"Stage {current_stage}", True, (0, 0, 0))
            screen.blit(stage_label, (WIDTH - stage_label.get_width() - 12, 12))
            
            # Pause 창이면 오버레이 표시
            if state == STATE_PAUSE:
                # 반투명 배경 오버레이
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                # Pause 창 크기와 위치 (화면 중앙, 상대적 위치) - 더 넓게
                panel_width = 760
                panel_height = 580
                panel_x = (WIDTH - panel_width) // 2
                panel_y = (HEIGHT - panel_height) // 2
                
                pause_panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                pygame.draw.rect(screen, (240, 240, 240), pause_panel)
                pygame.draw.rect(screen, (0, 0, 0), pause_panel, 4)
                
                # PAUSE 제목 (상대적 위치)
                title_y = panel_y + 40
                draw_text_center(screen, "PAUSE", big_font, (0, 0, 0), WIDTH // 2, title_y)
                
                # 볼륨 설정 (상대적 위치) - 레이블과 슬라이더 사이 간격 증가, 숫자는 슬라이더 가까이
                label_start_x = panel_x + 50
                label_y_offset = 100
                slider_x = label_start_x + 340  # 레이블과 슬라이더 사이 간격 더 증가
                slider_width = 260  # 슬라이더 너비
                num_x = slider_x + slider_width + 15  # 숫자를 슬라이더 끝에 더 가깝게 배치
                
                # 슬라이더 원래 위치 저장 (첫 번째 Pause 진입 시에만)
                if slider_orig_positions is None:
                    slider_orig_positions = {
                        'sound': (sound_slider.x, sound_slider.y, sound_slider.w),
                        'sfx': (sfx_slider.x, sfx_slider.y, sfx_slider.w)
                    }
                
                # Background Sound Volume
                sound_label_y = panel_y + label_y_offset
                sound_label = font.render("Background Sound Volume", True, (0, 0, 0))
                screen.blit(sound_label, (label_start_x, sound_label_y))
                
                # Slider 위치 조정 (상대적, Pause 창에서만 사용)
                slider_y = sound_label_y + 5  # 슬라이더 Y 위치 (슬라이더 높이 8, 중앙은 y+4)
                sound_slider.x = slider_x
                sound_slider.y = slider_y
                sound_slider.w = slider_width
                sound_slider.handle_x = sound_slider.x + sound_slider.w * sound_slider.value
                sound_slider.draw(screen)
                
                sound_val = int(sound_slider.value * 10)
                sound_num = font.render(str(sound_val), True, (0, 0, 0))
                # 숫자를 슬라이더 중앙에 맞춤 (슬라이더 높이 8, 중앙은 y+4, 폰트 높이의 절반만큼 빼서 수직 중앙 정렬)
                num_height = sound_num.get_height()
                screen.blit(sound_num, (num_x, slider_y + 4 - num_height // 2))
                
                # Effect Sound Volume
                sfx_label_y = panel_y + label_y_offset + 70
                sfx_label = font.render("Effect Sound Volume", True, (0, 0, 0))
                screen.blit(sfx_label, (label_start_x, sfx_label_y))
                
                # Slider 위치 조정 (상대적, Pause 창에서만 사용)
                sfx_slider_y = sfx_label_y + 5  # 슬라이더 Y 위치 (슬라이더 높이 8, 중앙은 y+4)
                sfx_slider.x = slider_x
                sfx_slider.y = sfx_slider_y
                sfx_slider.w = slider_width
                sfx_slider.handle_x = sfx_slider.x + sfx_slider.w * sfx_slider.value
                sfx_slider.draw(screen)
                
                sfx_val = int(sfx_slider.value * 10)
                sfx_num = font.render(str(sfx_val), True, (0, 0, 0))
                # 숫자를 슬라이더 중앙에 맞춤 (슬라이더 높이 8, 중앙은 y+4, 폰트 높이의 절반만큼 빼서 수직 중앙 정렬)
                num_height = sfx_num.get_height()
                screen.blit(sfx_num, (num_x, sfx_slider_y + 4 - num_height // 2))
                
                # Pause 창 버튼들 (상대적 위치) - 더 넓게
                button_width = 420
                button_height = 70
                button_x = (WIDTH - button_width) // 2
                button_spacing = 85
                button_start_y = panel_y + label_y_offset + 150
                
                # 버튼 위치 업데이트
                buttons["resume"].rect.x = button_x
                buttons["resume"].rect.y = button_start_y
                buttons["resume"].rect.width = button_width
                buttons["resume"].rect.height = button_height
                
                buttons["back_to_menu"].rect.x = button_x
                buttons["back_to_menu"].rect.y = button_start_y + button_spacing
                buttons["back_to_menu"].rect.width = button_width
                buttons["back_to_menu"].rect.height = button_height
                
                buttons["quit_game"].rect.x = button_x
                buttons["quit_game"].rect.y = button_start_y + button_spacing * 2
                buttons["quit_game"].rect.width = button_width
                buttons["quit_game"].rect.height = button_height
                
                buttons["resume"].draw(screen, font, korean_font)
                buttons["back_to_menu"].draw(screen, font, korean_font)
                buttons["quit_game"].draw(screen, font, korean_font)
                
                # Quit Game 확인 팝업 (Pause 창 위에 표시)
                if pause_quit_confirm:
                    # 더 진한 오버레이
                    confirm_overlay = pygame.Surface((WIDTH, HEIGHT))
                    confirm_overlay.set_alpha(150)
                    confirm_overlay.fill((0, 0, 0))
                    screen.blit(confirm_overlay, (0, 0))
                    
                    # 확인 팝업 창
                    popup_rect = pygame.Rect(280, 250, 400, 200)
                    pygame.draw.rect(screen, (250, 250, 250), popup_rect)
                    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)
                    
                    draw_text_center(screen, "정말 종료하시겠습니까?", font, (30, 30, 30), WIDTH // 2, 290, korean_font)
                    buttons["exit_yes"].draw(screen, font)
                    buttons["exit_no"].draw(screen, font)

        elif state == STATE_CLEAR:
            draw_text_center(screen, "STAGE CLEAR!", big_font, (10, 10, 10), WIDTH // 2, 140)
            buttons["next"].draw(screen, font)

        elif state == STATE_SETTINGS:
            # Settings 창으로 들어올 때 슬라이더 위치 복원
            if slider_orig_positions:
                sound_slider.x, sound_slider.y, sound_slider.w = slider_orig_positions['sound']
                sound_slider.handle_x = sound_slider.x + sound_slider.w * sound_slider.value
                sfx_slider.x, sfx_slider.y, sfx_slider.w = slider_orig_positions['sfx']
                sfx_slider.handle_x = sfx_slider.x + sfx_slider.w * sfx_slider.value
                slider_orig_positions = None
            
            # Settings 창 (메뉴에서 들어온 설정)
            draw_text_center(screen, "SETTINGS", big_font, (0, 0, 0), WIDTH // 2, 80)
            sound_label = font.render("Background Sound Volume", True, (0, 0, 0))
            sfx_label = font.render("Effect Sound Volume", True, (0, 0, 0))
            screen.blit(sound_label, (220, 206))
            screen.blit(sfx_label, (220, 306))

            sound_slider.draw(screen)
            sfx_slider.draw(screen)
            sound_val = int(sound_slider.value * 10)
            sfx_val = int(sfx_slider.value * 10)
            sound_num = font.render(str(sound_val), True, (0, 0, 0))
            sfx_num = font.render(str(sfx_val), True, (0, 0, 0))
            screen.blit(sound_num, (700, 226))
            screen.blit(sfx_num, (700, 326))

            buttons["go_back"].draw(screen, font, korean_font)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
