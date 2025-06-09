import pygame
from typing import List
import random

# Car-related utilities

def get_car_hitbox_rect(surf: pygame.Surface, x: int, y: int, car_hitbox_trim: int) -> pygame.Rect:
    """
    Get the hitbox rectangle for a car sprite, trimmed by a specified amount.
    """
    rect = surf.get_rect(bottomleft=(x, y))
    rect.width -= car_hitbox_trim  # Trimming so the player falls off more naturally
    return rect


def spawn_car(
    x_start: int,
    car_surfs: List,
    active_car_surfs: List,
    active_car_rects: List,
    ground_y: int,
    car_hitbox_trim: int
) -> None:
    """
    Spawns a car by selecting a random car surface, creating its hitbox, 
    and adding it to the active car surfaces and rectangles.
    """
    surf = random.choice(car_surfs)
    rect = get_car_hitbox_rect(surf, x_start, ground_y, car_hitbox_trim)
    active_car_surfs.append(surf)
    active_car_rects.append(rect)


def is_on_car(car: pygame.Rect, player: pygame.Rect):
    """
    Determines if the player is standing on top of a car.
    """
    # The 5px threshold allows for slight error in where the player is each frame since gravity speed can be >1
    if player.right > car.left and player.left < car.right:
        if abs(player.bottom - car.top) <= 5:
            return True
    return False


def init_cars(
    min_space: int,
    max_space: int,
    car_surfs: List[pygame.Surface],
    active_car_surfs: List[pygame.Surface],
    active_car_rects: List[pygame.Rect],
    ground_y: int = 365,
    screen_width: int = 800,
    num_cars: int = 5,
    right_trim: int = 0
) -> None:
    """
    Initialize cars by spawning a specified number of cars at random intervals off the screen.
    """
    active_car_rects.clear()
    active_car_surfs.clear()
    last_x = screen_width
    for _ in range(num_cars):
        spawn_car(
            last_x,
            car_surfs,
            active_car_surfs,
            active_car_rects,
            ground_y,
            right_trim
        )
        last_x = active_car_rects[-1].right + random.randint(min_space, max_space)


def explode_car(
    active_car_surfs: List[pygame.Surface],
    active_car_rects: List[pygame.Rect],
    car_surfs: List[pygame.Surface],
    explosion_rect: pygame.Rect,
    hitbox_rect: pygame.Rect,
    now: int,
    min_space: int,
    max_space: int,
    car_hitbox_trim: int,
    ground_y: int = 365,
    screen_width: int = 800,
) -> None:
    """
    Explode the next car by creating an explosion effect at its position and spawn a new car at the end.
    """
    for i in range(len(active_car_rects)):
        if active_car_rects[i].left > hitbox_rect.right:
            explosion_rect.centerx = active_car_rects[i].centerx
            explosion_rect.bottom = active_car_rects[i].bottom + 30  # Offset for visual alignment
            active_car_rects.pop(i)
            active_car_surfs.pop(i)
            last_x = active_car_rects[-1].right if active_car_rects else screen_width
            spawn_car(
                last_x + random.randint(min_space, max_space),
                car_surfs,
                active_car_surfs,
                active_car_rects,
                ground_y,
                car_hitbox_trim
            )
            break
