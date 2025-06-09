import pygame
from typing import List, Tuple

# Animation-related utilities

def advance_animation(
    frame_idx: int,
    last_time: int,
    delay: int,
    frames: List[pygame.Surface],
    now: int,
    loop: bool = True,
    clamp: bool = True
) -> Tuple[int, int]:
    """
    Advance the animation frame based on time and delay.
    """
    if now - last_time > delay:
        frame_idx += 1
        last_time = now
        # Clamp to last frame if not looping, so animation doesn't reset
        if frame_idx >= len(frames):
            if loop:
                frame_idx = 0
            elif clamp:
                frame_idx = len(frames) - 1
    return frame_idx, last_time


def load_animation(path: str, num_frames: int) -> List[pygame.Surface]:
    """
    Load an animation from a sprite sheet.
    """
    sheet = pygame.image.load(path).convert_alpha()
    frame_w = sheet.get_width() // num_frames
    frame_h = sheet.get_height()
    # Loop through the sprite sheet to create a list of surfaces for each frame
    return [sheet.subsurface((i * frame_w, 0, frame_w, frame_h)) for i in range(num_frames)]


def load_multi_img_animation(path: str, num_frames: int) -> List[pygame.Surface]:
    """
    Load an animation from multiple image files.
    """
    # Some animations are stored as separate images
    return [pygame.image.load(path + str(i) + ".png").convert_alpha() for i in range(1, num_frames + 1)]
