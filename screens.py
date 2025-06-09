import pygame
from typing import List, Tuple, Any  # Added type hints inspired by Mr. Evan's very clean code

def start_screen(
    screen: pygame.Surface,
    idle_frames: List[pygame.Surface],
    events: List[pygame.event.Event],
    idle_frame_idx: int,
    last_idle_frame_time: int,
    idle_anim_delay: int,
    play_icon: pygame.Surface,
    settings_icon: pygame.Surface
) -> Tuple[str, int, int]:
    screen.fill((20, 30, 60))
    title_font = pygame.font.Font("graphics/font/PixeloidMono.ttf", 40)
    title_surf = title_font.render("GANGSTER DINO", True, "white")
    title_rect = title_surf.get_rect(center=(400, 60))
    screen.blit(title_surf, title_rect)

    now = pygame.time.get_ticks()
    if now - last_idle_frame_time > idle_anim_delay:
        idle_frame_idx = (idle_frame_idx + 1) % len(idle_frames)
        last_idle_frame_time = now
    idle_frame = idle_frames[idle_frame_idx]
    idle_rect = idle_frame.get_rect(center=(400, 120))
    screen.blit(idle_frame, idle_rect)

    play_rect = play_icon.get_rect(center=(360, 300))
    settings_rect = settings_icon.get_rect(center=(440, 300))

    screen.blit(play_icon, play_rect)
    screen.blit(settings_icon, settings_rect)

    mouse_pos = pygame.mouse.get_pos()
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)

    if play_rect.collidepoint(mouse_pos) and clicked:
        return "game", idle_frame_idx, last_idle_frame_time
    elif settings_rect.collidepoint(mouse_pos) and clicked:
        return "settings", idle_frame_idx, last_idle_frame_time

    return "start", idle_frame_idx, last_idle_frame_time

def settings_screen(
    screen: pygame.Surface,
    events: List[pygame.event.Event]
) -> str:
    screen.fill((30, 30, 40))
    font = pygame.font.Font("graphics/font/PixeloidMono.ttf", 28)
    text_surf = font.render("Settings (coming soon)", True, "white")
    text_rect = text_surf.get_rect(center=(400, 180))
    screen.blit(text_surf, text_rect)

    back_surf = font.render("BACK", True, "black")
    back_rect = back_surf.get_rect(center=(400, 320))
    back_box = back_rect.inflate(40, 18)

    mouse_pos = pygame.mouse.get_pos()
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)

    if back_box.collidepoint(mouse_pos):
        pygame.draw.rect(screen, "yellow", back_box, border_radius=6)
        if clicked:
            return "start"
    else:
        pygame.draw.rect(screen, "orange", back_box, border_radius=6)

    screen.blit(back_surf, back_rect)
    return "settings"

def end_screen(
    screen: pygame.Surface,
    score: int,
    events: List[pygame.event.Event],
    idle_frames: List[pygame.Surface],
    idle_frame_idx: int,
    last_idle_frame_time: int,
    idle_anim_delay: int,
    GAME_FONT: pygame.font.Font,
    SCREEN_FONT: pygame.font.Font
) -> Tuple[Any, int, int]:
    screen.fill((50, 60, 100))

    title_surf = SCREEN_FONT.render("GAME OVER", True, "white")
    title_rect = title_surf.get_rect(center=(400, 50))
    screen.blit(title_surf, title_rect)

    score_surf = GAME_FONT.render(f"Score: {score}", True, "white")
    score_rect = score_surf.get_rect(center=(400, 90))
    screen.blit(score_surf, score_rect)

    now = pygame.time.get_ticks()
    if now - last_idle_frame_time > idle_anim_delay:
        idle_frame_idx = (idle_frame_idx + 1) % len(idle_frames)
        last_idle_frame_time = now
    idle_frame = idle_frames[idle_frame_idx]
    idle_rect = idle_frame.get_rect(center=(400, 140))
    screen.blit(idle_frame, idle_rect)

    button_font = pygame.font.Font("graphics/font/PixeloidMono.ttf", 28)

    restart_surf = button_font.render("RESTART", True, "black")
    restart_rect = restart_surf.get_rect(center=(400, 270))
    restart_box = restart_rect.inflate(40, 18)

    quit_surf = button_font.render("QUIT", True, "black")
    quit_rect = quit_surf.get_rect(center=(400, 340))
    quit_box = quit_rect.inflate(40, 18)

    mouse_pos = pygame.mouse.get_pos()
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)

    if restart_box.collidepoint(mouse_pos):
        pygame.draw.rect(screen, "yellow", restart_box, border_radius=6)
        if clicked:
            return "restart", idle_frame_idx, last_idle_frame_time
    else:
        pygame.draw.rect(screen, "orange", restart_box, border_radius=6)
    screen.blit(restart_surf, restart_rect)

    if quit_box.collidepoint(mouse_pos):
        pygame.draw.rect(screen, "yellow", quit_box, border_radius=6)
        if clicked:
            return "quit", idle_frame_idx, last_idle_frame_time
    else:
        pygame.draw.rect(screen, "orange", quit_box, border_radius=6)
    screen.blit(quit_surf, quit_rect)

    return None, idle_frame_idx, last_idle_frame_time