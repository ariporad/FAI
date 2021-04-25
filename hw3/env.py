from typing import *

from math import ceil
from dataclasses import dataclass

import numpy as np

FRAME_WIDTH = 50
FRAME_HEIGHT = 50
BORDER_HEIGHT = 2

PIPE_WIDTH = 7
PIPE_VERTICAL_GAP = 20
PIPE_HORIZONTAL_GAP = 22
TOP_PIPE_MIN_HEIGHT = 5
TOP_PIPE_MAX_HEIGHT = 25

BIRD_WIDTH = 5
BIRD_HEIGHT = 5

PIPE_VALUE = 1
BIRD_VALUE = 2


# For all coordinate systems, the origin is the upper left

@dataclass
class State:
    pipes: List[Tuple[int, int]]
    """
    List of all pipes.
    
    Each pipe is represented by the x-position of its leftmost edge and the height of the top pipe.
    """
    
    bird_height: int
    """
    The y-coordinate of the top edge of the bird. (The bird's x-coordinate is always centered)
    """
    
    bird_velocity: int
    """
    The y velocity of the bird, in pixels per frame. Increments by 2 each frame. Reset to -5 when screen is tapped.
    
    NOTE: Weird signage is because higher y values are visually lower
    """
    
    @property
    def done(self):
        pass
    
    @property
    def render(self):
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH), dtype=np.uint8)
        
        frame[0:BORDER_HEIGHT, :] = PIPE_VALUE
        frame[-BORDER_HEIGHT:, :] = PIPE_VALUE

        for left_x, top_height in self.pipes:
            upper_bottom_y = BORDER_HEIGHT + top_height
            lower_top_y = upper_bottom_y + PIPE_VERTICAL_GAP
            frame[0:upper_bottom_y, left_x:(left_x + PIPE_WIDTH)] = PIPE_VALUE
            frame[lower_top_y:, left_x:(left_x + PIPE_WIDTH)] = PIPE_VALUE
        
        bird_left_x = ceil((FRAME_WIDTH - BIRD_WIDTH) / 2)
        
        frame[self.bird_height:(self.bird_height + BIRD_HEIGHT), bird_left_x:(bird_left_x + BIRD_WIDTH)] = BIRD_VALUE
        
        return frame
    

class FlappyEnv(object):
    def __init__(self, use_pipes=False, deterministic=False):
        self.use_pipes = use_pipes
        self.deterministic = deterministic

    def reset(self):
        # This should completely reset your environment and return a new, fresh observation
        # This is like quitting and starting a new game.
        # The observation should be a 3D list of integers of dimension 4 x 50 x 50
        observation = None
        return observation

    def step(self, action):
        # The input `action` is an integer in {0, 1} representing the action of the agent
        # 0 is doing nothing, 1 is "tapping the screen."
        # The observation should be a 3D list of integers of dimension 4 x 50 x 50
        # The reward should be a scalar value in {-1.0, 0, or 1.0}
        # done should be a boolean indicating whether the bird has crashed
        observation = None
        reward = None
        done = None

        return observation, reward, done

