import pygame

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
pygame.display.set_caption("Gangster Dino Game")

# Game state
running = True
is_playing = True
score = 0
distance_accumulator = 0
GROUND_Y = 365
JUMP_GRAVITY_START_SPEED = -20
BASE_UNIT = 80 # How many pixels per each spatial unit in the game - used for score counting
players_gravity_speed = 0
is_jumping = False
is_shooting = False
shoot_start_time = 0
SHOOT_DELAY = 200  # milliseconds

# Scrolling settings
scroll_speed = 5.0
scroll_offset = 0.0
speed_increment = 0.003
speed_increment_decay = 0.00000056 # Increment decay so the game doesn't get too hard - kind of like subway surfers


# Load high score
HIGH_SCORE_FILE = "highscore.txt"
with open(HIGH_SCORE_FILE, "r") as f:
        high_score = int(f.read())

# Level assets
raw_road_img = pygame.image.load("graphics/level/road.png").convert_alpha()
raw_sky_img = pygame.image.load("graphics/level/sky.png").convert()
raw_buildings_back_img = pygame.image.load("graphics/level/buildings_back.png").convert_alpha()
raw_back_img = pygame.image.load("graphics/level/back.png").convert_alpha()

sky_surf = pygame.transform.scale(raw_sky_img, (800, 400))
ground_surf = pygame.transform.scale(raw_road_img, (800, 400))
buildings_back_surf = pygame.transform.scale(raw_buildings_back_img, (800, 400))
back_surf = pygame.transform.scale(raw_back_img, (800, 400))

# Set up the game font
game_font = pygame.font.Font("graphics/font/PixeloidMono.ttf", 24)
end_screen_font = pygame.font.Font("graphics/font/PixeloidMono.ttf", 36)

# Enemy egg setup
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

# Animation settings and state
frame_idx = 0
last_frame_time = pygame.time.get_ticks()

idle_frame_idx = 0
last_idle_frame_time = pygame.time.get_ticks()
IDLE_ANIM_DELAY = 100 # ms delay between frames for idle animation

# Load sprite sheets
def load_animation(path, num_frames):
    sheet = pygame.image.load(path).convert_alpha()
    frame_w = sheet.get_width() // num_frames
    frame_h = sheet.get_height()
    return [sheet.subsurface((i * frame_w, 0, frame_w, frame_h)) for i in range(num_frames)]

def load_multi_img_animation(path, num_frames):
    return [pygame.image.load(path + str(i) + ".png").convert_alpha() for i in range(1, num_frames + 1)]

# Scale the frames to make the player fit the background better
def scale_frames(frames, factor):
    return [
        pygame.transform.scale(frame, (
            int(frame.get_width() * factor),
            int(frame.get_height() * factor)
        )) for frame in frames
    ]

def display_score(score, high_score):
    score_text = f"HI {high_score}    {score:05d}"
    score_surf = game_font.render(score_text, False, "white")
    score_rect = score_surf.get_rect(topright=(760, 20))
    screen.blit(score_surf, score_rect)

def draw_parallax(surface: pygame.Surface, offset: float, ratio: float):
    scroll = offset * ratio % surface.get_width()
    screen.blit(surface, (-scroll, 0))
    screen.blit(surface, (-scroll + surface.get_width(), 0))

def end_screen(score, events, idle_frame_idx, last_idle_frame_time):
    screen.fill((50, 60, 100))

    title_surf = end_screen_font.render("GAME OVER", True, "white")
    title_rect = title_surf.get_rect(center=(400, 50))
    screen.blit(title_surf, title_rect)

    score_surf = game_font.render(f"Score: {score}", True, "white")
    score_rect = score_surf.get_rect(center=(400, 90))
    screen.blit(score_surf, score_rect)

    now = pygame.time.get_ticks()
    if now - last_idle_frame_time > IDLE_ANIM_DELAY:
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


run_frames = load_animation("graphics/player/Run.png", 10)
jump_frames = load_animation("graphics/player/Jump.png", 10)
idle_frames = load_animation("graphics/player/Idle.png", 7)
shoot_frames = load_animation("graphics/player/Shoot.png", 12)
explosion_frames = load_multi_img_animation("graphics/effects/Explosion_2/", 10)

# Scale up the character so it fits with the background
PLAYER_SCALE = 1.3

run_frames = scale_frames(run_frames, PLAYER_SCALE)
jump_frames = scale_frames(jump_frames, PLAYER_SCALE)
idle_frames = scale_frames(idle_frames, PLAYER_SCALE)
shoot_frames = scale_frames(shoot_frames, PLAYER_SCALE)
explosion_frames = scale_frames(explosion_frames, 0.2)

# player setup
run_speed = 40 # ms delay between frames for running animation
JUMP_SPEED = 50 # ms delay between frames for jumping animation
SHOOT_SPEED = 14 # ms delay between frames for shooting animation (actually smaller than frame time so not necessary)
player_surf = run_frames[0]
player_rect = player_surf.get_rect(midbottom=(80, GROUND_Y))

