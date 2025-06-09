# Made by: Bassem Farid, Anthony Efthimiadis
# June 11, 2025
# Note: I added my own features as I implemented tutorial features.
# This version is when I completed all tutorial features. It includes many of my core unique features for the final game.

import pygame
import random
# Utility imports
from score_utils import display_score
from image_utils import draw_parallax, scale_to_height, scale_frames
from animation_utils import advance_animation, load_animation, load_multi_img_animation
from car_utils import spawn_car, is_on_car, init_cars, explode_car
from screens import start_screen, settings_screen, end_screen


# CONSTANTS & CONFIG

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Ground and physics settings
GROUND_Y_DEFAULT = 365
JUMP_GRAVITY_START_SPEED = -20
IDLE_ANIM_DELAY = 100  # ms delay between frames for idle animation
ICON_SIZE = 64
GAME_FONT_PATH = "graphics/font/PixeloidMono.ttf"
GAME_FONT_SIZE = 24
SCREEN_FONT_SIZE = 36

# Scrolling and speed settings
SCROLL_SPEED_START = 5.0
SPEED_INCREMENT = 0.003
MAX_SPEED = 15.0

# High score file
HIGH_SCORE_FILE = "highscore.txt"

# Player and car scaling
PLAYER_SCALE = 1.3
CAR_SCALE = 2.5
RUN_SPEED_START = 60 # ms delay between frames for running animation
JUMP_SPEED = 50 # ms delay between frames for jumping animation
SHOOT_SPEED = 15 # ms delay between frames for shooting animation
EXPLOSION_SPEED = 20  # ms delay between frames for explosion animation

# Hitbox settings
HITBOX_OFFSET_X = int(34 * PLAYER_SCALE)
HITBOX_OFFSET_Y = int(60 * PLAYER_SCALE)
HITBOX_WIDTH = int(38 * PLAYER_SCALE)
HITBOX_HEIGHT = int(68 * PLAYER_SCALE)

# Car settings
CAR_HITBOX_RIGHT_TRIM = 60 # Subtle trim off the back of car hitbox for smoother fall
CAR_MIN_SPACING = 0
CAR_MAX_SPACING = 1400
MAX_CARS_ON_SCREEN = 4


# INITIALIZATION

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Gangster Dino Game")

# Font initialization
GAME_FONT = pygame.font.Font(GAME_FONT_PATH, GAME_FONT_SIZE)
SCREEN_FONT = pygame.font.Font(GAME_FONT_PATH, SCREEN_FONT_SIZE)

# Icon initialization
play_icon = pygame.image.load("graphics/ui/play_icon.png").convert_alpha()
settings_icon = pygame.image.load("graphics/ui/settings_icon.png").convert_alpha()
play_icon = pygame.transform.scale(play_icon, (ICON_SIZE, ICON_SIZE))
settings_icon = pygame.transform.scale(settings_icon, (ICON_SIZE, ICON_SIZE))

