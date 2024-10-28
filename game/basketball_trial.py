# Importing pygame module
import pygame
from pygame import Surface
from bs4 import BeautifulSoup, Tag
from flask import Flask, jsonify, request, send_file, Response, render_template, make_response, url_for, session
from PIL import Image
from pydantic import BaseModel
from typing import List, Dict, Tuple, NamedTuple, TypeVar, Generic, Optional, Callable

ARC_PI = 3.14
def ratio(val:int, mul:int|float=1, div:int|float=1) -> int:
    return int((val * mul) / div)
class Color:
    BLACK = (0, 0, 0)
    DARK_GREY = (25, 25, 25)
    LIGHT_GREY = (75, 75, 75)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    SEMI_BLUE = (92, 144, 189)
    SEMI_ORANGE = (204, 154, 84)
    VERY_LIGHT_ORANGE = (241, 208, 159)
    SEMI_RED = (227, 112, 112)
class Dimension:
    def __init__(self, width:int, height:int):
        self.width = width
        self.height = height
    @classmethod
    def new(cls, pair:Tuple[int, int]) -> "Dimension":
        return Dimension(width=pair[0], height=pair[1])
    def get(self) -> Tuple[int, int]:
        return self.width, self.height
    def ratio_width(self, mul:int|float=1, div:int|float=1) -> int:
        return ratio(val=self.width, mul=mul, div=div)
    def ratio_height(self, mul:int|float=1, div:int|float=1) -> int:
        return ratio(val=self.height, mul=mul, div=div)
class Position:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y
    @classmethod
    def new(cls, pair:Tuple[int, int]) -> "Position":
        return Position(x=pair[0], y=pair[1])
    def get(self) -> Tuple[int, int]:
        return self.x, self.y
    def ratio_x(self, mul:int|float=1, div:int|float=1) -> int:
        return ratio(val=self.x, mul=mul, div=div)
    def ratio_y(self, mul:int|float=1, div:int|float=1) -> int:
        return ratio(val=self.y, mul=mul, div=div)
class Pixel:
    def __init__(self, screen:Surface, color:Tuple[int, int, int], position:Position, size:int=1):
        self.screen = screen
        self.color = color
        self.position = position
        self.size = size
    def update(self):
        pygame.draw.circle(self.screen, self.color, self.position.get(), self.size)
class Player(pygame.sprite.Sprite):
    def __init__(self, window:Surface, name:str):
        super().__init__()
        self.window = window
        self.name = name
        self.position = None
    def update(self):
        # if not self.game_area.contains(self.rect): self.kill()
        return
class SpriteStyle(BaseModel):
    color:Tuple[int, int, int]
    width:int
    radius:int=0
