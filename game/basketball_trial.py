import random
import pygame
from enum import Enum
from pygame import Surface
from bs4 import BeautifulSoup, Tag
from flask import Flask, jsonify, request, send_file, Response, render_template, make_response, url_for, session
from PIL import Image
from game.entities import Player, Team, Ball, InGamePlayer, InGameTeam, PlayerPosition, Strategy, LooseBall, SimpleAttack
from game.court import Court, CourtArea
from game.utils import ARC_PI, Color, Position, Dimension, Pixel, SpriteStyle, ratio, image_dimensions, find_trend
from pydantic import BaseModel
from typing import List, Dict, Tuple, NamedTuple, TypeVar, Generic, Optional, Callable

class BasketBallTrialGame:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    TICK_RATE = 60
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
        self.all_teams = [self.home_team, self.away_team]
        self.all_players = [y for x in self.all_teams for y in x.players]
        # self.all_sprites = [self.court, self.home_team, self.away_team]
        self.all_sprites = pygame.sprite.Group(self.court, self.home_team, self.away_team, self.ball)
        self.strategy_loose_ball = LooseBall(court=self.court, ball=self.ball)
        self.strategy_simple_attack = SimpleAttack(court=self.court, ball=self.ball)
    def run_game(self):
        self.start_game()
        while self.game_running:
            self.window.fill(Color.DARK_GREY)
            is_update_game_state = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.game_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"MOUSE BUTTON DOWN !!!")
                    self.start_game()
                    is_update_game_state = False
            if is_update_game_state:
                self.update_game_state()
            # [x.update() for x in self.all_sprites]
            self.all_sprites.update()
            pygame.display.update()
            self.timer.tick(self.TICK_RATE)
        return
    def start_game(self):
        self.ball.starting_position()
        self.players_to_starting_positions()
        return
    def players_to_starting_positions(self):
        # player.position = self.defense_area.starting_position(player_width=player.scaled_dimension.width, player_height=player.scaled_dimension.height) if player.position is None else player.position
        [self.players_to_starting_positions_within_area(player=player, area=self.home_team.defense_area) for player in self.home_team.players]
        [self.players_to_starting_positions_within_area(player=player, area=self.away_team.defense_area) for player in self.away_team.players]
        return
    @classmethod
    def players_to_starting_positions_within_area(cls, player:InGamePlayer, area:CourtArea):
        # player.position = area.random_position(player_width=player.scaled_dimension.width, player_height=player.scaled_dimension.height) if player.position is None else player.position
        player.position = area.random_position(player_width=player.scaled_dimension.width, player_height=player.scaled_dimension.height)
        # print(f"[RESET][{player.player.name}] {player.position.get()}")
        return
    def update_player_in_possession(self):
        has_possession = False
        for team in self.all_teams:
            for player in self.all_players:
                if player.position is None: continue
                has_possession = pygame.Rect.colliderect(player.get_rect(), self.ball.get_rect())
                # print(f"COLLISION={has_possession} | p={player.player.name} {player.get_rect()} | b={self.ball.get_rect()}")
                if has_possession:
                    self.ball.set_possession(player=player, team=team)
                    break
            if has_possession:
                break
        if not has_possession:
            self.ball.unset_possession()
        self.ball.sync_ball_position_to_possession()
        return
    def update_game_state(self):
        self.update_player_in_possession()
        player_in_possession_name = None if self.ball.player_in_possession is None else self.ball.player_in_possession.player.name
        if self.ball.is_not_in_possession():
            # print(f"Loose Ball Strategy | Possession={player_in_possession_name} | {self.ball.player_in_possession}")
            self.strategy_loose_ball.execute(teams=self.all_teams)
        else:
            # print(f"No Strategy | Possession={player_in_possession_name} | {self.ball.player_in_possession}")
            self.strategy_simple_attack.execute(teams=self.all_teams)
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