# Level asset loading and scaling
raw_road_img = pygame.image.load("graphics/level/road.png").convert_alpha()
raw_sky_img = pygame.image.load("graphics/level/sky.png").convert()
raw_buildings_back_img = pygame.image.load("graphics/level/buildings_back.png").convert_alpha()
raw_back_img = pygame.image.load("graphics/level/back.png").convert_alpha()
sky_surf = pygame.transform.scale(raw_sky_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
ground_surf = pygame.transform.scale(raw_road_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
buildings_back_surf = pygame.transform.scale(raw_buildings_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
back_surf = pygame.transform.scale(raw_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Car setup
CAR_MIN_SPACING = 20 + CAR_HITBOX_RIGHT_TRIM
CAR_MAX_SPACING = 800

# Load and scale car images
car_surfs = [pygame.image.load(f"graphics/obstacle/vehicles/{i+1}.png").convert_alpha() for i in range(12)]
car_surfs = [pygame.transform.flip(scale_to_height(x, 100), True, False) for x in car_surfs]  # Maintain aspect ratio

# Active car lists
active_car_surfs = []
active_car_rects = []

# Spawn first batch of cars with random spacing
init_cars(CAR_MIN_SPACING, CAR_MAX_SPACING, car_surfs, active_car_surfs, active_car_rects)

# Animation settings and state
frame_idx = 0
last_frame_time = pygame.time.get_ticks()

idle_frame_idx = 0
last_idle_frame_time = pygame.time.get_ticks()

run_frames = load_animation("graphics/player/Run.png", 10)
jump_frames = load_animation("graphics/player/Jump.png", 10)
idle_frames = load_animation("graphics/player/Idle.png", 7)
shoot_frames = load_animation("graphics/player/Shoot.png", 12)
explosion_frames = load_multi_img_animation("graphics/effects/Explosion/", 10)

# Scale up the character so it fits with the background
run_frames = scale_frames(run_frames, PLAYER_SCALE)
jump_frames = scale_frames(jump_frames, PLAYER_SCALE)
idle_frames = scale_frames(idle_frames, PLAYER_SCALE)
shoot_frames = scale_frames(shoot_frames, PLAYER_SCALE)
explosion_frames = scale_frames(explosion_frames, 0.35)


# GAME STATE VARIABLES

# Game state
running = True
is_playing = True
score = 0
distance_accumulator = 0
ground_y = GROUND_Y_DEFAULT
players_gravity_speed = 0
is_jumping = False
is_shooting = False
shoot_start_time = 0
current_screen = "start"  # possible values: "start", "game", "settings"
current_anim = "run"

# Scrolling settings
scroll_speed = SCROLL_SPEED_START
scroll_offset = 0.0

# Load high score - using try/except to gitignore further changes to the highscore file.
try:
    with open(HIGH_SCORE_FILE, "r") as f:
        high_score = int(f.read())
except:
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write("0")
    high_score = 0

# Player setup
run_speed = RUN_SPEED_START
player_surf = run_frames[0]
player_rect = player_surf.get_rect(midbottom=(80, ground_y))

# Effects setup
explosion_surf = explosion_frames[0]
explosion_rect = explosion_surf.get_rect(center=(SCREEN_WIDTH // 2, ground_y))

# Explosion state
exploding = False
explosion_frame_idx = 0
explosion_start_time = 0

# MAIN GAME LOOP
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # Handle controls (jumping, shooting)
        elif is_playing:
            # Jumping logic
            if (
                event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_w)
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= ground_y:
                frame_idx = 0
                players_gravity_speed = JUMP_GRAVITY_START_SPEED
                is_jumping = True
                frame_idx = 0
                last_frame_time = pygame.time.get_ticks()

            # Shooting logic
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if player_rect.bottom >= GROUND_Y_DEFAULT and not is_shooting:  # Player can only shoot on the actual floor
                    frame_idx = 0
                    is_shooting = True
                    shoot_start_time = pygame.time.get_ticks()

    if current_screen == "start":
        current_screen, idle_frame_idx, last_idle_frame_time = start_screen(
            screen, idle_frames, events, idle_frame_idx, last_idle_frame_time, IDLE_ANIM_DELAY, play_icon, settings_icon
        )

    elif current_screen == "settings":
        current_screen = settings_screen(screen, events)

    elif current_screen == "game":
        if is_playing:
            # Set custom player hitbox within the frame
            hitbox_rect = pygame.Rect(
                player_rect.left + HITBOX_OFFSET_X,
                player_rect.top + HITBOX_OFFSET_Y,
                HITBOX_WIDTH,
                HITBOX_HEIGHT
            )

            # Background scrolling and drawing
            screen.fill("black")
            scroll_step = round(scroll_speed)  # Round to avoid rendering stutter
            scroll_offset += scroll_step
            distance_accumulator += scroll_step

            # Draw parallax backgrounds
            screen.blit(sky_surf, (0, 0))
            draw_parallax(screen, back_surf, scroll_offset, 0.85)
            draw_parallax(screen, buildings_back_surf, scroll_offset, 0.94)
            draw_parallax(screen, ground_surf, scroll_offset, 0.98)

            # Score logic based on distance traveled
            if distance_accumulator >= 100:
                score += 1
                distance_accumulator = 0
            display_score(score, high_score, GAME_FONT, screen)

            # Car logic
            i = 0
            while i < len(active_car_rects):
                active_car_rects[i].x -= scroll_step

                # Remove off-screen cars and spawn new ones
                if active_car_rects[i].right + CAR_HITBOX_RIGHT_TRIM <= 0:
                    active_car_surfs.pop(i)
                    active_car_rects.pop(i)

                    # Spawn new car at a random distance from the previous one
                    last_x = active_car_rects[-1].right if active_car_rects else SCREEN_WIDTH
                    spawn_car(
                        last_x + random.randint(CAR_MIN_SPACING, CAR_MAX_SPACING),
                        car_surfs,
                        active_car_surfs,
                        active_car_rects,
                        GROUND_Y_DEFAULT,
                        CAR_HITBOX_RIGHT_TRIM
                    )
                    continue  # don't increment i because list shifted left

                screen.blit(active_car_surfs[i], active_car_rects[i])
                i += 1
            
            # Player on car logic
            ground_y = GROUND_Y_DEFAULT
            for car_rect in active_car_rects:
                if is_on_car(car_rect, hitbox_rect) and players_gravity_speed >= 0:
                    player_rect.bottom = car_rect.top
                    players_gravity_speed = 0
                    is_jumping = False
                    ground_y = car_rect.top
                    break  # Player can only be on one car
            
            # Player falling logic
            if player_rect.bottom > ground_y:
                player_rect.bottom = ground_y
                is_jumping = False
            elif player_rect.bottom < ground_y:
                is_jumping = True

            now = pygame.time.get_ticks()

            # Animation state handling
            new_anim = "shoot" if is_shooting else "jump" if is_jumping else "run"
            if new_anim != current_anim:
                frame_idx = 0
                last_frame_time = now
                current_anim = new_anim
            
            # Player animation logic
            if current_anim == "shoot":
                frame_idx, last_frame_time = advance_animation(
                    frame_idx, last_frame_time, SHOOT_SPEED, shoot_frames, now, loop=False
                )
                player_surf = shoot_frames[frame_idx]

                # Trigger explosion when shooting animation shows fire
                if frame_idx >= len(shoot_frames) - 3:
                    # Set explosion state variables
                    exploding = True
                    explosion_frame_idx = 0
                    explosion_start_time = now
                    explode_car(active_car_surfs, active_car_rects, car_surfs, explosion_rect,
                                hitbox_rect, now, CAR_MIN_SPACING, CAR_MAX_SPACING, CAR_HITBOX_RIGHT_TRIM)
                    is_shooting = False
                
            elif current_anim == "jump":
                players_gravity_speed += 1
                player_rect.y += players_gravity_speed

                frame_idx, last_frame_time = advance_animation(
                    frame_idx, last_frame_time, JUMP_SPEED, jump_frames, now, loop=False
                )
                player_surf = jump_frames[frame_idx]

            else:
                frame_idx, last_frame_time = advance_animation(
                    frame_idx, last_frame_time, int(run_speed), run_frames, now, loop=True
                )
                player_surf = run_frames[frame_idx]

            screen.blit(player_surf, player_rect)

            # Explosion animation logic
            if exploding:
                explosion_rect.x -= scroll_step  # Explosion moves with the scroll
                explosion_frame_idx, explosion_start_time = advance_animation(
                    explosion_frame_idx, explosion_start_time, EXPLOSION_SPEED, explosion_frames, now, loop=False, clamp=False
                )
                if explosion_frame_idx < len(explosion_frames):
                    explosion_surf = explosion_frames[explosion_frame_idx]
                    screen.blit(explosion_surf, explosion_rect)
                else:
                    exploding = False

            # Collision and game over
            for car_rect in active_car_rects:
                if car_rect.colliderect(hitbox_rect) and not is_on_car(car_rect, hitbox_rect):
                    is_playing = False
                    if score > high_score:
                        high_score = score
                        with open(HIGH_SCORE_FILE, "w") as f:
                            f.write(str(high_score))
                    break

            # Speed increment difficulty logic
            if scroll_speed < MAX_SPEED:
                scroll_speed += SPEED_INCREMENT
                run_speed -= SPEED_INCREMENT / 2 # make the run animation faster as speed increases

        else:
            # End screen
            end_screen_state, idle_frame_idx, last_idle_frame_time = end_screen(
                screen, score, events, idle_frames, idle_frame_idx, last_idle_frame_time, IDLE_ANIM_DELAY, GAME_FONT, SCREEN_FONT
            )
            if end_screen_state == "quit":
                running = False
            elif end_screen_state == "restart":
                # Reset all game state variables for a new game
                is_playing = True
                current_screen = "game"
                score = 0
                distance_accumulator = 0
                players_gravity_speed = 0
                is_jumping = False
                is_shooting = False
                shoot_start_time = 0
                exploding = False
                explosion_frame_idx = 0
                explosion_start_time = 0
                scroll_speed = SCROLL_SPEED_START
                scroll_offset = 0.0
                run_speed = RUN_SPEED_START
                frame_idx = 0
                last_frame_time = pygame.time.get_ticks()
                player_rect.midbottom = (80, ground_y)
                player_surf = run_frames[0]
                ground_y = GROUND_Y_DEFAULT
                init_cars(CAR_MIN_SPACING, CAR_MAX_SPACING, car_surfs, active_car_surfs, active_car_rects)
                

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
