import pygame

# Sound and music management

# Initialize pygame mixer
if not pygame.mixer.get_init():
    pygame.mixer.init()

# Music state tracking
menu_music_loaded = False
game_music_loaded = False

# Sound effects
shot_sound = None
explosion_sound = None
reload_sound = None
hover_sound = None
click_sound = None
death_sound = None

def load_sound_effects():
    """Load all sound effects into memory."""
    global shot_sound, explosion_sound, reload_sound, hover_sound, click_sound, death_sound
    
    try:
        shot_sound = pygame.mixer.Sound("assets/sound/sound_effects/shot.mp3")
        explosion_sound = pygame.mixer.Sound("assets/sound/sound_effects/explosion.mp3")
        reload_sound = pygame.mixer.Sound("assets/sound/sound_effects/reload.mp3")
        hover_sound = pygame.mixer.Sound("assets/sound/sound_effects/hover.wav")
        click_sound = pygame.mixer.Sound("assets/sound/sound_effects/click.wav")
        death_sound = pygame.mixer.Sound("assets/sound/sound_effects/death.mp3")
        
        # Set volumes for sound effects
        shot_sound.set_volume(0.7)
        explosion_sound.set_volume(1.0)
        reload_sound.set_volume(0.6)
        hover_sound.set_volume(0.4)
        click_sound.set_volume(0.5)
        death_sound.set_volume(0.8)
        
    except pygame.error as e:
        print(f"Warning: Could not load sound effect: {e}")

def load_menu_music():
    """Load and play menu music if not already playing."""
    global menu_music_loaded, game_music_loaded
    if not menu_music_loaded:
        try:
            pygame.mixer.music.load("assets/sound/music/menu_music.mp3")
            pygame.mixer.music.play(-1)  # Loop indefinitely
            menu_music_loaded = True
            game_music_loaded = False
        except pygame.error as e:
            print(f"Warning: Could not load menu music: {e}")

def load_game_music():
    """Load and play game music if not already playing."""
    global menu_music_loaded, game_music_loaded
    if not game_music_loaded:
        try:
            pygame.mixer.music.load("assets/sound/music/game_music.mp3")
            pygame.mixer.music.play(-1)  # Loop indefinitely
            game_music_loaded = True
            menu_music_loaded = False
        except pygame.error as e:
            print(f"Warning: Could not load game music: {e}")

def play_shot_sound():
    """Play the shooting sound effect."""
    if shot_sound:
        shot_sound.play()

def play_explosion_sound():
    """Play the explosion sound effect."""
    if explosion_sound:
        explosion_sound.play()

def play_reload_sound():
    """Play the reload/ammo pickup sound effect."""
    if reload_sound:
        reload_sound.play()

def play_hover_sound():
    from screens import sfx_volume
    if hover_sound:
        hover_sound.set_volume(sfx_volume)
        hover_sound.play()

def play_click_sound():
    from screens import sfx_volume
    if click_sound:
        click_sound.set_volume(sfx_volume)
        click_sound.play()

def play_death_sound():
    """Play the death sound effect."""
    from screens import sfx_volume
    if death_sound:
        death_sound.set_volume(sfx_volume * 0.8)
        death_sound.play()

def stop_music():
    """Stop all music playback."""
    global menu_music_loaded, game_music_loaded
    pygame.mixer.music.stop()
    menu_music_loaded = False
    game_music_loaded = False

def set_music_volume(volume):
    """Set the music volume (0.0 to 1.0)."""
    pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

def set_sound_volume(volume):
    """Set the volume for all sound effects (0.0 to 1.0)."""
    volume = max(0.0, min(1.0, volume))
    if shot_sound:
        shot_sound.set_volume(volume * 0.7)
    if explosion_sound:
        explosion_sound.set_volume(volume * 0.8)
    if reload_sound:
        reload_sound.set_volume(volume * 0.6)
    if hover_sound:
        hover_sound.set_volume(volume * 0.4)
    if click_sound:
        click_sound.set_volume(volume * 0.5)
    if death_sound:
        death_sound.set_volume(volume * 0.8)

# Initialize sound effects and set default music volume
load_sound_effects()
pygame.mixer.music.set_volume(0.5)