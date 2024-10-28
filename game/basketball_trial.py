import random
import pygame
from enum import Enum
from pygame import Surface
from bs4 import BeautifulSoup, Tag
from flask import Flask, jsonify, request, send_file, Response, render_template, make_response, url_for, session
from PIL import Image
from game.court import Court, CourtArea
from game.utils import ARC_PI, Color, Position, Dimension, Pixel, SpriteStyle, ratio, image_dimensions
from pydantic import BaseModel
from typing import List, Dict, Tuple, NamedTuple, TypeVar, Generic, Optional, Callable

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
        self.position = self.defense_area.starting_position(player_width=self.scaled_dimension.width, player_height=self.scaled_dimension.height) if self.position is None else self.position
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






