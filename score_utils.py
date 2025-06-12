import pygame

def display_score(score: int, high_score: int, font: pygame.font.Font, screen: pygame.Surface) -> None:
    """
    Display the current score and high score on the screen.
    """
    score_text = f"HI {high_score}    {score:05d}"
    score_surf = font.render(score_text, False, "white")
    score_rect = score_surf.get_rect(topright=(760, 20))
    screen.blit(score_surf, score_rect)
