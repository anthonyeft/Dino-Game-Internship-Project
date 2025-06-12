# Made by: Bassem Farid, Anthony Efthimiadis
# June 11, 2025
# Commit hash of all tutorial features implemented: b21b4e5e4c80e6fc5adb027b70315392b6450cce

import pygame
import random
# Utility imports
from score_utils import display_score
from image_utils import draw_parallax, scale_to_height, scale_frames
from animation_utils import advance_animation, load_animation, load_multi_img_animation
from car_utils import spawn_car, is_on_car, init_cars, explode_car
from screens import start_screen, settings_screen, end_screen
from ammo_utils import (
    draw_ammo_ui, 
    manage_ammo_pickups, 
    AMMO_ICON_HEIGHT, 
    AMMO_PICKUP_HEIGHT,
)
from sound_utils import (
    load_menu_music, 
    load_game_music, 
    play_shot_sound, 
    play_explosion_sound, 
    play_reload_sound,
    play_death_sound
)


# CONSTANTS & CONFIG

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Ground and physics settings
GROUND_Y_DEFAULT = 365
JUMP_GRAVITY_START_SPEED = -20
WALK_ANIM_DELAY = 100  # ms delay between frames for walk animation
GAME_FONT_PATH = "assets/font/PixeloidMono.ttf"
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
RUN_SPEED_START = 60 # ms delay between frames for running animation
JUMP_SPEED = 50 # ms delay between frames for jumping animation
SHOOT_SPEED = 15 # ms delay between frames for shooting animation
RELOAD_SPEED = 30 # ms delay between frames for reload animation
EXPLOSION_SPEED = 20  # ms delay between frames for explosion animation
DEATH_SPEED = 100  # ms delay between frames for death animation
DEATH_DISPLAY_TIME = 2000  # 2 seconds to display death before end screen

# Hitbox settings
HITBOX_OFFSET_X = int(34 * PLAYER_SCALE)
HITBOX_OFFSET_Y = int(60 * PLAYER_SCALE)
HITBOX_WIDTH = int(38 * PLAYER_SCALE)
HITBOX_HEIGHT = int(68 * PLAYER_SCALE)

# Car settings
CAR_HITBOX_RIGHT_TRIM = 60 # Subtle trim off the back of car hitbox for smoother fall
CAR_MIN_SPACING = 20 + CAR_HITBOX_RIGHT_TRIM
CAR_MAX_SPACING = 800

# Ammo settings - some constants are imported from ammo_utils.py, the rest are defined there

# INITIALIZATION

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Gangster Dino Game")

# Font initialization
GAME_FONT = pygame.font.Font(GAME_FONT_PATH, GAME_FONT_SIZE)
SCREEN_FONT = pygame.font.Font(GAME_FONT_PATH, SCREEN_FONT_SIZE)

