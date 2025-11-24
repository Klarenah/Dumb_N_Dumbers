import sys
import pygame

from config import WIDTH, HEIGHT, TITLE, FPS, BACKGROUND_COLOR, MAX_STAGE
from stages import create_stage_objects
from ui import Button, Slider, draw_text_center


STATE_MAIN = "main"
STATE_SELECT_PLAYER = "select_player"
STATE_STAGE_SELECT = "stage_select"
STATE_GAME = "game"
STATE_CLEAR = "clear"
STATE_OPTION = "option"


def create_stage_buttons(total_stages):
    buttons = []
    for i in range(total_stages):
        bx = 150 + (i % 3) * 240
        by = 200 + (i // 3) * 180
        buttons.append(Button(bx, by, 180, 110, f"Stage {i + 1}"))
    return buttons


def initialize_buttons():
    return {
        "play": Button(380, 300, 200, 70, "PLAY"),
        "left": Button(300, 200, 60, 60, "<"),
        "right": Button(600, 200, 60, 60, ">"),
        "start": Button(380, 360, 200, 70, "START"),
        "reset": Button(360, 440, 220, 60, "RESET", color=(255, 200, 200), hover=(255, 220, 220)),
        "exit": Button(360, 520, 220, 60, "EXIT", color=(255, 200, 200), hover=(255, 220, 220)),
        "next": Button(360, 420, 220, 70, "NEXT", color=(200, 255, 200), hover=(180, 255, 180)),
    }


def initialize_sliders():
    return Slider(320, 240, 360, start=0.6), Slider(320, 340, 360, start=0.5)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)

    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 64)
    clock = pygame.time.Clock()

    buttons = initialize_buttons()
    stage_buttons = create_stage_buttons(MAX_STAGE)
    sound_slider, sfx_slider = initialize_sliders()

    state = STATE_MAIN
    selected_player_count = 1
    current_stage = 1
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
                        state = STATE_OPTION
                    elif state == STATE_OPTION:
                        state = STATE_GAME
                    else:
                        state = STATE_MAIN
                elif event.key == pygame.K_DOWN and state == STATE_GAME:
                    if door_obj.player_can_enter(player):
                        state = STATE_CLEAR

            if state == STATE_OPTION:
                sound_slider.handle_event(event)
                sfx_slider.handle_event(event)

            if state == STATE_MAIN:
                if buttons["play"].handle_event(event):
                    state = STATE_SELECT_PLAYER

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

            elif state == STATE_OPTION:
                if buttons["reset"].handle_event(event):
                    player, key_obj, door_obj, platforms = create_stage_objects(current_stage)
                    state = STATE_GAME
                if buttons["exit"].handle_event(event):
                    state = STATE_MAIN

            elif state == STATE_CLEAR:
                if buttons["next"].handle_event(event):
                    state = STATE_STAGE_SELECT

        screen.fill(BACKGROUND_COLOR)

        if state == STATE_MAIN:
            draw_text_center(screen, "DUMB N DUMBERS", big_font, (20, 20, 20), WIDTH // 2, 120)
            buttons["play"].draw(screen, font)
            draw_text_center(screen, "Press PLAY to continue", font, (50, 50, 50), WIDTH // 2, 220)

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

        elif state == STATE_GAME:
            for platform in platforms:
                pygame.draw.rect(screen, (150, 150, 150), platform)

            keys = pygame.key.get_pressed()
            player.update(keys, platforms)
            key_obj.update(player)
            door_obj.update(player)

            if key_obj.collected and not player.has_key:
                key_obj.attached_to_player = False

            for platform in platforms:
                pygame.draw.rect(screen, (120, 120, 120), platform)
            player.draw(screen)
            key_obj.draw(screen)
            door_obj.draw(screen, font)

            if door_obj.player_can_enter(player):
                hint = font.render("Press(DOWN) key to enter", True, (0, 0, 0))
                screen.blit(hint, (door_obj.x - 60, door_obj.y - 40))

            stage_label = font.render(f"Stage {current_stage}", True, (0, 0, 0))
            screen.blit(stage_label, (WIDTH - stage_label.get_width() - 12, 12))

        elif state == STATE_CLEAR:
            draw_text_center(screen, "STAGE CLEAR!", big_font, (10, 10, 10), WIDTH // 2, 140)
            buttons["next"].draw(screen, font)

        elif state == STATE_OPTION:
            draw_text_center(screen, "OPTION", font, (0, 0, 0), WIDTH // 2, 60)
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

            buttons["reset"].draw(screen, font)
            buttons["exit"].draw(screen, font)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
