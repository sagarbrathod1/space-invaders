import pygame
from pygame.locals import *

# define fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

# load background image
background = pygame.image.load("assets/space_background.png")

def draw_background():
    screen.blit(background, (0, 0))

run = True
while run:

    # frame rate
    clock.tick(fps)

    # drawing the background
    draw_background()

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()