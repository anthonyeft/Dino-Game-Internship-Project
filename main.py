import pygame

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True

# Game state
is_playing = True
score = 0
GROUND_Y = 360
JUMP_GRAVITY_START_SPEED = -20
players_gravity_speed = 0
is_jumping = False

scroll_speed = 5.0
speed_increment = 0.003
speed_increment_decay = 0.00000056 # Increment decay so the game doesn't get too hard - kind of like subway surfers

# Level assets
raw_road_img = pygame.image.load("graphics/level/road.png").convert_alpha()
raw_sky_img = pygame.image.load("graphics/level/sky.png").convert()
raw_wall1_img = pygame.image.load("graphics/level/wall1.png").convert_alpha()
raw_back_img = pygame.image.load("graphics/level/back.png").convert_alpha()

SKY_SURF = pygame.transform.scale(raw_sky_img, (800, 400))
GROUND_SURF = pygame.transform.scale(raw_road_img, (800, 400))
WALL1_SURF = pygame.transform.scale(raw_wall1_img, (800, 400))
BACK_SURF = pygame.transform.scale(raw_back_img, (800, 400))

game_font = pygame.font.Font("graphics/font/PixeloidMono.ttf", 24) # Use custom font
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Enemy egg
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

# Load sprite sheets
NUM_FRAMES = 10
def load_animation(path):
    sheet = pygame.image.load(path).convert_alpha()
    frame_w = sheet.get_width() // NUM_FRAMES # Get the width of each frame
    frame_h = sheet.get_height()
    return [sheet.subsurface((i * frame_w, 0, frame_w, frame_h)) for i in range(NUM_FRAMES)] # Luh list comprehension

run_frames = load_animation("graphics/player/Run.png") # Load the run sheet
jump_frames = load_animation("graphics/player/Jump.png") # Load the jump sheet

# Animation state
frame_idx = 0 # keep track of which frame we're on
last_frame_time = pygame.time.get_ticks() # Keep track of what time the last frame was, so we can judge whether to blit the next one
run_speed = 40 # ms per frame
jump_speed = 50 # ms per frame
player_surf = run_frames[0] # Get an initial surface
player_rect = player_surf.get_rect(midbottom=(80, GROUND_Y)) # Position the player

# Hitbox config - relative to larger frame since sprite does not take up the full size
HITBOX_OFFSET_X = 32
HITBOX_OFFSET_Y = 60
HITBOX_WIDTH = 40
HITBOX_HEIGHT = 68

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= GROUND_Y:
                players_gravity_speed = JUMP_GRAVITY_START_SPEED
                is_jumping = True
                frame_idx = 0  # restart jump animation
                last_frame_time = pygame.time.get_ticks()

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800

    if is_playing:
        # Display level assets
        screen.fill("black")
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(BACK_SURF, (0, 0))
        screen.blit(WALL1_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, 0))

        # Score logic and display
        score += 1  # simple increment each frame
        score_text = f"{score:05d}"  # padded like Dino game
        score_surf = game_font.render(score_text, False, "black")
        score_rect = score_surf.get_rect(topright=(780, 20))  # top-right position
        screen.blit(score_surf, score_rect)

        # Move egg
        egg_rect.x -= scroll_speed
        if egg_rect.right <= 0:
            egg_rect.left = 800
        screen.blit(egg_surf, egg_rect)

        # Gravity
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
            is_jumping = False

        # Animation handling
        now = pygame.time.get_ticks()
        if is_jumping:
            if now - last_frame_time > jump_speed and frame_idx < len(jump_frames) - 1:
                frame_idx += 1
                last_frame_time = now
            player_surf = jump_frames[frame_idx]
        else:
            if now - last_frame_time > run_speed:
                frame_idx = (frame_idx + 1) % len(run_frames)
                last_frame_time = now
            player_surf = run_frames[frame_idx]

        screen.blit(player_surf, player_rect)

        # Collision hitbox
        hitbox_rect = pygame.Rect(
            player_rect.left + HITBOX_OFFSET_X,
            player_rect.top + HITBOX_OFFSET_Y,
            HITBOX_WIDTH,
            HITBOX_HEIGHT
        )
        pygame.draw.rect(screen, "red", hitbox_rect, 1)

        if egg_rect.colliderect(hitbox_rect):
            is_playing = False
        
        scroll_speed += speed_increment
        speed_increment = max(speed_increment - speed_increment_decay, 0.0002)  # gradually slows growth to tiny increment

    else:
        screen.fill("black")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