class Court(pygame.sprite.Sprite):
    DEFAULT_COURT_STYLE = SpriteStyle(color=Color.VERY_LIGHT_ORANGE, width=0)
    DEFAULT_MARKING_STYLE = SpriteStyle(color=Color.LIGHT_GREY, width=2)
    DEFAULT_BASKET_STYLE = SpriteStyle(color=Color.SEMI_RED, width=4)
    # def __init__(self, window:Surface, court_style:Color=Color.VERY_LIGHT_ORANGE, marking_color:Color=Color.LIGHT_GREY, basket_color:Color=Color.SEMI_RED, border_width:int=1, border_radius:int=0, court_width:int=0, marking_width:int=2, marking_radius:int=0):
    def __init__(self, window:Surface, court_style:SpriteStyle=DEFAULT_COURT_STYLE, marking_style:SpriteStyle=DEFAULT_MARKING_STYLE, basket_style:SpriteStyle=DEFAULT_BASKET_STYLE):
        super().__init__()
        self.window = window
        self.court_style = court_style
        self.marking_style = marking_style
        self.basket_style = basket_style
        self.screen_size = Dimension.new(pair=self.window.get_size())
        self.top = self.screen_size.ratio_height(mul=1, div=11)
        self.bottom = self.screen_size.ratio_height(mul=10, div=11)
        self.height = self.bottom - self.top
        # self.width = ratio(val=self.height, mul=0.531914893617)
        self.width = ratio(val=self.height, mul=0.631914893617)
        self.left = self.screen_size.ratio_width(div=2) - ratio(val=self.width, div=2)
        self.right = self.screen_size.ratio_width(div=2) + ratio(val=self.width, div=2)
        self.position = Position(x=self.left, y=self.top)
        self.dimension = Dimension(width=self.width, height=self.height)
        self.rect = [*self.position.get(), *self.dimension.get()]
    def draw_court(self):
        self.rect = [*self.position.get(), *self.dimension.get()]
        pygame.draw.rect(surface=self.window, color=self.court_style.color, rect=self.rect, width=self.court_style.width, border_radius=self.court_style.radius)
        return
    def draw_mid_line(self):
        half_height = self.top + self.dimension.ratio_height(div=2)
        mid_line_start_position = Position(x=self.left, y=half_height)
        mid_line_end_position = Position(x=self.right, y=half_height)
        pygame.draw.line(surface=self.window, color=self.marking_style.color, start_pos=mid_line_start_position.get(), end_pos=mid_line_end_position.get(), width=self.marking_style.width)
        return
    def draw_box(self, box_width:int, box_height:int, box_y:int):
        box_left = self.dimension.ratio_width(div=2) - ratio(val=box_width, div=2) + self.left
        box_position = Position(x=box_left, y=box_y)
        box_dimension = Dimension(width=box_width, height=box_height)
        box_rect = [*box_position.get(), *box_dimension.get()]
        pygame.draw.rect(surface=self.window, color=self.marking_style.color, rect=box_rect, width=self.marking_style.width, border_radius=self.marking_style.radius)
        return
    def draw_box_circle(self, center_y:int):
        box_circle_radius = self.dimension.ratio_width(mul=6, div=50)
        box_circle_position = Position(x=self.left + self.dimension.ratio_width(div=2), y=center_y)
        pygame.draw.circle(surface=self.window, color=self.marking_style.color, center=box_circle_position.get(), radius=box_circle_radius, width=self.marking_style.width)
        return
    def draw_box_circles(self, box_height:int):
        self.draw_box_circle(center_y=self.top + box_height)
        self.draw_box_circle(center_y=self.bottom - box_height)
        return
    def draw_outer_line(self, outer_line_left:int, outer_line_top:int, outer_line_height:int):
        outer_line_start = Position(x=self.left + outer_line_left, y=outer_line_top)
        outer_line_end = Position(x=self.left + outer_line_left, y=outer_line_top + outer_line_height)
        pygame.draw.line(surface=self.window, color=self.marking_style.color, start_pos=outer_line_start.get(), end_pos=outer_line_end.get(), width=self.marking_style.width)
        return
    def draw_arcs(self, outer_line_left:int, outer_line_right:int, outer_line_height:int):
        arc_start_x = self.left + outer_line_left
        arc_start_y = self.top + outer_line_height
        arc_end_x = self.left + outer_line_right
        arc_end_y = self.top + outer_line_height
        # boom = 500
        # arc_end_x = boom
        # arc_end_y = boom
        arc_rect = (arc_start_x, arc_start_y, arc_end_x, arc_end_y)
        start_angle = ARC_PI / 2
        stop_angle = ARC_PI * 2
        # arc_rect = (50, 50, 100, 100)
        start_angle = ARC_PI + ((ARC_PI * 1)/ 4)
        stop_angle = ARC_PI + ((ARC_PI * 3)/ 4)
        arc_length = self.dimension.ratio_height(mul=14, div=50)
        # pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=arc_rect, start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=(50, 50, 100, 100), start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=(50, 100, 100, 100), start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=(arc_start_x, arc_start_y, outer_line_right, arc_length), start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        # pygame.draw.line(surface=self.window, color=self.marking_style.color, start_pos=(arc_start_x, arc_start_y), end_pos=(arc_end_x, arc_end_y), width=self.marking_style.width)
        pygame.draw.rect(surface=self.window, color=self.marking_style.color, rect=(arc_start_x, arc_start_y, outer_line_right, arc_length), width=self.marking_style.width, border_radius=self.marking_style.radius)
        return
    def draw_outer_lines(self):
        outer_line_height = self.dimension.ratio_height(mul=14, div=94)
        outer_line_left = self.dimension.ratio_width(mul=3, div=50)
        outer_line_right = self.dimension.ratio_width(mul=47, div=50)
        self.draw_outer_line(outer_line_left=outer_line_left, outer_line_top=self.top, outer_line_height=outer_line_height)
        self.draw_outer_line(outer_line_left=outer_line_right, outer_line_top=self.top, outer_line_height=outer_line_height)
        self.draw_outer_line(outer_line_left=outer_line_left, outer_line_top=self.bottom - outer_line_height, outer_line_height=outer_line_height)
        self.draw_outer_line(outer_line_left=outer_line_right, outer_line_top=self.bottom - outer_line_height, outer_line_height=outer_line_height)
        self.draw_arcs(outer_line_left=outer_line_left, outer_line_right=outer_line_right, outer_line_height=outer_line_height)
        return
    def draw_boxes(self):
        outer_width = self.dimension.ratio_width(mul=16, div=50)
        inner_width = self.dimension.ratio_width(mul=12, div=50)
        box_height = self.dimension.ratio_height(mul=19, div=94)
        self.draw_box(box_width=outer_width, box_height=box_height, box_y=self.top)
        self.draw_box(box_width=inner_width, box_height=box_height, box_y=self.top)
        self.draw_box(box_width=outer_width, box_height=box_height, box_y=self.bottom - box_height)
        self.draw_box(box_width=inner_width, box_height=box_height, box_y=self.bottom - box_height)
        self.draw_box_circles(box_height=box_height)
        return
    def draw_center_circle(self, mul:int=1, div:int=1):
        circle_radius = self.dimension.ratio_width(mul=mul, div=div)
        circle_position = Position(x=self.left + self.dimension.ratio_width(div=2), y=self.top + self.dimension.ratio_height(div=2))
        pygame.draw.circle(surface=self.window, color=self.marking_style.color, center=circle_position.get(), radius=circle_radius, width=self.marking_style.width)
        return
    def draw_inner_center_circle(self):
        return self.draw_center_circle(mul=2, div=50)
    def draw_outer_center_circle(self):
        return self.draw_center_circle(mul=6, div=50)
    def draw_center_circles(self):
        self.draw_inner_center_circle()
        self.draw_outer_center_circle()
        return
    def draw_basket(self, basket_radius:int, basket_y:int):
        basket_position = Position(x=self.left + self.dimension.ratio_width(div=2), y=basket_y + basket_radius)
        pygame.draw.circle(surface=self.window, color=self.basket_style.color, center=basket_position.get(), radius=basket_radius, width=self.basket_style.width)
        return
    def draw_baskets(self):
        basket_radius = self.dimension.ratio_width(mul=1.5, div=50)
        basket_diameter = basket_radius * 2
        self.draw_basket(basket_radius=basket_radius, basket_y=self.top)
        self.draw_basket(basket_radius=basket_radius, basket_y=self.bottom - basket_diameter)
        return
    def update(self):
        # if not self.game_area.contains(self.rect): self.kill()
        self.draw_court()
        self.draw_mid_line()
        self.draw_boxes()
        self.draw_center_circles()
        self.draw_baskets()
        self.draw_outer_lines()
        return
# class Player(pygame.sprite.Sprite):
class BasketBallTrialGame:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Basketball Trial')
        self.timer = pygame.time.Clock()
        # self.window:Surface = pygame.display.set_mode(self.SCREEN_SIZE)
        # self.window:Surface = pygame.display.set_mode((0, 0))
        # You have to call this before pygame.display.set_mode()
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w,info.current_h
        self.window:Surface = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.game_running = True
    def run_game(self):
        court = Court(window=self.window)
        all_sprites = [court]
        while self.game_running:
            self.window.fill(Color.DARK_GREY)
            [x.update() for x in all_sprites]
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.game_running = False
            pygame.display.update()
            self.timer.tick(90)
        return
def execute():
    basketball_trial = BasketBallTrialGame()
    basketball_trial.run_game()
    return
def main():
    execute()
    return
if __name__ == "__main__":
    main()





