import random
import pygame
from enum import Enum
from pygame import Surface
from bs4 import BeautifulSoup, Tag
from flask import Flask, jsonify, request, send_file, Response, render_template, make_response, url_for, session
from PIL import Image
from pydantic import BaseModel
from typing import List, Dict, Tuple, NamedTuple, TypeVar, Generic, Optional, Callable

ARC_PI = 3.14
def ratio(val:int, mul:int|float=1, div:int|float=1) -> int:
    return int((val * mul) / div)
def image_dimensions(image_file_path):
    with Image.open(image_file_path) as image:
        image_width, image_height = image.size
    return image_width, image_height
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
class CourtArea:
    def __init__(self, position:Position, dimension:Dimension):
        self.position = position
        self.dimension = dimension
    def starting_position(self, player:"InGamePlayer") -> Position:
        x = random.randint(self.position.x, self.position.x + self.dimension.width - player.scaled_dimension.width)
        y = random.randint(self.position.y, self.position.y + self.dimension.height - player.scaled_dimension.height)
        return Position(x=x, y=y)
class Ball(pygame.sprite.Sprite):
    def __init__(self, window:Surface, court:Court):
        super().__init__()
        self.window = window
        self.court = court
        self.player_in_possession = None
        self.image_file_path = f"../images/basketball.png"
        self.position = Position(x=self.court.left + self.court.dimension.ratio_width(div=2), y=self.court.top + self.court.dimension.ratio_height(div=2))
        self.image = pygame.image.load(self.image_file_path).convert_alpha()
        self.actual_image_dimensions = image_dimensions(image_file_path=self.image_file_path)
        self.scaled_width = 30
        self.scaled_height = ratio(val=self.scaled_width, mul=self.actual_image_dimensions[1], div=self.actual_image_dimensions[0])
        self.scaled_dimension = Dimension(width=self.scaled_width, height=self.scaled_height)
        self.scaled_image = pygame.transform.scale(self.image, self.scaled_dimension.get())
        self.rect = self.image.get_rect()
    def is_in_possession(self):
        return self.player_in_possession != None
    def update(self):
        # if self.position is None: return
        # pygame.draw.circle(surface=self.window, color=self.)
        self.window.blit(self.scaled_image, self.position.get())
        return
class PlayerPosition(Enum):
    GUARD = 1
    FORWARD = 2
    CENTER = 3
class Player(BaseModel):
    name:str
    image_file_path:str
    position:PlayerPosition
class Team(BaseModel):
    name:str
    players:List[Player]
class Strategy:
    def __init__(self, court:Court, ball:Ball, team:"InGameTeam"):
        self.court = court
        self.ball = ball
        self.team = team
    def execute(self):
        pass
class LooseBall(Strategy):
    def __init__(self, court:Court, ball:Ball, team:"InGameTeam"):
        super().__init__(court=court, ball=ball, team=team)
    def execute(self):
        return
class InGamePlayer(pygame.sprite.Sprite):
    def __init__(self, window:Surface, court:Court, player:Player, ball:Ball, attack_area:CourtArea, defense_area:CourtArea):
        super().__init__()
        self.window = window
        self.court = court
        self.player = player
        self.attack_area = attack_area
        self.defense_area = defense_area
        self.position = None
        self.image = pygame.image.load(self.player.image_file_path).convert_alpha()
        self.actual_image_dimensions = image_dimensions(image_file_path=self.player.image_file_path)
        self.scaled_width = 75
        self.scaled_height = ratio(val=self.scaled_width, mul=self.actual_image_dimensions[1], div=self.actual_image_dimensions[0])
        self.scaled_dimension = Dimension(width=self.scaled_width, height=self.scaled_height)
        self.scaled_image = pygame.transform.scale(self.image, self.scaled_dimension.get())
        self.rect = self.image.get_rect()
    def update(self):
        # if not self.game_area.contains(self.rect): self.kill()
        self.position = self.defense_area.starting_position(self) if self.position is None else self.position
        # print(f"updating {self.player.name} @ {self.position}")
        # dime = self.scaled_image.get_rect(center=self.window.get_rect())
        self.window.blit(self.scaled_image, self.position.get())
        return
class InGameTeam(pygame.sprite.Sprite):
    def __init__(self, window:Surface, court:Court, ball:Ball, team:Team, is_home:bool):
        super().__init__()
        self.window = window
        self.team = team
        self.court = court
        self.ball = ball
        self.is_home = is_home
        court_home_area = court.get_home_area()
        court_away_area = court.get_away_area()
        self.attack_area = court_away_area if self.is_home else court_home_area
        self.defense_area = court_away_area if self.is_home else court_home_area
        self.players = [InGamePlayer(window=self.window, court=self.court, ball=self.ball, player=x, attack_area=self.attack_area, defense_area=self.defense_area) for x in team.players]
        self.player_sprites = pygame.sprite.Group(*self.players)
    def update(self):
        # if not self.game_area.contains(self.rect): self.kill()
        # [x.update() for x in self.players]

        ### ### ###
        #if self.ball.is_in_possession():
        ### ### ###

        self.player_sprites.update()
        return
class BasketBallTrialGame:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    def __init__(self, home_team:Team, away_team:Team):
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
        self.court = Court(window=self.window)
        self.ball = Ball(window=self.window, court=self.court)
        self.home_team = InGameTeam(window=self.window, court=self.court, ball=self.ball, team=home_team, is_home=True)
        self.away_team = InGameTeam(window=self.window, court=self.court, ball=self.ball, team=away_team, is_home=False)
        # self.all_sprites = [self.court, self.home_team, self.away_team]
        self.all_sprites = pygame.sprite.Group(self.court, self.ball, self.home_team, self.away_team)
    def run_game(self):
        while self.game_running:
            self.window.fill(Color.DARK_GREY)
            # [x.update() for x in self.all_sprites]
            self.all_sprites.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.game_running = False
            pygame.display.update()
            self.timer.tick(90)
        return
def execute():
    # basketball_trial = BasketBallTrialGame()
    # basketball_trial.run_game()
    return
def main():
    execute()
    return
if __name__ == "__main__":
    main()






