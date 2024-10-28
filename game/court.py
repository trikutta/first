import pygame
import random
from PIL import Image
from pydantic import BaseModel
from pygame import Surface
from typing import List, Dict, NamedTuple, Tuple, Optional
from game.utils import ARC_PI, Color, Position, Dimension, Pixel, SpriteStyle, ratio, image_dimensions

class CourtArea:
    def __init__(self, position:Position, dimension:Dimension):
        self.position = position
        self.dimension = dimension
    def starting_position(self, player_width:int, player_height:int) -> Position:
        x = random.randint(self.position.x, self.position.x + self.dimension.width - player_width)
        y = random.randint(self.position.y, self.position.y + self.dimension.height - player_height)
        return Position(x=x, y=y)
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
        self.court_scale_by = 29
        self.top = self.screen_size.ratio_height(mul=1, div=self.court_scale_by)
        self.bottom = self.screen_size.ratio_height(mul=self.court_scale_by - 1, div=self.court_scale_by)
        self.height = self.bottom - self.top
        # self.width = ratio(val=self.height, mul=0.531914893617)
        self.width = ratio(val=self.height, mul=0.631914893617)
        self.left = self.screen_size.ratio_width(div=2) - ratio(val=self.width, div=2)
        self.right = self.screen_size.ratio_width(div=2) + ratio(val=self.width, div=2)
        self.position = Position(x=self.left, y=self.top)
        self.dimension = Dimension(width=self.width, height=self.height)
        self.rect = [*self.position.get(), *self.dimension.get()]
        self.count_rect = None
        self.mid_line_rect = None
        self.top_box_rect = None
        self.bottom_box_rect = None
        self.top_arc_rect = None
        self.bottom_arc_rect = None
    def get_home_area(self) -> "CourtArea":
        return CourtArea(position=Position(x=self.left, y=self.top), dimension=Dimension(width=self.dimension.width, height=self.dimension.ratio_height(div=2)))
    def get_away_area(self) -> "CourtArea":
        return CourtArea(position=Position(x=self.left, y=self.top + self.dimension.ratio_height(div=2)), dimension=Dimension(width=self.dimension.width, height=self.dimension.ratio_height(div=2)))
    def draw_court(self):
        self.rect = [*self.position.get(), *self.dimension.get()]
        self.count_rect = pygame.draw.rect(surface=self.window, color=self.court_style.color, rect=self.rect, width=self.court_style.width, border_radius=self.court_style.radius)
        return
    def draw_mid_line(self):
        half_height = self.top + self.dimension.ratio_height(div=2)
        mid_line_start_position = Position(x=self.left, y=half_height)
        mid_line_end_position = Position(x=self.right, y=half_height)
        self.mid_line_rect = pygame.draw.line(surface=self.window, color=self.marking_style.color, start_pos=mid_line_start_position.get(), end_pos=mid_line_end_position.get(), width=self.marking_style.width)
        return
    def draw_box(self, box_width:int, box_height:int, box_y:int):
        box_left = self.dimension.ratio_width(div=2) - ratio(val=box_width, div=2) + self.left
        box_position = Position(x=box_left, y=box_y)
        box_dimension = Dimension(width=box_width, height=box_height)
        box_rect_area = [*box_position.get(), *box_dimension.get()]
        box_rect = pygame.draw.rect(surface=self.window, color=self.marking_style.color, rect=box_rect_area, width=self.marking_style.width, border_radius=self.marking_style.radius)
        return box_rect
    def draw_box_circle(self, center_y:int):
        box_circle_radius = self.dimension.ratio_width(mul=6, div=50)
        box_circle_position = Position(x=self.left + self.dimension.ratio_width(div=2), y=center_y)
        box_rect = pygame.draw.circle(surface=self.window, color=self.marking_style.color, center=box_circle_position.get(), radius=box_circle_radius, width=self.marking_style.width)
        return box_rect
    def draw_box_circles(self, box_height:int):
        self.top_box_rect = self.draw_box_circle(center_y=self.top + box_height)
        self.bottom_box_rect = self.draw_box_circle(center_y=self.bottom - box_height)
        return
    def draw_outer_line(self, outer_line_left:int, outer_line_top:int, outer_line_height:int):
        outer_line_start = Position(x=self.left + outer_line_left, y=outer_line_top)
        outer_line_end = Position(x=self.left + outer_line_left, y=outer_line_top + outer_line_height)
        pygame.draw.line(surface=self.window, color=self.marking_style.color, start_pos=outer_line_start.get(), end_pos=outer_line_end.get(), width=self.marking_style.width)
        return
    def draw_arcs(self, outer_line_left:int, outer_line_right:int, outer_line_height:int):
        arc_rect_length = outer_line_height * 2
        rect_width = outer_line_right - outer_line_left
        arc_rect_area = (self.left + outer_line_left, self.top, rect_width, arc_rect_length)
        # pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=arc_rect_area, start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        # pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=(50, 50, 100, 100), start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        # pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=(50, 100, 100, 100), start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        # pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=(arc_start_x, arc_start_y, rect_width, arc_length), start_angle=start_angle, stop_angle=stop_angle, width=self.marking_style.width)
        self.top_arc_rect = pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=arc_rect_area, start_angle=ARC_PI, stop_angle=ARC_PI * 2, width=self.marking_style.width)
        # pygame.draw.line(surface=self.window, color=self.marking_style.color, start_pos=(arc_start_x, arc_start_y), end_pos=(arc_end_x, arc_end_y), width=self.marking_style.width)
        # pygame.draw.rect(surface=self.window, color=self.marking_style.color, rect=(arc_start_x, arc_start_y, rect_width, arc_length), width=self.marking_style.width, border_radius=self.marking_style.radius)

        arc_rect_area = (self.left + outer_line_left, self.bottom - arc_rect_length, rect_width, arc_rect_length)
        self.bottom_arc_rect = pygame.draw.arc(surface=self.window, color=self.marking_style.color, rect=arc_rect_area, start_angle=0, stop_angle=ARC_PI, width=self.marking_style.width)
        # self.bottom_arc_rect = pygame.draw.arc(surface=self.window, color=(50, 100, 200), rect=arc_rect_area, start_angle=0, stop_angle=ARC_PI, width=0)
        return
    def draw_mid_range(self):
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
        self.draw_mid_range()
        return









