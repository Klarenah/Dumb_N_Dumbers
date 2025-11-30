import sys
import os
import math
import pygame

from config import WIDTH, HEIGHT, TITLE, FPS, BACKGROUND_COLOR, MAX_STAGE, PICO_TEXT_COLOR, PICO_FLOOR_COLOR
from stages import create_stage_objects
from ui import Button, Slider, draw_text_center


STATE_MAIN = "main"
STATE_MENU = "menu"  # Game Start, Settings, Exit 버튼이 있는 메뉴 화면
STATE_SELECT_PLAYER_COUNT = "select_player_count"  # 플레이어 수 선택
STATE_CUSTOMIZE_PLAYERS = "customize_players"  # 플레이어 커스터마이징
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
        # 메뉴 화면 버튼들 (중앙 정렬, 세로 배치, 가로로 긴 형태 - 2배 길이)
        "game_start": Button((WIDTH - 800) // 2, 200, 800, 80, "GAME START", color=(180, 220, 255), hover=(200, 240, 255)),
        "settings": Button((WIDTH - 800) // 2, 300, 800, 80, "SETTINGS", color=(255, 220, 180), hover=(255, 240, 200)),
        "exit": Button((WIDTH - 800) // 2, 400, 800, 80, "EXIT", color=(255, 200, 200), hover=(255, 220, 220)),
        # Exit 확인 팝업 버튼들
        "exit_yes": Button(320, 360, 150, 60, "YES", color=(255, 150, 150), hover=(255, 170, 170)),
        "exit_no": Button(490, 360, 150, 60, "NO", color=(200, 200, 200), hover=(220, 220, 220)),
        # 기타 버튼들
        "left": Button(300, 200, 60, 60, "<", color=PICO_TEXT_COLOR, hover=(255, 180, 100)),
        "right": Button(600, 200, 60, 60, ">", color=PICO_TEXT_COLOR, hover=(255, 180, 100)),
        "next_to_customize": Button(380, 360, 200, 70, "NEXT"),
        "select_stage": Button(WIDTH - 240, HEIGHT - 180, 220, 70, "SELECT STAGE", color=(240, 240, 240), hover=(220, 220, 220)),
        # Settings 창 버튼 (바닥 위에 여백을 두고 위치)
        "go_back": Button(360, 400, 240, 70, "GO BACK", color=(200, 200, 200), hover=(220, 220, 220)),
        # Pause 창 버튼들
        "resume": Button(360, 380, 240, 70, "RESUME", color=(180, 255, 180), hover=(200, 255, 200)),
        "reset_stage": Button(360, 470, 240, 70, "RESET STAGE", color=(255, 255, 180), hover=(255, 255, 200)),
        "back_to_menu": Button(360, 560, 240, 70, "GO BACK TO MAIN MENU", color=(200, 220, 255), hover=(220, 240, 255)),
        "quit_game": Button(360, 650, 240, 70, "QUIT GAME", color=(255, 200, 200), hover=(255, 220, 220)),
        "next": Button(360, 420, 220, 70, "NEXT", color=(200, 255, 200), hover=(180, 255, 180)),
    }


def initialize_sliders():
    return Slider(320, 240, 360, start=0.6), Slider(320, 340, 360, start=0.5)


def get_korean_font(size):
    """한글 폰트 로드 (DungGeunMo.ttf)"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dirs = [
        os.path.join(script_dir, "fonts"),
        os.path.join(os.path.dirname(script_dir), "fonts")
    ]
    
    for fonts_dir in fonts_dirs:
        font_path = os.path.join(fonts_dir, "DungGeunMo.ttf")
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    return pygame.font.Font(None, size)


def get_english_font(size):
    """영어용 기본 폰트"""
    return pygame.font.Font(None, size)


def restore_slider_positions(sound_slider, sfx_slider, slider_orig_positions):
    """슬라이더 위치를 원래대로 복원"""
    if slider_orig_positions:
        sound_slider.x, sound_slider.y, sound_slider.w = slider_orig_positions['sound']
        sound_slider.handle_x = sound_slider.x + sound_slider.w * sound_slider.value
        sfx_slider.x, sfx_slider.y, sfx_slider.w = slider_orig_positions['sfx']
        sfx_slider.handle_x = sfx_slider.x + sfx_slider.w * sfx_slider.value
        return None
    return slider_orig_positions


def create_overlay(width, height, alpha):
    """반투명 오버레이 생성"""
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(alpha)
    overlay.fill((0, 0, 0))
    return overlay


def draw_grass_background(screen):
    """인게임 바닥 스타일 배경 그리기 (화면 하단) - 단순한 직사각형"""
    floor_height = 120  # 바닥 높이
    floor_y = HEIGHT - floor_height
    
    # 단순한 바닥 (인게임 플랫폼과 동일한 스타일)
    pygame.draw.rect(screen, PICO_FLOOR_COLOR, (0, floor_y, WIDTH, floor_height))


def draw_confirm_popup(screen, font, korean_font, buttons, message):
    """확인 팝업 그리기"""
    # 반투명 배경 오버레이
    overlay = create_overlay(WIDTH, HEIGHT, 200)
    screen.blit(overlay, (0, 0))
    
    # 팝업 창 배경
    popup_rect = pygame.Rect(280, 250, 400, 200)
    pygame.draw.rect(screen, (240, 240, 240), popup_rect)
    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)
    
    # 메시지 표시
    draw_text_center(screen, message, font, PICO_TEXT_COLOR, WIDTH // 2, 290, korean_font)
    
    # YES, NO 버튼
    buttons["exit_yes"].draw(screen, font)
    buttons["exit_no"].draw(screen, font)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)

    # 폰트 초기화
    font = get_english_font(36)
    korean_font = get_korean_font(36)
    big_font = get_english_font(64)
    title_font = get_english_font(100)
    clock = pygame.time.Clock()

    buttons = initialize_buttons()
    stage_buttons = create_stage_buttons(MAX_STAGE)
    sound_slider, sfx_slider = initialize_sliders()

    state = STATE_MAIN
    selected_player_count = 2  # 최소 2명
    current_stage = 1
    unlocked_stages = [1]  # 잠금 해제된 스테이지 (초기값: Stage 1만 해제)
    show_exit_confirm = False  # Exit 확인 팝업 표시 여부 (오버레이 방식)
    pause_quit_confirm = False  # Pause 창에서 Quit Game 확인 팝업
    # 슬라이더 원래 위치 저장 (Settings 창 복원용)
    slider_orig_positions = None
    
    # 플레이어 커스터마이징 데이터 (먼저 정의)
    player_names = ["Player 1", "Player 2", "Player 3"]
    player_colors = [(30, 120, 255), (255, 80, 80), (80, 255, 80)]  # 기본 색상
    editing_player_name = None  # 현재 이름 편집 중인 플레이어 인덱스
    showing_color_picker = None  # 현재 색상 선택 팝업을 보여줄 플레이어 인덱스
    color_picker_colors = [
        (30, 120, 255), (255, 80, 80), (80, 255, 80),  # 파란색, 빨간색, 초록색
        (255, 180, 100), (255, 200, 0), (180, 100, 255),  # 주황색, 노란색, 보라색
        (255, 100, 150), (100, 255, 200), (200, 200, 200)  # 분홍색, 청록색, 회색
    ]
    
    # 게임 오브젝트 초기화 (player_colors 정의 후)
    stage_result = create_stage_objects(current_stage, player_colors)
    if len(stage_result) == 7:
        # 3스테이지: spike, floor_button 포함
        players, key_obj, door_obj, platforms, moving_platforms, spike, floor_button = stage_result
        bottom_spike = None
    elif len(stage_result) == 6:
        # 4스테이지: bottom_spike 포함
        players, key_obj, door_obj, platforms, moving_platforms, bottom_spike = stage_result
        spike = None
        floor_button = None
    elif len(stage_result) == 5:
        players, key_obj, door_obj, platforms, moving_platforms = stage_result
        spike = None
        floor_button = None
        bottom_spike = None
    else:
        players, key_obj, door_obj, platforms = stage_result
        moving_platforms = []
        spike = None
        floor_button = None
        bottom_spike = None

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
                            slider_orig_positions = restore_slider_positions(
                                sound_slider, sfx_slider, slider_orig_positions
                            )
                            state = STATE_GAME  # Pause 창에서 ESC → 게임 재개
                    elif state == STATE_SETTINGS:
                        state = STATE_MENU  # Settings 창에서 ESC → 메뉴로 돌아가기
                    elif show_exit_confirm and state == STATE_MENU:
                        show_exit_confirm = False  # Exit 확인 팝업에서 ESC로 취소
                    else:
                        state = STATE_MAIN
                # 상호작용 키는 KEYDOWN 이벤트에서 처리하지 않고, 게임 루프에서 지속적으로 체크

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
                        state = STATE_SELECT_PLAYER_COUNT
                    if buttons["settings"].handle_event(event):
                        state = STATE_SETTINGS
                    if buttons["exit"].handle_event(event):
                        show_exit_confirm = True  # Exit 확인 팝업 표시

            elif state == STATE_SELECT_PLAYER_COUNT:
                if buttons["left"].handle_event(event):
                    selected_player_count = max(2, selected_player_count - 1)
                if buttons["right"].handle_event(event):
                    selected_player_count = min(3, selected_player_count + 1)
                if buttons["next_to_customize"].handle_event(event):
                    state = STATE_CUSTOMIZE_PLAYERS
            
            elif state == STATE_CUSTOMIZE_PLAYERS:
                # 이름 편집 처리
                if event.type == pygame.KEYDOWN:
                    if editing_player_name is not None:
                        if event.key == pygame.K_RETURN:
                            editing_player_name = None
                        elif event.key == pygame.K_BACKSPACE:
                            if len(player_names[editing_player_name]) > 0:
                                player_names[editing_player_name] = player_names[editing_player_name][:-1]
                        else:
                            if len(player_names[editing_player_name]) < 15:  # 최대 길이 제한
                                player_names[editing_player_name] += event.unicode
                
                # 마우스 클릭 처리
                if event.type == pygame.MOUSEBUTTONUP:
                    mx, my = pygame.mouse.get_pos()
                    
                    # 색상 선택 팝업 처리
                    if showing_color_picker is not None:
                        picker_x = WIDTH // 2 - 200
                        floor_height = 120
                        floor_y = HEIGHT - floor_height
                        picker_y = floor_y - 350 - 40  # 바닥에서 40픽셀 위로
                        if not (picker_x <= mx <= picker_x + 400 and picker_y <= my <= picker_y + 350):
                            showing_color_picker = None
                        else:
                            # 색상 버튼 클릭 확인 (새로운 위치에 맞춰서)
                            btn_size = 70
                            btn_spacing = 20
                            grid_width = 3 * btn_size + 2 * btn_spacing
                            grid_start_x = picker_x + (400 - grid_width) // 2
                            grid_start_y = picker_y + 60
                            
                            for i, color in enumerate(color_picker_colors):
                                btn_x = grid_start_x + (i % 3) * (btn_size + btn_spacing)
                                btn_y = grid_start_y + (i // 3) * (btn_size + btn_spacing)
                                if btn_x <= mx <= btn_x + btn_size and btn_y <= my <= btn_y + btn_size:
                                    player_colors[showing_color_picker] = color
                                    showing_color_picker = None
                                    break
                    else:
                        # 이름 편집 영역 클릭 확인
                        box_width = 250
                        box_spacing = 30
                        total_width = selected_player_count * box_width + (selected_player_count - 1) * box_spacing
                        start_x = (WIDTH - total_width) // 2
                        box_y = 150
                        
                        for i in range(selected_player_count):
                            box_x = start_x + i * (box_width + box_spacing)
                            name_rect = pygame.Rect(box_x + 10, box_y + 20, box_width - 20, 30)
                            if name_rect.collidepoint(mx, my):
                                editing_player_name = i
                                break
                            
                            # 색상 선택 버튼 클릭 확인
                            color_btn_y = box_y + 80 + 60 + 20
                            color_btn_rect = pygame.Rect(box_x + 50, color_btn_y, box_width - 100, 40)
                            if color_btn_rect.collidepoint(mx, my):
                                showing_color_picker = i
                                break
                
                # Select Stage 버튼
                if buttons["select_stage"].handle_event(event):
                    state = STATE_STAGE_SELECT

            elif state == STATE_STAGE_SELECT:
                for idx, button in enumerate(stage_buttons):
                    stage_num = idx + 1
                    # 잠금 해제된 스테이지만 클릭 가능
                    if stage_num in unlocked_stages and button.handle_event(event):
                        current_stage = stage_num
                        stage_result = create_stage_objects(current_stage, player_colors)
                        if len(stage_result) == 7:
                            players, key_obj, door_obj, platforms, moving_platforms, spike, floor_button = stage_result
                            bottom_spike = None
                        elif len(stage_result) == 6:
                            players, key_obj, door_obj, platforms, moving_platforms, bottom_spike = stage_result
                            spike = None
                            floor_button = None
                        elif len(stage_result) == 5:
                            players, key_obj, door_obj, platforms, moving_platforms = stage_result
                            spike = None
                            floor_button = None
                            bottom_spike = None
                        else:
                            players, key_obj, door_obj, platforms = stage_result
                            moving_platforms = []
                            spike = None
                            floor_button = None
                            bottom_spike = None
                        # 상호작용 상태 초기화
                        active_players = players[:selected_player_count]
                        door_obj.reset_interactions(active_players)
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
                        slider_orig_positions = restore_slider_positions(
                            sound_slider, sfx_slider, slider_orig_positions
                        )
                        state = STATE_GAME  # 게임 재개
                    if buttons["reset_stage"].handle_event(event):
                        # 스테이지 리셋: 현재 스테이지 재초기화
                        stage_result = create_stage_objects(current_stage, player_colors)
                        if len(stage_result) == 7:
                            players, key_obj, door_obj, platforms, moving_platforms, spike, floor_button = stage_result
                            bottom_spike = None
                        elif len(stage_result) == 6:
                            players, key_obj, door_obj, platforms, moving_platforms, bottom_spike = stage_result
                            spike = None
                            floor_button = None
                        elif len(stage_result) == 5:
                            players, key_obj, door_obj, platforms, moving_platforms = stage_result
                            spike = None
                            floor_button = None
                            bottom_spike = None
                        else:
                            players, key_obj, door_obj, platforms = stage_result
                            moving_platforms = []
                            spike = None
                            floor_button = None
                            bottom_spike = None
                        # 상호작용 상태 초기화
                        active_players = players[:selected_player_count]
                        door_obj.reset_interactions(active_players)
                        slider_orig_positions = restore_slider_positions(
                            sound_slider, sfx_slider, slider_orig_positions
                        )
                        state = STATE_GAME  # 게임 재개
                    if buttons["back_to_menu"].handle_event(event):
                        slider_orig_positions = restore_slider_positions(
                            sound_slider, sfx_slider, slider_orig_positions
                        )
                        state = STATE_MENU  # 메뉴로 돌아가기
                    if buttons["quit_game"].handle_event(event):
                        pause_quit_confirm = True  # Quit Game 확인 팝업 표시

            elif state == STATE_CLEAR:
                if buttons["next"].handle_event(event):
                    state = STATE_STAGE_SELECT

        screen.fill(BACKGROUND_COLOR)

        if state == STATE_MAIN:
            # 잔디밭 배경
            draw_grass_background(screen)
            # 큰 제목 표시
            title_text = "DUMB N DUMBERS"
            title_y = HEIGHT // 2 - 100
            draw_text_center(screen, title_text, title_font, PICO_TEXT_COLOR, WIDTH // 2, title_y)
            # 제목 밑줄 (같은 색상, 두껍고 둥근 모서리)
            title_surface = title_font.render(title_text, True, PICO_TEXT_COLOR)
            title_width = title_surface.get_width()
            underline_y = title_y + title_surface.get_height() + 5
            underline_thickness = 8
            underline_x = WIDTH // 2 - title_width // 2
            # 둥근 모서리를 가진 밑줄 그리기
            underline_rect = pygame.Rect(underline_x, underline_y - underline_thickness // 2, 
                                        title_width, underline_thickness)
            pygame.draw.rect(screen, PICO_TEXT_COLOR, underline_rect, border_radius=underline_thickness // 2)
            # 피코파크 스타일: Press Any Buttons 메시지
            draw_text_center(screen, "PRESS ANY BUTTONS", font, PICO_TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 100)

        elif state == STATE_MENU:
            # 잔디밭 배경
            draw_grass_background(screen)
            # 제목과 밑줄 표시
            title_text = "DUMB N DUMBERS"
            title_y = 80
            draw_text_center(screen, title_text, title_font, PICO_TEXT_COLOR, WIDTH // 2, title_y)
            # 제목 밑줄 (같은 색상, 두껍고 둥근 모서리)
            title_surface = title_font.render(title_text, True, PICO_TEXT_COLOR)
            title_width = title_surface.get_width()
            underline_y = title_y + title_surface.get_height() + 5
            underline_thickness = 8
            underline_x = WIDTH // 2 - title_width // 2
            # 둥근 모서리를 가진 밑줄 그리기
            underline_rect = pygame.Rect(underline_x, underline_y - underline_thickness // 2, 
                                        title_width, underline_thickness)
            pygame.draw.rect(screen, PICO_TEXT_COLOR, underline_rect, border_radius=underline_thickness // 2)
            # 메뉴 화면 디자인 - 배경 직사각형 제거
            # Game Start, Settings, Exit 버튼 (중앙 정렬, 세로 배치, 그림자 효과)
            buttons["game_start"].draw(screen, font, korean_font, shadow=True)
            buttons["settings"].draw(screen, font, korean_font, shadow=True)
            buttons["exit"].draw(screen, font, korean_font, shadow=True)
            
            # Exit 확인 팝업 오버레이 (메뉴 화면 위에 표시)
            if show_exit_confirm:
                draw_confirm_popup(screen, font, korean_font, buttons, "정말 종료하시겠습니까?")

        elif state == STATE_SELECT_PLAYER_COUNT:
            # 잔디밭 배경
            draw_grass_background(screen)
            # 제목 (크게)
            draw_text_center(screen, "Select Number of Player", big_font, PICO_TEXT_COLOR, WIDTH // 2, 80)
            # 숫자와 화살표 버튼 수평 정렬 (중앙 기준)
            number_y = 200
            number_surface = big_font.render(str(selected_player_count), True, PICO_TEXT_COLOR)
            number_height = number_surface.get_height()
            # 숫자와 버튼의 중앙을 맞춤
            button_center_y = number_y + number_height // 2
            buttons["left"].rect.y = button_center_y - buttons["left"].rect.height // 2
            buttons["right"].rect.y = button_center_y - buttons["right"].rect.height // 2
            draw_text_center(screen, str(selected_player_count), big_font, PICO_TEXT_COLOR, WIDTH // 2, number_y)
            buttons["left"].draw(screen, font)
            buttons["right"].draw(screen, font)
            buttons["next_to_customize"].draw(screen, font)
        
        elif state == STATE_CUSTOMIZE_PLAYERS:
            # 잔디밭 배경
            draw_grass_background(screen)
            
            # 플레이어 박스들 그리기
            box_width = 250
            box_height = 300
            box_spacing = 30
            total_width = selected_player_count * box_width + (selected_player_count - 1) * box_spacing
            start_x = (WIDTH - total_width) // 2
            box_y = 150
            
            for i in range(selected_player_count):
                box_x = start_x + i * (box_width + box_spacing)
                
                # 박스 배경
                box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
                pygame.draw.rect(screen, (240, 240, 240), box_rect)
                pygame.draw.rect(screen, (200, 200, 200), box_rect, 3)
                
                # 플레이어 이름 (맨 위)
                name_y = box_y + 20
                if editing_player_name == i:
                    # 편집 중일 때
                    name_text = player_names[i] + "_"
                    name_surface = font.render(name_text, True, PICO_TEXT_COLOR)
                else:
                    name_text = player_names[i]
                    name_surface = font.render(name_text, True, PICO_TEXT_COLOR)
                
                screen.blit(name_surface, (box_x + (box_width - name_surface.get_width()) // 2, name_y))
                
                # 캐릭터 (중간)
                char_size = 60
                char_x = box_x + (box_width - char_size) // 2
                char_y = box_y + 80
                char_rect = pygame.Rect(char_x, char_y, char_size, char_size)
                pygame.draw.rect(screen, player_colors[i], char_rect)
                pygame.draw.rect(screen, (0, 0, 0), char_rect, 2)
                
                # 색상 선택 버튼 (캐릭터 밑) - 버튼 가로 늘리기
                color_btn_y = char_y + char_size + 20
                color_btn_width = box_width - 40  # 더 넓게
                color_btn_rect = pygame.Rect(box_x + 20, color_btn_y, color_btn_width, 40)
                pygame.draw.rect(screen, player_colors[i], color_btn_rect)
                pygame.draw.rect(screen, (0, 0, 0), color_btn_rect, 2)
                color_text = font.render("Change Color", True, (255, 255, 255))
                screen.blit(color_text, (box_x + (box_width - color_text.get_width()) // 2, color_btn_y + 10))
            
            # 색상 선택 팝업
            if showing_color_picker is not None:
                picker_x = WIDTH // 2 - 200
                floor_height = 120
                floor_y = HEIGHT - floor_height
                # 팝업을 바닥 위에 여백을 두고 배치
                picker_y = floor_y - 350 - 40  # 바닥에서 40픽셀 위로
                picker_rect = pygame.Rect(picker_x, picker_y, 400, 350)  # 높이 증가
                pygame.draw.rect(screen, (250, 250, 250), picker_rect)
                pygame.draw.rect(screen, (0, 0, 0), picker_rect, 3)
                
                picker_title = font.render("Select Color", True, (0, 0, 0))
                screen.blit(picker_title, (picker_x + (400 - picker_title.get_width()) // 2, picker_y + 20))
                
                # 색상 버튼들을 팝업 내부에 중심 정렬하여 배치
                # 3x3 그리드, 버튼 크기와 간격 계산
                btn_size = 70
                btn_spacing = 20
                grid_width = 3 * btn_size + 2 * btn_spacing
                grid_height = 3 * btn_size + 2 * btn_spacing
                grid_start_x = picker_x + (400 - grid_width) // 2
                grid_start_y = picker_y + 60  # 제목 아래 여백
                
                for i, color in enumerate(color_picker_colors):
                    btn_x = grid_start_x + (i % 3) * (btn_size + btn_spacing)
                    btn_y = grid_start_y + (i // 3) * (btn_size + btn_spacing)
                    color_btn = pygame.Rect(btn_x, btn_y, btn_size, btn_size)
                    pygame.draw.rect(screen, color, color_btn)
                    pygame.draw.rect(screen, (0, 0, 0), color_btn, 2)
            
            # Select Stage 버튼 (오른쪽 아래, 바닥 위에)
            buttons["select_stage"].draw(screen, font, korean_font)

        elif state == STATE_STAGE_SELECT:
            # 잔디밭 배경
            draw_grass_background(screen)
            # 제목 크게
            draw_text_center(screen, "Select Stage", big_font, PICO_TEXT_COLOR, WIDTH // 2, 80)
            for idx, button in enumerate(stage_buttons):
                stage_num = idx + 1
                # 잠금 상태 확인
                is_locked = stage_num not in unlocked_stages
                
                if is_locked:
                    # 잠금된 스테이지: 회색으로 표시
                    original_color = button.color
                    original_hover = button.hover
                    button.color = (150, 150, 150)
                    button.hover = (150, 150, 150)
                    button.draw(screen, font)
                    button.color = original_color
                    button.hover = original_hover
                    
                    # 자물쇠 아이콘 그리기 (간단한 사각형과 원으로)
                    lock_x = button.rect.x + button.rect.w // 2 - 15
                    lock_y = button.rect.y + button.rect.h // 2 - 10
                    # 자물쇠 본체 (사각형)
                    pygame.draw.rect(screen, (100, 100, 100), (lock_x, lock_y + 8, 30, 20))
                    # 자물쇠 구멍 (원)
                    pygame.draw.circle(screen, (100, 100, 100), (lock_x + 15, lock_y + 8), 8)
                    # 자물쇠 테두리
                    pygame.draw.rect(screen, (80, 80, 80), (lock_x, lock_y + 8, 30, 20), 2)
                    pygame.draw.circle(screen, (80, 80, 80), (lock_x + 15, lock_y + 8), 8, 2)
                else:
                    # 잠금 해제된 스테이지: 정상 표시
                    button.draw(screen, font)

        elif state == STATE_GAME or state == STATE_PAUSE:
            # 선택한 플레이어 수만큼만 계산 (한 번만)
            active_players = players[:selected_player_count]
            
            # 게임 화면 그리기 (Pause일 때도 표시)
            for platform in platforms:
                pygame.draw.rect(screen, (120, 120, 120), platform)

            # 게임 로직 업데이트 (Pause일 때는 업데이트 안 함)
            if state == STATE_GAME:
                keys = pygame.key.get_pressed()
                
                # 4스테이지: 동기화된 플레이어 처리
                if current_stage == 4 and len(active_players) > 0:
                    from entities import SyncedPlayer
                    if isinstance(active_players[0], SyncedPlayer):
                        # 모든 플레이어의 키 입력을 수집
                        all_players_keys = []
                        for i in range(selected_player_count):
                            player_keys = {}
                            # 각 플레이어의 키 매핑
                            if i == 0:  # 플레이어 1: 방향키
                                player_keys = {pygame.K_LEFT: keys[pygame.K_LEFT], pygame.K_RIGHT: keys[pygame.K_RIGHT], 
                                             pygame.K_UP: keys[pygame.K_UP], pygame.K_DOWN: keys[pygame.K_DOWN]}
                            elif i == 1:  # 플레이어 2: WASD
                                player_keys = {pygame.K_a: keys[pygame.K_a], pygame.K_d: keys[pygame.K_d], 
                                             pygame.K_w: keys[pygame.K_w], pygame.K_s: keys[pygame.K_s]}
                            elif i == 2:  # 플레이어 3: IJKL
                                player_keys = {pygame.K_j: keys[pygame.K_j], pygame.K_l: keys[pygame.K_l], 
                                             pygame.K_i: keys[pygame.K_i], pygame.K_k: keys[pygame.K_k]}
                            all_players_keys.append(player_keys)
                        
                        # 움직이는 발판을 플랫폼으로 추가
                        all_platforms = platforms + [p.rect() for p in moving_platforms]
                        active_players[0].update(keys, platforms, all_platforms, all_players_keys)
                        
                        # 움직이는 발판 업데이트
                        for platform in moving_platforms:
                            platform.update()
                else:
                    # 일반 플레이어 처리
                    all_platforms = platforms.copy()
                    
                    # 움직이는 발판도 플랫폼으로 추가
                    if current_stage == 4:
                        for platform in moving_platforms:
                            all_platforms.append(platform.rect())
                    
                    # 플레이어 간 충돌 처리를 위해 다른 플레이어 리스트 전달
                    for i, player in enumerate(active_players):
                        other_players = [p for j, p in enumerate(active_players) if j != i]
                        player.update(keys, all_platforms, other_players)
                    
                    # 움직이는 발판 업데이트
                    if current_stage == 4:
                        for platform in moving_platforms:
                            platform.update()
                
                key_obj.update(active_players)
                door_obj.update(active_players)
                
                # 3스테이지: 가시 충돌 체크 및 버튼 처리
                if current_stage == 3 and spike is not None:
                    # 가시 충돌 체크 (게임 오버)
                    if spike.check_collision(active_players):
                        # 게임 오버: 스테이지 리셋
                        stage_result = create_stage_objects(current_stage, player_colors)
                        players, key_obj, door_obj, platforms, moving_platforms, spike, floor_button = stage_result
                        active_players = players[:selected_player_count]
                        door_obj.reset_interactions(active_players)
                    
                    # 버튼 업데이트
                    if floor_button is not None and floor_button.update(active_players):
                        # 버튼이 눌리면 바닥 생성 (뚫려있는 곳 매꾸기)
                        gap_platform = pygame.Rect(400, 580, 160, 60)  # 400~560 사이
                        platforms.append(gap_platform)
                
                # 4스테이지: 하단 가시 충돌 체크
                if current_stage == 4 and bottom_spike is not None:
                    # 가시 충돌 체크 (게임 오버)
                    if bottom_spike.check_collision(active_players):
                        # 게임 오버: 스테이지 리셋
                        stage_result = create_stage_objects(current_stage, player_colors)
                        players, key_obj, door_obj, platforms, moving_platforms, bottom_spike = stage_result
                        active_players = players[:selected_player_count]
                        door_obj.reset_interactions(active_players)
                
                # 문과의 상호작용 체크 (지속적으로)
                door_obj.check_interaction(active_players, keys)
                
                # 열쇠가 수집되었는지 확인
                any_has_key = any(p.has_key for p in active_players)
                if key_obj.collected and not any_has_key:
                    key_obj.attached_to_player = False
                
                # 모든 플레이어가 문과 상호작용했는지 확인
                if door_obj.all_players_interacted(active_players):
                    state = STATE_CLEAR
                    # 다음 스테이지 준비를 위해 상호작용 상태 초기화
                    door_obj.reset_interactions(active_players)
                    # 다음 스테이지 잠금 해제
                    next_stage = current_stage + 1
                    if next_stage <= MAX_STAGE and next_stage not in unlocked_stages:
                        unlocked_stages.append(next_stage)
                elif door_obj.open:
                    # 문이 열려있고 일부 플레이어만 상호작용한 경우 힌트 표시
                    door_rect = door_obj.rect()
                    players_at_door = [p for p in active_players if door_rect.colliderect(p.rect())]
                    if players_at_door:
                        interacted_count = sum(1 for p in active_players if p.interacted_with_door)
                        total_count = len(active_players)
                        hint_text = f"Press \"Down keys\" to enter ({interacted_count}/{total_count})"
                        hint = font.render(hint_text, True, PICO_TEXT_COLOR)
                        screen.blit(hint, (door_obj.x - 250, door_obj.y - 60))
            # 움직이는 발판 렌더링
            if current_stage == 4:
                for platform in moving_platforms:
                    platform.draw(screen)
            
            # 3스테이지: 가시와 버튼 렌더링
            if current_stage == 3:
                if spike is not None and (floor_button is None or not floor_button.pressed):
                    spike.draw(screen)
                if floor_button is not None:
                    floor_button.draw(screen, font)
            
            # 4스테이지: 하단 가시 렌더링
            if current_stage == 4 and bottom_spike is not None:
                bottom_spike.draw(screen)
            
            # 플레이어 렌더링 (문 안으로 들어간 플레이어는 먼저 그리기)
            for player in active_players:
                if player.entered_door:
                    player.draw(screen)
            for player in active_players:
                if not player.entered_door:
                    player.draw(screen)
            key_obj.draw(screen)
            door_obj.draw(screen, font)
            
            # 1스테이지: 조작키 설명 표시
            if current_stage == 1:
                controls_text = [
                    "Player 1: Arrow Keys (↑↓←→)",
                    "Player 2: WASD (W/A/S/D)",
                    "Player 3: IJKL (I/J/K/L)"
                ]
                y_offset = 50
                for i, text in enumerate(controls_text):
                    if i < selected_player_count:
                        control_label = font.render(text, True, PICO_TEXT_COLOR)
                        screen.blit(control_label, (10, y_offset + i * 30))
            
            # 4스테이지: 동기화 메시지 표시
            if current_stage == 4:
                sync_message = "All players must input the same action to move!"
                sync_label = font.render(sync_message, True, PICO_TEXT_COLOR)
                # 화면 상단 중앙에 표시
                message_x = (WIDTH - sync_label.get_width()) // 2
                screen.blit(sync_label, (message_x, 50))

            stage_label = font.render(f"Stage {current_stage}", True, PICO_TEXT_COLOR)
            screen.blit(stage_label, (WIDTH - stage_label.get_width() - 12, 12))
            
            # Pause 창이면 오버레이 표시
            if state == STATE_PAUSE:
                # 반투명 배경 오버레이
                overlay = create_overlay(WIDTH, HEIGHT, 180)
                screen.blit(overlay, (0, 0))
                
                # Pause 창 크기와 위치 (화면 중앙, 상대적 위치) - 더 넓게
                panel_width = 760
                panel_height = 650  # 버튼 4개를 위해 높이 증가
                panel_x = (WIDTH - panel_width) // 2
                panel_y = (HEIGHT - panel_height) // 2
                
                pause_panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                pygame.draw.rect(screen, (240, 240, 240), pause_panel)
                pygame.draw.rect(screen, (0, 0, 0), pause_panel, 4)
                
                # PAUSE 제목 (상대적 위치)
                title_y = panel_y + 40
                draw_text_center(screen, "PAUSE", big_font, PICO_TEXT_COLOR, WIDTH // 2, title_y)
                
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
                
                # 슬라이더 그리기 (중복 코드 최적화)
                slider_configs = [
                    ("Background Sound Volume", sound_slider, panel_y + label_y_offset),
                    ("Effect Sound Volume", sfx_slider, panel_y + label_y_offset + 70),
                ]
                
                for label_text, slider, label_y in slider_configs:
                    label = font.render(label_text, True, PICO_TEXT_COLOR)
                    screen.blit(label, (label_start_x, label_y))
                    
                    slider_y = label_y + 5
                    slider.x = slider_x
                    slider.y = slider_y
                    slider.w = slider_width
                    slider.handle_x = slider.x + slider.w * slider.value
                    slider.draw(screen)
                
                    val = int(slider.value * 10)
                    num = font.render(str(val), True, PICO_TEXT_COLOR)
                    num_height = num.get_height()
                    screen.blit(num, (num_x, slider_y + 4 - num_height // 2))
                
                # Pause 창 버튼들 (상대적 위치) - 더 넓게
                button_width = 420
                button_height = 70
                button_x = (WIDTH - button_width) // 2
                button_spacing = 85
                button_start_y = panel_y + label_y_offset + 150
                
                # 버튼 위치 업데이트
                pause_buttons = ["resume", "reset_stage", "back_to_menu", "quit_game"]
                for idx, btn_key in enumerate(pause_buttons):
                    btn = buttons[btn_key]
                    btn.rect.x = button_x
                    btn.rect.y = button_start_y + button_spacing * idx
                    btn.rect.width = button_width
                    btn.rect.height = button_height
                
                for btn_key in pause_buttons:
                    buttons[btn_key].draw(screen, font, korean_font)
                
                # Quit Game 확인 팝업 (Pause 창 위에 표시)
                if pause_quit_confirm:
                    # 더 진한 오버레이
                    confirm_overlay = create_overlay(WIDTH, HEIGHT, 150)
                    screen.blit(confirm_overlay, (0, 0))
                    
                    # 확인 팝업 창
                    popup_rect = pygame.Rect(280, 250, 400, 200)
                    pygame.draw.rect(screen, (250, 250, 250), popup_rect)
                    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)
                    
                    draw_text_center(screen, "정말 종료하시겠습니까?", font, PICO_TEXT_COLOR, WIDTH // 2, 290, korean_font)
                    buttons["exit_yes"].draw(screen, font)
                    buttons["exit_no"].draw(screen, font)

        elif state == STATE_CLEAR:
            draw_text_center(screen, "STAGE CLEAR!", big_font, PICO_TEXT_COLOR, WIDTH // 2, 140)
            buttons["next"].draw(screen, font)

        elif state == STATE_SETTINGS:
            # 잔디밭 배경
            draw_grass_background(screen)
            # Settings 창으로 들어올 때 슬라이더 위치 복원
            slider_orig_positions = restore_slider_positions(
                sound_slider, sfx_slider, slider_orig_positions
            )
            
            # Settings 창 (메뉴에서 들어온 설정)
            draw_text_center(screen, "SETTINGS", big_font, PICO_TEXT_COLOR, WIDTH // 2, 80)
            sound_label = font.render("Background Sound Volume", True, PICO_TEXT_COLOR)
            sfx_label = font.render("Effect Sound Volume", True, PICO_TEXT_COLOR)
            screen.blit(sound_label, (220, 206))
            screen.blit(sfx_label, (220, 306))

            sound_slider.draw(screen)
            sfx_slider.draw(screen)
            sound_val = int(sound_slider.value * 10)
            sfx_val = int(sfx_slider.value * 10)
            sound_num = font.render(str(sound_val), True, PICO_TEXT_COLOR)
            sfx_num = font.render(str(sfx_val), True, PICO_TEXT_COLOR)
            screen.blit(sound_num, (700, 226))
            screen.blit(sfx_num, (700, 326))

            buttons["go_back"].draw(screen, font, korean_font)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

