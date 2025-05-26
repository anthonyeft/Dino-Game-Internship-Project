import pygame

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True

# Game state variables
is_playing = True
GROUND_Y = 300
JUMP_GRAVITY_START_SPEED = -20
players_gravity_speed = 0

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load sprite assets
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))

# Load player sprite
NUM_FRAMES = 10
ANIMATION_SPEED_MS = 40
sprite_sheet = pygame.image.load("graphics/player/Run.png").convert_alpha()
frame_w = sprite_sheet.get_width() // NUM_FRAMES
frame_h = sprite_sheet.get_height()

def load_animation(path):
    sheet = pygame.image.load(path).convert_alpha()
    frame_w = sheet.get_width() // NUM_FRAMES
    frame_h = sheet.get_height()
    return [sheet.subsurface((i * frame_w, 0, frame_w, frame_h)) for i in range(NUM_FRAMES)]


jump_frames = load_animation("graphics/player/Jump.png")

run_frames = load_animation("graphics/player/Run.png")
current_frame_idx = 0
player_last_frame_time = pygame.time.get_ticks()
player_surf = run_frames[0]
player_rect = player_surf.get_rect(midbottom=(80, GROUND_Y))

# Custom collision hitbox relative to player_rect
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
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800

    if is_playing:
        screen.fill("purple")
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)

        # Move egg
        egg_rect.x -= 5
        if egg_rect.right <= 0:
            egg_rect.left = 800
        screen.blit(egg_surf, egg_rect)

        # Apply gravity
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y

        # Animate player
        now = pygame.time.get_ticks()
        if now - player_last_frame_time >= ANIMATION_SPEED_MS:
            current_frame_idx = (current_frame_idx + 1) % NUM_FRAMES
            player_last_frame_time = now

        player_surf = run_frames[current_frame_idx]
        screen.blit(player_surf, player_rect)

        # Define hitbox rect based on player frame rect
        hitbox_rect = pygame.Rect(
            player_rect.left + HITBOX_OFFSET_X,
            player_rect.top + HITBOX_OFFSET_Y,
            HITBOX_WIDTH,
            HITBOX_HEIGHT
        )
        pygame.draw.rect(screen, "red", hitbox_rect, 1)

        # Use hitbox for collision
        if egg_rect.colliderect(hitbox_rect):
            is_playing = False

    else:
        screen.fill("black")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
