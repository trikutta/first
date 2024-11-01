import pygame
from enum import Enum
from pygame import Surface, Rect
from game.court import Court, CourtArea
from game.utils import ARC_PI, Color, Position, Dimension, Pixel, SpriteStyle, ratio, image_dimensions, find_trend
from pydantic import BaseModel
from typing import List, Dict, Tuple, NamedTuple, TypeVar, Generic, Optional, Callable

class PlayerPosition(Enum):
    GUARD = 1
    FORWARD = 2
    CENTER = 3
class Play(BaseModel):
    long:int
    three:int
    mid:int
    post:int
    drive:int
class Pref(BaseModel):
    long:int
    three:int
    mid:int
    post:int
    drive:int
    passing:int
class Zone(BaseModel):
    short:int
    mid:int
    long:int
    half:int
class Stealing(BaseModel):
    on_pass:int
    on_ball:int
class Player(BaseModel):
    name:str
    image_file_path:str
    position:PlayerPosition
    speed:int=1
    shooting_rating:Play=Play(long=5, three=40, mid=50, post=40, drive=50)
    passing:Zone=Zone(short=80, mid=75, long=40, half=20)
    attack_pref:Pref=Pref(long=3, three=18, mid=30, post=19, drive=30, passing=60)
    stealing:Stealing=Stealing(on_pass=30, on_ball=40)
    blocking:Zone=Zone(short=40, mid=30, long=20, half=5)
    stamina:int=80
    risky:int=40
    def trend_speed(self, trend:int, invert:bool=False):
        inversion = -1 if invert else 1
        return self.speed * (trend * inversion)
    def inverse_trend_speed(self, trend:int):
        return -1 * self.trend_speed(trend=trend)
class Team(BaseModel):
    name:str
    players:List[Player]
class Ball(pygame.sprite.Sprite):
    def __init__(self, window:Surface, court:Court):
        super().__init__()
        self.window = window
        self.court = court
        self.player_in_possession = None
        self.team_in_possession = None
        self.image_file_path = f"../game/images/basketball.png"
        self.position = None
        self.image = pygame.image.load(self.image_file_path).convert_alpha()
        self.actual_image_dimensions = image_dimensions(image_file_path=self.image_file_path)
        self.scaled_width = 30
        self.scaled_height = ratio(val=self.scaled_width, mul=self.actual_image_dimensions[1], div=self.actual_image_dimensions[0])
        self.scaled_dimension = Dimension(width=self.scaled_width, height=self.scaled_height)
        self.scaled_image = pygame.transform.scale(self.image, self.scaled_dimension.get())
        self.rect = self.image.get_rect()
    def starting_position(self):
        self.unset_possession()
        self.position = Position(x=self.court.left + self.court.dimension.ratio_width(div=2), y=self.court.top + self.court.dimension.ratio_height(div=2))
        # print(f"[RESET] BALL: {self.position.get()} | {id(self)}")
        return
    def get_rect(self, x:int=None, y:int=None) -> Rect:
        position = Position.new(pair=self.position.get())
        position.x = position.x if x is None else x
        position.y = position.y if y is None else y
        dimension = self.scaled_dimension
        return Rect(position.get(), dimension.get())
    def update(self):
        # print(f"[UPDATE] BALL: {self.position.get()} | {id(self)}")
        # if self.position is None: return
        # pygame.draw.circle(surface=self.window, color=self.)
        self.window.blit(self.scaled_image, self.position.get())
        return
    def is_in_possession(self) -> bool:
        return self.player_in_possession is not None
    def is_not_in_possession(self) -> bool:
        return self.player_in_possession is None
    def sync_ball_position_to_possession(self):
        if self.is_in_possession():
            self.position = Position.copy(position=self.player_in_possession.position)
        return
    def set_possession(self, player:"InGamePlayer", team:"InGameTeam"):
        self.player_in_possession = player
        self.team_in_possession = team
        return
    def unset_possession(self):
        self.player_in_possession = None
        self.team_in_possession = None
        return
class InGamePlayer(pygame.sprite.Sprite):
    def __init__(self, window:Surface, court:Court, ball:Ball, player:Player, attack_area:CourtArea, defense_area:CourtArea):
        super().__init__()
        self.window = window
        self.court = court
        self.ball = ball
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
        self.stamina = self.player.stamina
    def get_rect(self, x:int=None, y:int=None) -> Rect:
        position = Position.new(pair=self.position.get())
        position.x = position.x if x is None else x
        position.y = position.y if y is None else y
        dimension = self.scaled_dimension
        return Rect(position.get(), dimension.get())
    def update(self):
        # print(f"[UPDATE][{self.player.name}] {self.position.get()}")
        # if not self.game_area.contains(self.rect): self.kill()
        # self.position = self.defense_area.starting_position(player_width=self.scaled_dimension.width, player_height=self.scaled_dimension.height) if self.position is None else self.position
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
        self.player_sprites.update()
        return
class Strategy:
    def __init__(self, court:Court, ball:Ball):
        self.court = court
        self.ball = ball
    def execute(self, team:"InGameTeam"):
        pass
    @classmethod
    def is_player_colliding(cls, player:InGamePlayer, all_players:List[InGamePlayer], x:int=None, y:int=None):
        for all_player in all_players:
            if all_player.player.name == player.player.name:
                continue
            is_colliding = pygame.Rect.colliderect(all_player.get_rect(), player.get_rect(x=x, y=y))
            if is_colliding:
                return True
        return False
    @classmethod
    def is_player_not_colliding(cls, player:InGamePlayer, all_players:List[InGamePlayer], x:int=None, y:int=None):
        return not cls.is_player_colliding(player=player, all_players=all_players, x=x, y=y)
class LooseBall(Strategy):
    def __init__(self, court:Court, ball:Ball):
        super().__init__(court=court, ball=ball)
    def execute(self, teams:List["InGameTeam"]):
        all_players = [y for x in teams for y in x.players]
        for team in teams:
            for player in team.players:
                # player.chase_ball()
                trend_x = find_trend(self.ball.position.x - player.position.x)
                x = player.position.x + player.player.trend_speed(trend=trend_x)
                if self.is_player_not_colliding(player=player, all_players=all_players, x=x, y=None):
                    player.position.x = x

                trend_y = find_trend(self.ball.position.y - player.position.y)
                y = player.position.y + player.player.trend_speed(trend=trend_y)
                if self.is_player_not_colliding(player=player, all_players=all_players, x=player.position.x, y=y):
                    player.position.y = y
        return
class SimpleAttack(Strategy):
    def __init__(self, court:Court, ball:Ball):
        super().__init__(court=court, ball=ball)
    def execute(self, teams:List["InGameTeam"]):
        for team in teams:
            for player in team.players:
                if player.player.name == self.ball.player_in_possession.player.name:
                    # player.advance_ball()
                    self.do_nothing()
                else:
                    # player.move_to_attack()
                    self.do_nothing()
        return
    def do_nothing(self):
        return


