import pygame
from PIL import Image
from pydantic import BaseModel
from pygame import Surface
from typing import List, Dict, NamedTuple, Tuple, Optional

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



