import pygame
import random

# Constants for world
SCREEN_WIDTH = 800
GROUND_Y_DEFAULT = 365

AMMO_MAX = 3
AMMO_ICON_HEIGHT = 32
AMMO_PICKUP_HEIGHT = 32
AMMO_PICKUP_WIDTH = 32
AMMO_PICKUP_MIN_SPACING = 800
AMMO_PICKUP_MAX_SPACING = 1600


def draw_ammo_ui(screen: pygame.Surface, ammo_icon: pygame.Surface, player_ammo: int) -> None:
    """
    Draw the ammo UI on the screen.
    """
    for i in range(player_ammo):
        screen.blit(ammo_icon, (10 + i * (AMMO_ICON_HEIGHT + 4), 10))


def manage_ammo_pickups(
    ammo_pickups: list[pygame.Rect],
    car_rects: list[pygame.Rect],
    player_rect: pygame.Rect,
    player_ammo: int,
    scroll_step: int
) -> int:
    """
    Handle all ammo pickup logic: movement, cleanup, collision, and spawning.
    Returns updated player_ammo.
    """
    # Move all pickups with the world
    for pickup in ammo_pickups:
        pickup.x -= scroll_step
    
    # Remove off-screen pickups
    ammo_pickups[:] = [p for p in ammo_pickups if p.right > 0]  # Modify the list in place to keep the reference
    
    # Check for player collision with pickups
    for pickup in ammo_pickups[:]:
        if player_rect.colliderect(pickup) and player_ammo < AMMO_MAX:
            player_ammo += 1
            ammo_pickups.remove(pickup)
    
    # Keep 1-2 pickups on screen - spawn if needed
    while len(ammo_pickups) < 2:
        # Find spawn position
        last_pickup_x = max([p.right for p in ammo_pickups], default=SCREEN_WIDTH)
        x = last_pickup_x + random.randint(AMMO_PICKUP_MIN_SPACING, AMMO_PICKUP_MAX_SPACING)
        
        # Simple collision avoidance with cars
        for car_rect in car_rects:
            if abs(x - car_rect.centerx) < 150:  # Too close to car
                x = car_rect.right + 100  # Move past it
        
        y = GROUND_Y_DEFAULT - AMMO_PICKUP_HEIGHT
        ammo_pickups.append(pygame.Rect(x, y, AMMO_PICKUP_WIDTH, AMMO_PICKUP_HEIGHT))
    
    return player_ammo
