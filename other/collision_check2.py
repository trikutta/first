# Importing the pygame module
import pygame
from pygame.locals import *

# Initiate pygame and give permission
# to use pygame's functionality
pygame.init()

# Create a display surface object
# of specific dimension
window = pygame.display.set_mode((1024, 768))

# Creating a new clock object to
# track the amount of time
clock = pygame.time.Clock()


# Creating a new rect for first object
player_rect = Rect(300, 50, 50, 50)

# Creating a new rect for second object
other_rects_unused = [
    Rect(300, 150, 50, 50),
    Rect(325, 225, 50, 50),
    Rect(350, 300, 50, 50),
    Rect(350, 375, 50, 50),
]
other_colors = [(0, 0, 255)] * 4

# Creating variable for gravity
gravity = 4

# Creating a boolean variable that
# we will use to run the while loop
run = True

# Creating an infinite loop
# to run our game
while run:

    # Setting the framerate to 60fps
    clock.tick(60)

    # Adding gravity in player_rect2
    # player_rect.bottom += gravity

    # Checking if player is colliding
    # with platform or not using the
    # colliderect() method.
    # It will return a boolean value
    # collide = pygame.Rect.colliderect(player_rect, player_rect2)

    # If the objects are colliding
    # then changing the y coordinate
    # if collide: player_rect2.bottom = player_rect.top

    main_rect = pygame.draw.rect(window, (0, 255, 0), player_rect)
    main_mask = pygame.Surface((player_rect[0], player_rect[1]), pygame.SRCALPHA)

    # pygame.draw.rect(window, (0,   0,   255), ())
    rect1_rect = pygame.draw.rect(window, other_colors[0], Rect(300, 150, 50, 50))
    circle1_rect = pygame.draw.circle(window, other_colors[1], (325, 225), radius=25)
    circle2_rect = pygame.draw.circle(window, other_colors[2], (370, 300), radius=25)
    rect2_rect = pygame.draw.rect(window, other_colors[3], Rect(340, 375, 50, 50))

    other_rects = [rect1_rect, circle1_rect, circle2_rect, rect2_rect]
    for i, other_rect in enumerate(other_rects):
        is_colliding = pygame.Rect.colliderect(player_rect, other_rect)
        if is_colliding:
            other_colors[i] = (255, 0, 0)
        else:
            other_colors[i] = (0, 0, 255)
    # Updating the display surface
    pygame.display.update()

    # Filling the window with white color
    window.fill((40, 40, 40))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player_rect.bottom += gravity


pygame.quit()

