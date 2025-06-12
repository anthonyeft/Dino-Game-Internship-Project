import pygame
from typing import List, Tuple, Any  # Added type hints inspired by Mr. Evan's very clean code
from sound_utils import play_hover_sound, play_click_sound

# Global hover state tracking - simple variables
hover_played_play = False
hover_played_settings = False
hover_played_back = False
hover_played_restart = False
hover_played_quit = False
hover_played_home = False

# Volume settings
sfx_volume = 0.7  # Sound effects volume (0.0 to 1.0)
music_volume = 0.5  # Music volume (0.0 to 1.0)

def handle_button(
    screen: pygame.Surface, 
    text: str, 
    center_pos: tuple[int, int], 
    mouse_pos: tuple[int, int], 
    clicked: bool, 
    button_key: str, 
    font: pygame.font.Font, 
    color: str = "orange", 
    hover_color: str = "yellow"
) -> bool:
    """Handle button rendering, hover effects, and click detection. Returns True if clicked."""
    global hover_played_play, hover_played_settings, hover_played_back, hover_played_restart, hover_played_quit, hover_played_home
    
    text_surf = font.render(text, True, "black")
    text_rect = text_surf.get_rect(center=center_pos)
    button_box = text_rect.inflate(40, 18)
    
    if button_box.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, button_box, border_radius=6)
        # Check which button and play sound if not already played
        if button_key == "play" and not hover_played_play:
            play_hover_sound()
            hover_played_play = True
        elif button_key == "settings" and not hover_played_settings:
            play_hover_sound()
            hover_played_settings = True
        elif button_key == "back" and not hover_played_back:
            play_hover_sound()
            hover_played_back = True
        elif button_key == "restart" and not hover_played_restart:
            play_hover_sound()
            hover_played_restart = True
        elif button_key == "quit" and not hover_played_quit:
            play_hover_sound()
            hover_played_quit = True
        elif button_key == "home" and not hover_played_home:
            play_hover_sound()
            hover_played_home = True
            
        if clicked:
            play_click_sound()
            return True
    else:
        pygame.draw.rect(screen, color, button_box, border_radius=6)
        
        # Reset hover state when not hovering
        if button_key == "play":
            hover_played_play = False
        elif button_key == "settings":
            hover_played_settings = False
        elif button_key == "back":
            hover_played_back = False
        elif button_key == "restart":
            hover_played_restart = False
        elif button_key == "quit":
            hover_played_quit = False
        elif button_key == "home":
            hover_played_home = False
    
    screen.blit(text_surf, text_rect)
    return False

def handle_slider(
    screen: pygame.Surface, 
    label: str, 
    value: float, 
    pos: tuple[int, int], 
    mouse_pos: tuple[int, int], 
    mouse_pressed: bool, 
    font: pygame.font.Font
) -> float:
    """Handle slider rendering and interaction. Returns new value (0.0 to 1.0)."""
    slider_width = 200
    slider_height = 20
    knob_width = 16
    
    # Draw label
    label_surf = font.render(label, True, "white")
    screen.blit(label_surf, (pos[0] - 100, pos[1] - 30))
    
    # Draw slider track
    slider_rect = pygame.Rect(pos[0], pos[1], slider_width, slider_height)
    pygame.draw.rect(screen, "gray", slider_rect, border_radius=10)
    
    # Calculate knob position
    knob_x = pos[0] + (value * (slider_width - knob_width))
    knob_rect = pygame.Rect(knob_x, pos[1] - 2, knob_width, slider_height + 4)
    
    # Handle interaction
    new_value = value
    if slider_rect.collidepoint(mouse_pos) and mouse_pressed:
        # Calculate new value based on mouse position
        relative_x = mouse_pos[0] - pos[0]
        new_value = max(0.0, min(1.0, relative_x / slider_width))
    
    # Draw knob
    knob_color = "yellow" if knob_rect.collidepoint(mouse_pos) else "orange"
    pygame.draw.rect(screen, knob_color, knob_rect, border_radius=8)
    
    # Draw value percentage
    percentage_text = f"{int(new_value * 100)}%"
    percentage_surf = font.render(percentage_text, True, "white")
    screen.blit(percentage_surf, (pos[0] + slider_width + 20, pos[1]))
    
    return new_value

