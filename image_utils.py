import pygame
from typing import List

def scale_to_height(img: pygame.Surface, new_height: int) -> pygame.Surface:
    """
    Scale an image to a new height keeping its aspect ratio.
    """
    original_width, original_height = img.get_size()
    scale_factor = new_height / original_height
    new_width = int(original_width * scale_factor)
    return pygame.transform.scale(img, (int(new_width), new_height))


def scale_frames(frames: List[pygame.Surface], factor: float) -> List[pygame.Surface]:
    """
    Scale a list of frames by a given factor.
    """
    return [
        pygame.transform.scale(frame, (
            int(frame.get_width() * factor),
            int(frame.get_height() * factor)
        )) for frame in frames
    ]


def draw_parallax(screen: pygame.Surface, surface: pygame.Surface, offset: float, ratio: float) -> None:
    """
    Draw a parallax scrolling background.
    """
    scroll = offset * ratio % surface.get_width()
    screen.blit(surface, (-scroll, 0))
    screen.blit(surface, (-scroll + surface.get_width(), 0))
