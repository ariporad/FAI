from typing import *

from math import ceil, floor
from dataclasses import dataclass
from random import Random

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

FRAMES_PER_OBSERVATION = 4


# For all coordinate systems, the origin is the upper left

@dataclass
class State:
    prev: Optional['State']
    """
    The state that proceeded this one.
    """
    
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

    def next(self, tap, get_pipe_height):
        new_pipes = []
        
        for left_x, top_height in self.pipes:
            # Wrap pipes around
            if left_x <= -PIPE_WIDTH:
                left_x = FRAME_WIDTH + 1 # +1 so we have a frame with it offscreen
                top_height = get_pipe_height()  # re-randomize the height
            
            new_pipes.append((left_x - 1, top_height))
        
        velocity = -5 if tap else (self.bird_velocity + 2)
        
        return State(prev=self, pipes=new_pipes, bird_height=(self.bird_height + self.bird_velocity), bird_velocity=velocity)

    @property
    def done(self):
        pass
    
    @property
    def frame(self):
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH), dtype=np.uint8)
        
        frame[0:BORDER_HEIGHT, :] = PIPE_VALUE
        frame[-BORDER_HEIGHT:, :] = PIPE_VALUE

        for left_x, top_height in self.pipes:
            upper_bottom_y = BORDER_HEIGHT + top_height
            lower_top_y = upper_bottom_y + PIPE_VERTICAL_GAP
            frame[0:upper_bottom_y, max(left_x, 0):min(FRAME_WIDTH - 1, left_x + PIPE_WIDTH)] = PIPE_VALUE
            frame[lower_top_y:, max(left_x, 0):min(FRAME_WIDTH - 1, left_x + PIPE_WIDTH)] = PIPE_VALUE
        
        bird_left_x = ceil((FRAME_WIDTH - BIRD_WIDTH) / 2)
        
        frame[self.bird_height:(self.bird_height + BIRD_HEIGHT), bird_left_x:(bird_left_x + BIRD_WIDTH)] = BIRD_VALUE
        
        return frame
    
    @property
    def observation(self):
        observation = np.empty((FRAMES_PER_OBSERVATION, FRAME_HEIGHT, FRAME_WIDTH), dtype=np.uint8)
        cur_state = self
        
        for i in range(FRAMES_PER_OBSERVATION):
            observation[i] = cur_state.frame
            cur_state = cur_state.prev if cur_state.prev else cur_state # for the starting frame, just give it 4 times
            
        return observation
        
    

class FlappyEnv(object):
    def __init__(self, use_pipes=False, deterministic=False):
        self.use_pipes = use_pipes
        self.deterministic = deterministic
        self.state = None
        self.random = Random(1 if deterministic else None)
        
        self.reset()
        
    def generate_pipe_height(self):
        return self.random.randrange(TOP_PIPE_MIN_HEIGHT, TOP_PIPE_MAX_HEIGHT)

    def reset(self):
        # This should completely reset your environment and return a new, fresh observation
        # This is like quitting and starting a new game.
        # The observation should be a 3D list of integers of dimension 4 x 50 x 50

        pipes = []

        if self.use_pipes:
            pipes = [
                (FRAME_HEIGHT, self.generate_pipe_height()),
                (FRAME_HEIGHT + PIPE_WIDTH + PIPE_HORIZONTAL_GAP, self.generate_pipe_height())
            ]

        self.state = State(None, pipes, floor(FRAME_HEIGHT / 2), 0)
        
        return self.state.observation

    def step(self, action):
        # The input `action` is an integer in {0, 1} representing the action of the agent
        # 0 is doing nothing, 1 is "tapping the screen."
        # The observation should be a 3D list of integers of dimension 4 x 50 x 50
        # The reward should be a scalar value in {-1.0, 0, or 1.0}
        # done should be a boolean indicating whether the bird has crashed
        reward = None
        done = None
        
        self.state = self.state.next(action, lambda: self.generate_pipe_height())

        return self.state.observation, reward, done

