# Importing pygame module
import pygame
import random
import readchar
import rich
import time
import uuid
import waitress
from abc import abstractmethod
from bs4 import BeautifulSoup, Tag
from flask import Flask, jsonify, request, send_file, Response, render_template, make_response, url_for, session
from PIL import Image
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Tuple, NamedTuple, TypeVar, Generic, Optional, Callable

COLOR_BLACK = (0, 0, 0)
COLOR_DARK_GREY = (25, 25, 25)
COLOR_LIGHT_GREY = (75, 75, 75)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 0, 255)
COLOR_SEMI_BLUE = (92, 144, 189)
COLOR_SEMI_ORANGE = (204, 154, 84)
# SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
# SCREEN_WIDTH, SCREEN_HEIGHT = (SCREEN_WIDTH * 2), (SCREEN_HEIGHT * 2)
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
# 1920 / 48 = 480 / 12 = 120 / 3 = 40
def run_game():
    # initiate pygame and give permission
    # to use pygame's functionality.
    pygame.init()
    # set title
    pygame.display.set_caption('Something')
    timer = pygame.time.Clock()

    # create the display surface object
    # of specific dimension.
    window = pygame.display.set_mode(SCREEN_SIZE)

    # RECTANGLE
    # rect_x, rect_y = 100, 100
    # rect_width, rect_height = 400, 100
    rect_width, rect_height = 15, 40
    rect_x, rect_y = int(SCREEN_WIDTH / 2) - int(rect_width / 2), int((SCREEN_HEIGHT * 4) / 5) - int(rect_height / 2)
    RECT_WIDTH = 0
    # CIRCLE
    circle_radius = 50
    circle_x, circle_y = int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 5)
    CIRCLE_WIDTH = 0
    # circle_movement_base_offset = int(SCREEN_WIDTH / 50)
    circle_movement_base_offset = 10
    circle_movement_direction = 1
    # circle_movement_randomnesses = [(-20, 1), (-10, 1), (0, 2), (10, 1), (20, 1)]
    # circle_movement_randomnesses = [(-10, 1), (0, 2), (10, 1)]
    circle_movement_randomnesses = [(-5, 1), (0, 2), (5, 1)]
    circle_boundary_margin = int(3 * circle_radius)
    circle_limit_x, circle_limit_y = circle_boundary_margin, (SCREEN_WIDTH - circle_boundary_margin)
    circle_moving = True
    MOVE_CIRCLE = pygame.USEREVENT + 1
    MOVE_CIRCLE_INTERVAL = 5
    # posting a event to switch color after every 500ms
    pygame.time.set_timer(MOVE_CIRCLE, MOVE_CIRCLE_INTERVAL)

    run = True
    # Creating a while loop
    while run:
        # Fill the scree with white color
        window.fill(COLOR_DARK_GREY)
        rect_dimension = (rect_width, rect_height)
        rect_position = (rect_x, rect_y)
        circle_position = (circle_x, circle_y)
        # circle_movement_offset = random.choice([circle_movement_base_offset - 10] * 1 + [circle_movement_base_offset - 10] * 1 + [circle_movement_base_offset + 10] * 1)
        circle_movement_offsets = []
        [[circle_movement_offsets.append(circle_movement_base_offset - circle_movement_randomness) for x in range(0, circle_movement_times)] for circle_movement_randomness, circle_movement_times in circle_movement_randomnesses]
        circle_movement_offset = random.choice(circle_movement_offsets)
        # Using draw.rect module of
        # pygame to draw the outlined rectangle
        # pygame.draw.rect(surface=window, color=COLOR_BLUE, rect=[*rect_position, *rect_dimension], width=5, border_radius=5)
        pygame.draw.rect(surface=window, color=COLOR_SEMI_BLUE, rect=[*rect_position, *rect_dimension], width=RECT_WIDTH, border_radius=5)
        # Using draw.rect module of pygame to draw the solid circle
        pygame.draw.circle(window, color=COLOR_SEMI_ORANGE, center=circle_position, radius=circle_radius, width=CIRCLE_WIDTH)
        if not circle_moving:
            # Using draw.rect module of pygame to draw the line
            # pygame.draw.line(window, (0, 0, 0), [100, 300], [500, 300], 5)
            pygame.draw.line(window, color=COLOR_LIGHT_GREY, start_pos=[int(SCREEN_WIDTH / 2), 0], end_pos=[int(SCREEN_WIDTH / 2), SCREEN_HEIGHT], width=1)
            pygame.draw.line(window, color=COLOR_LIGHT_GREY, start_pos=[0, int(SCREEN_HEIGHT / 2)], end_pos=[SCREEN_WIDTH, int(SCREEN_HEIGHT / 2)], width=1)
        for event in pygame.event.get():
            # If the type of the event is quit
            # then setting the run variable to false
            if event.type == pygame.QUIT:
                run = False
            # if the type of the event is MOUSEBUTTONDOWN
            # then storing the current position
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # position = event.pos
                # circle_positions.append(position)
                # rect_x += 10
                circle_moving = not circle_moving
            elif event.type == MOVE_CIRCLE and circle_moving:
                # print(f"moving circle | x={circle_x} | offset={circle_movement_offset}")
                circle_x = circle_x + (circle_movement_offset * circle_movement_direction)
                circle_movement_direction = (circle_movement_direction * -1) if circle_x < circle_limit_x or circle_x > circle_limit_y else circle_movement_direction
        # Draws the surface object to the screen.
        pygame.display.update()
        # pygame.display.flip()
        # Setting Frames per Second
        timer.tick(90)
    # pygame.quit()
    return
def execute():
    run_game()
    return
def main():
    execute()
    return
if __name__ == "__main__":
    main()