# Effects setup
EXPLOSION_SPEED = 20  # ms delay between frames for explosion animation
explosion_surf = explosion_frames[0]
explosion_rect = explosion_surf.get_rect(center=(400, 200))

# Explosion state
exploding = False
explosion_frame_idx = 0
explosion_start_time = 0

# Hitbox config - relative to larger frame since sprite does not take up the full size - Scale with player
HITBOX_OFFSET_X = int(34 * PLAYER_SCALE)
HITBOX_OFFSET_Y = int(60 * PLAYER_SCALE)
HITBOX_WIDTH = int(38 * PLAYER_SCALE)
HITBOX_HEIGHT = int(68 * PLAYER_SCALE)

# MAIN GAME LOOP
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= GROUND_Y:
                players_gravity_speed = JUMP_GRAVITY_START_SPEED
                is_jumping = True
                frame_idx = 0
                last_frame_time = pygame.time.get_ticks()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if player_rect.bottom >= GROUND_Y and not is_shooting:
                    frame_idx = 0
                    is_shooting = True
                    shoot_start_time = pygame.time.get_ticks()


    if is_playing:
        screen.fill("black")
        scroll_step = round(scroll_speed)
        scroll_offset += scroll_step

        screen.blit(sky_surf, (0, 0))
        draw_parallax(back_surf, scroll_offset, 0.85)
        draw_parallax(buildings_back_surf, scroll_offset, 0.95)
        draw_parallax(ground_surf, scroll_offset, 1)

        distance_accumulator += scroll_speed
        while distance_accumulator >= BASE_UNIT:
            score += 1
            distance_accumulator -= BASE_UNIT
        display_score(score, high_score)

        egg_rect.x -= scroll_step
        if egg_rect.right <= 0:
            egg_rect.left = 800
        screen.blit(egg_surf, egg_rect)

        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
            is_jumping = False

        now = pygame.time.get_ticks()
        if is_shooting:
            if now - last_frame_time > SHOOT_SPEED and frame_idx < len(jump_frames) - 1:
                frame_idx += 1
                last_frame_time = now
            
            player_surf = shoot_frames[frame_idx]
            
            if now - shoot_start_time >= SHOOT_DELAY:
                explosion_rect.centerx = egg_rect.centerx  # center explosion horizontally on the egg
                explosion_rect.centery = egg_rect.centery - 18 # adjust for explosion centering in the image
                exploding = True
                explosion_frame_idx = 0
                explosion_start_time = now

                egg_rect.left = 800  # Remove egg
                is_shooting = False

            
        elif is_jumping:
            if now - last_frame_time > JUMP_SPEED and frame_idx < len(jump_frames) - 1:
                frame_idx += 1
                last_frame_time = now
            player_surf = jump_frames[frame_idx]
        else:
            if now - last_frame_time > run_speed:
                frame_idx = (frame_idx + 1) % len(run_frames)
                last_frame_time = now
            player_surf = run_frames[frame_idx]

        screen.blit(player_surf, player_rect)

        # play explosion animation if active
        if exploding:
            explosion_rect.x -= scroll_step
            if now - explosion_start_time > EXPLOSION_SPEED:
                explosion_frame_idx += 1
                explosion_start_time = now
            if explosion_frame_idx < len(explosion_frames):
                explosion_surf = explosion_frames[explosion_frame_idx]
                screen.blit(explosion_surf, explosion_rect)
            else:
                exploding = False  # animation done

        hitbox_rect = pygame.Rect(
            player_rect.left + HITBOX_OFFSET_X,
            player_rect.top + HITBOX_OFFSET_Y,
            HITBOX_WIDTH,
            HITBOX_HEIGHT
        )
        pygame.draw.rect(screen, "red", hitbox_rect, 1)

        if egg_rect.colliderect(hitbox_rect):
            is_playing = False

            if score > high_score:
                high_score = score
                with open(HIGH_SCORE_FILE, "w") as f:
                    f.write(str(high_score))

        speed_increment = max(speed_increment - speed_increment_decay, 0.0002)
        scroll_speed += speed_increment
        run_speed -= speed_increment

    else:
        end_screen_state, idle_frame_idx, last_idle_frame_time = end_screen(score, events, idle_frame_idx, last_idle_frame_time)
        if end_screen_state == "quit":
            running = False
        elif end_screen_state == "restart":
            is_playing = True
            score = 0
            distance_accumulator = 0
            players_gravity_speed = 0
            is_jumping = False
            is_shooting = False
            exploding = False
            explosion_frame_idx = 0
            explosion_start_time = 0
            scroll_speed = 5.0
            scroll_offset = 0.0
            speed_increment = 0.003
            run_speed = 40
            egg_rect.left = 800
            frame_idx = 0
            last_frame_time = pygame.time.get_ticks()
            player_rect.midbottom = (80, GROUND_Y)
            player_surf = run_frames[0]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