def start_screen(
    screen: pygame.Surface,
    walk_frames: List[pygame.Surface],
    events: List[pygame.event.Event],
    walk_frame_idx: int,
    last_walk_frame_time: int,
    walk_anim_delay: int
) -> Tuple[str, int, int]:
    screen.fill((30, 40, 80))  # Dark blue-purple color
    title_font = pygame.font.Font("assets/font/PixeloidMono.ttf", 40)
    title_surf = title_font.render("GANGSTER DINO", True, "white")
    title_rect = title_surf.get_rect(center=(400, 60))
    screen.blit(title_surf, title_rect)

    now = pygame.time.get_ticks()
    if now - last_walk_frame_time > walk_anim_delay:
        walk_frame_idx = (walk_frame_idx + 1) % len(walk_frames)
        last_walk_frame_time = now
    walk_frame = walk_frames[walk_frame_idx]
    walk_rect = walk_frame.get_rect(center=(400, 120))
    screen.blit(walk_frame, walk_rect)

    button_font = pygame.font.Font("assets/font/PixeloidMono.ttf", 28)
    mouse_pos = pygame.mouse.get_pos()
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)

    if handle_button(screen, "PLAY", (400, 250), mouse_pos, clicked, "play", button_font):
        return "game", walk_frame_idx, last_walk_frame_time
    
    if handle_button(screen, "SETTINGS", (400, 320), mouse_pos, clicked, "settings", button_font):
        return "settings", walk_frame_idx, last_walk_frame_time

    return "start", walk_frame_idx, last_walk_frame_time

def settings_screen(
    screen: pygame.Surface,
    events: List[pygame.event.Event]
) -> str:
    global sfx_volume, music_volume
    
    screen.fill((30, 40, 80))  # Dark blue-purple color
    
    # Title
    title_font = pygame.font.Font("assets/font/PixeloidMono.ttf", 32)
    title_surf = title_font.render("SETTINGS", True, "white")
    title_rect = title_surf.get_rect(center=(400, 60))
    screen.blit(title_surf, title_rect)
    
    font = pygame.font.Font("assets/font/PixeloidMono.ttf", 20)
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)
    
    # Volume sliders
    sfx_volume = handle_slider(screen, "Sound Effects", sfx_volume, (300, 150), mouse_pos, mouse_pressed, font)
    music_volume = handle_slider(screen, "Music", music_volume, (300, 220), mouse_pos, mouse_pressed, font)
    
    # Update pygame mixer volumes
    pygame.mixer.music.set_volume(music_volume)
    
    # Back button
    button_font = pygame.font.Font("assets/font/PixeloidMono.ttf", 28)
    if handle_button(screen, "BACK", (400, 350), mouse_pos, clicked, "back", button_font):
        return "start"

    return "settings"

def end_screen(
    screen: pygame.Surface,
    score: int,
    events: List[pygame.event.Event],
    walk_frames: List[pygame.Surface],
    walk_frame_idx: int,
    last_walk_frame_time: int,
    walk_anim_delay: int,
    GAME_FONT: pygame.font.Font,
    SCREEN_FONT: pygame.font.Font
) -> Tuple[Any, int, int]:
    screen.fill((30, 40, 80))  # Dark blue-purple color

    title_surf = SCREEN_FONT.render("GAME OVER", True, "white")
    title_rect = title_surf.get_rect(center=(400, 50))
    screen.blit(title_surf, title_rect)

    score_surf = GAME_FONT.render(f"Score: {score}", True, "white")
    score_rect = score_surf.get_rect(center=(400, 90))
    screen.blit(score_surf, score_rect)

    now = pygame.time.get_ticks()
    if now - last_walk_frame_time > walk_anim_delay:
        walk_frame_idx = (walk_frame_idx + 1) % len(walk_frames)
        last_walk_frame_time = now
    walk_frame = walk_frames[walk_frame_idx]
    walk_rect = walk_frame.get_rect(center=(400, 140))
    screen.blit(walk_frame, walk_rect)

    button_font = pygame.font.Font("assets/font/PixeloidMono.ttf", 28)
    mouse_pos = pygame.mouse.get_pos()
    clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)

    if handle_button(screen, "RESTART", (400, 250), mouse_pos, clicked, "restart", button_font):
        return "restart", walk_frame_idx, last_walk_frame_time
    
    if handle_button(screen, "HOME", (330, 320), mouse_pos, clicked, "home", button_font):
        return "home", walk_frame_idx, last_walk_frame_time
    
    if handle_button(screen, "QUIT", (470, 320), mouse_pos, clicked, "quit", button_font):
        return "quit", walk_frame_idx, last_walk_frame_time

    return None, walk_frame_idx, last_walk_frame_time