# Level asset loading and scaling
raw_road_img = pygame.image.load("assets/level/road.png").convert_alpha()
raw_sky_img = pygame.image.load("assets/level/sky.png").convert()
raw_buildings_back_img = pygame.image.load("assets/level/buildings_back.png").convert_alpha()
raw_back_img = pygame.image.load("assets/level/back.png").convert_alpha()
sky_surf = pygame.transform.scale(raw_sky_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
ground_surf = pygame.transform.scale(raw_road_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
buildings_back_surf = pygame.transform.scale(raw_buildings_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
back_surf = pygame.transform.scale(raw_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and scale car images
car_surfs = [pygame.image.load(f"assets/obstacle/vehicles/{i+1}.png").convert_alpha() for i in range(12)]
car_surfs = [pygame.transform.flip(scale_to_height(x, 100), True, False) for x in car_surfs]  # Maintain aspect ratio

# Active car lists
active_car_surfs = []
active_car_rects = []

# Spawn first batch of cars with random spacing
init_cars(CAR_MIN_SPACING, CAR_MAX_SPACING, car_surfs, active_car_surfs, active_car_rects)

# Animation settings and state
frame_idx = 0
last_frame_time = pygame.time.get_ticks()

walk_frame_idx = 0
last_walk_frame_time = pygame.time.get_ticks()

run_frames = load_animation("assets/player/Run.png", 10)
jump_frames = load_animation("assets/player/Jump.png", 10)
walk_frames = load_animation("assets/player/Walk.png", 10)
shoot_frames = load_animation("assets/player/Shoot.png", 12)
reload_frames = load_animation("assets/player/Reload.png", 6)
death_frames = load_animation("assets/player/Dead.png", 5)
explosion_frames = load_multi_img_animation("assets/effects/Explosion/", 10)

# Scale up the character so it fits with the background
run_frames = scale_frames(run_frames, PLAYER_SCALE)
jump_frames = scale_frames(jump_frames, PLAYER_SCALE)
walk_frames = scale_frames(walk_frames, PLAYER_SCALE)
shoot_frames = scale_frames(shoot_frames, PLAYER_SCALE)
reload_frames = scale_frames(reload_frames, PLAYER_SCALE)
death_frames = scale_frames(death_frames, PLAYER_SCALE)
explosion_frames = scale_frames(explosion_frames, 0.35)

# Ammo icon loading and scaling
raw_ammo_icon = pygame.image.load("assets/powerups/ammo.png").convert_alpha()
ammo_icon = scale_to_height(raw_ammo_icon, AMMO_ICON_HEIGHT)
ammo_pickup_img = scale_to_height(raw_ammo_icon, AMMO_PICKUP_HEIGHT)


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
is_reloading = False
is_dying = False
shoot_start_time = 0
reload_start_time = 0
death_start_time = 0
current_screen = "start"  # possible values: "start", "game", "settings"
current_anim = "run"

def reset_game_state():
    """Reset all game state variables for a new game."""
    global is_playing, score, distance_accumulator, players_gravity_speed, is_jumping
    global is_shooting, is_reloading, is_dying, shoot_start_time, reload_start_time
    global death_start_time, exploding, explosion_frame_idx, explosion_start_time
    global scroll_speed, scroll_offset, run_speed, frame_idx
    global last_frame_time, ground_y, player_rect, player_surf, player_ammo
    
    is_playing = True
    score = 0
    distance_accumulator = 0
    players_gravity_speed = 0
    is_jumping = False
    is_shooting = False
    is_reloading = False
    is_dying = False
    shoot_start_time = 0
    reload_start_time = 0
    death_start_time = 0
    exploding = False
    explosion_frame_idx = 0
    explosion_start_time = 0
    scroll_speed = SCROLL_SPEED_START
    scroll_offset = 0.0
    run_speed = RUN_SPEED_START
    frame_idx = 0
    last_frame_time = pygame.time.get_ticks()
    ground_y = GROUND_Y_DEFAULT
    player_rect.midbottom = (80, ground_y) 
    player_surf = run_frames[0]
    player_ammo = 0
    ammo_pickups.clear()
    init_cars(CAR_MIN_SPACING, CAR_MAX_SPACING, car_surfs, active_car_surfs, active_car_rects)

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

# Ammo state
player_ammo = 0
ammo_pickups = []  # List of rects for ammo pickups

def remove_ammo_under_cars(ammo_pickups: list[pygame.Rect], car_rects: list[pygame.Rect]) -> None:
    """Remove any ammo pickups that are colliding with cars to catch edge cases."""
    ammo_pickups[:] = [pickup for pickup in ammo_pickups 
                       if not any(pickup.colliderect(car_rect) for car_rect in car_rects)]


# MAIN GAME LOOP
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # Handle controls (jumping, shooting)
        elif is_playing and not is_dying:
            # Jumping logic
            if (
                event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_w)  # No more clicking to jump
            ) and player_rect.bottom >= ground_y and not is_jumping:
                frame_idx = 0
                players_gravity_speed = JUMP_GRAVITY_START_SPEED
                is_jumping = True
                last_frame_time = pygame.time.get_ticks()
            # Shooting logic
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if player_rect.bottom >= GROUND_Y_DEFAULT and not is_shooting and player_ammo > 0:
                    frame_idx = 0
                    is_shooting = True
                    shoot_start_time = pygame.time.get_ticks()
                    player_ammo -= 1
                    play_shot_sound()  # Play shooting sound effect

    if current_screen == "start":
        load_menu_music()
        current_screen, walk_frame_idx, last_walk_frame_time = start_screen(
            screen, walk_frames, events, walk_frame_idx,
            last_walk_frame_time, WALK_ANIM_DELAY
        )

    elif current_screen == "settings":
        load_menu_music()
        current_screen = settings_screen(screen, events)

    elif current_screen == "game":
        if is_playing:
            load_game_music()
            # Set custom player hitbox within the frame
            hitbox_rect = pygame.Rect(
                player_rect.left + HITBOX_OFFSET_X,
                player_rect.top + HITBOX_OFFSET_Y,
                HITBOX_WIDTH,
                HITBOX_HEIGHT
            )

            # Background scrolling and drawing
            screen.fill("black")
            # Only scroll if not dying
            if not is_dying:
                scroll_step = round(scroll_speed)  # Round to avoid rendering stutter
                scroll_offset += scroll_step
                distance_accumulator += scroll_step
            else:
                scroll_step = 0  # Stop all scrolling when dying

            # Draw parallax backgrounds
            screen.blit(sky_surf, (0, 0))
            draw_parallax(screen, back_surf, scroll_offset, 0.85)
            draw_parallax(screen, buildings_back_surf, scroll_offset, 0.94)
            draw_parallax(screen, ground_surf, scroll_offset, 0.98)

            # Score logic based on distance traveled (only if not dying)
            if distance_accumulator >= 100 and not is_dying:
                score += 1
                distance_accumulator = 0
            display_score(score, high_score, GAME_FONT, screen)

            # Car logic (only move cars if not dying)
            i = 0
            while i < len(active_car_rects):
                if not is_dying:
                    active_car_rects[i].x -= scroll_step

                # Remove off-screen cars and spawn new ones (only if not dying)
                if active_car_rects[i].right + CAR_HITBOX_RIGHT_TRIM <= 0 and not is_dying:
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
                    continue  # Don't increment i because list shifted left

                screen.blit(active_car_surfs[i], active_car_rects[i])
                i += 1

            # Ammo pickup logic (only if not dying)
            if not is_dying:
                old_ammo = player_ammo
                # Use hitbox_rect instead of player_rect for more accurate collision detection
                player_ammo = manage_ammo_pickups(ammo_pickups, active_car_rects, hitbox_rect, player_ammo, scroll_step)
                
                # Trigger reload animation and sound if ammo was picked up
                if player_ammo > old_ammo and not is_reloading and not is_shooting and not is_jumping:
                    is_reloading = True
                    reload_start_time = pygame.time.get_ticks()
                    frame_idx = 0
                    play_reload_sound()  # Play reload sound effect
                
                # Safety check: remove any ammo that ended up under cars
                remove_ammo_under_cars(ammo_pickups, active_car_rects)
            
            # Draw ammo pickups
            for pickup in ammo_pickups:
                screen.blit(ammo_pickup_img, pickup)

            # Player on car logic (only if not dying)
            ground_y = GROUND_Y_DEFAULT
            if not is_dying:
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
            elif player_rect.bottom < ground_y and not is_dying:
                is_jumping = True

            now = pygame.time.get_ticks()

            # Animation state handling
            new_anim = "death" if is_dying else "shoot" if is_shooting else "jump" if is_jumping else "reload" if is_reloading else "run"
            if new_anim != current_anim:
                frame_idx = 0
                last_frame_time = now
                current_anim = new_anim
                # Cancel reload if jumping, shooting, or dying takes priority
                if current_anim in ["jump", "shoot", "death"] and is_reloading:
                    is_reloading = False
            
            # Player animation logic
            if current_anim == "death":
                frame_idx, last_frame_time = advance_animation(
                    frame_idx, last_frame_time, DEATH_SPEED, death_frames, now, loop=False
                )
                player_surf = death_frames[frame_idx]
                
                # Check if death animation is complete and enough time has passed
                if frame_idx >= len(death_frames) - 1 and now - death_start_time >= DEATH_DISPLAY_TIME:
                    is_playing = False
                    if score > high_score:
                        high_score = score
                        with open(HIGH_SCORE_FILE, "w") as f:
                            f.write(str(high_score))
                
            elif current_anim == "shoot":
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
                    play_explosion_sound()  # Play explosion sound effect
                    is_shooting = False
                
            elif current_anim == "reload":
                frame_idx, last_frame_time = advance_animation(
                    frame_idx, last_frame_time, RELOAD_SPEED, reload_frames, now, loop=False
                )
                player_surf = reload_frames[frame_idx]
                
                # End reload animation when complete
                if frame_idx >= len(reload_frames) - 1:
                    is_reloading = False
                
            elif current_anim == "jump":
                # Only apply gravity if not dying
                if not is_dying:
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
                # Only move explosion with scroll if not dying (scroll stops when dying)
                if not is_dying:
                    explosion_rect.x -= scroll_step
                explosion_frame_idx, explosion_start_time = advance_animation(
                    explosion_frame_idx, explosion_start_time, EXPLOSION_SPEED, explosion_frames, now, loop=False, clamp=False
                )
                if explosion_frame_idx < len(explosion_frames):
                    explosion_surf = explosion_frames[explosion_frame_idx]
                    screen.blit(explosion_surf, explosion_rect)
                else:
                    exploding = False

            # Collision and game over
            if not is_dying:
                for car_rect in active_car_rects:
                    if car_rect.colliderect(hitbox_rect) and not is_on_car(car_rect, hitbox_rect):
                        is_dying = True
                        death_start_time = now
                        frame_idx = 0
                        # Force player to fall to default ground level when dying
                        ground_y = GROUND_Y_DEFAULT
                        player_rect.bottom = GROUND_Y_DEFAULT
                        is_jumping = False
                        players_gravity_speed = 0
                        play_death_sound()
                        break

            # Speed increment difficulty logic (only if not dying)
            if scroll_speed < MAX_SPEED and not is_dying:
                scroll_speed += SPEED_INCREMENT
                run_speed -= SPEED_INCREMENT / 2 # make the run animation faster as speed increases

            # UI: Draw ammo icons in top left
            draw_ammo_ui(screen, ammo_icon, player_ammo)

        else:
            # End screen - play menu music
            load_menu_music()
            end_screen_state, walk_frame_idx, last_walk_frame_time = end_screen(
                screen, score, events, walk_frames, walk_frame_idx, last_walk_frame_time, WALK_ANIM_DELAY, GAME_FONT, SCREEN_FONT
            )
            if end_screen_state == "quit":
                running = False
            elif end_screen_state == "home":
                reset_game_state()
                current_screen = "start"
            elif end_screen_state == "restart":
                reset_game_state()
                current_screen = "game"
                

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
