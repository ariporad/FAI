from typing import *

from math import floor
from collections import deque
from dataclasses import dataclass
from random import randrange

import numpy as np

from config import *

# NOTE: for all coordinate systems, the origin is the upper left

@dataclass
class Frame:
    """
    One frame of the game. Immutable.
    """
    
    pipes: List[Tuple[int, int]]
    """
    List of all pipes.
    
    Each pipe is represented by a tuple with  the x-position of its left edge and the height of the top half (in that
    order).
    """
    
    bird_height: int
    """
    The y-coordinate of the top edge of the bird. (The bird's x-coordinate is always centered.)
    """
    
    bird_velocity: int
    """
    The y velocity of the bird, in pixels per frame. Increments by BIRD_ACCELERATION each frame. Reset to
    BIRD_TAP_VELOCITY when screen is tapped.
    
    NOTE: Weird signage is because higher y values are visually lower.
    """

    def next(self, tap, get_pipe_height):
        """
        Generate the frame that succeeds this one.
        
        NOTE: This does *not* check for if the game has ended/the bird has crashed. This means it's possible to produce
              illegal states if you just keep calling next().
        
        :param tap: Was the screen tapped? If so, the bird's velocity will reset, otherwise it will decrease.
        :param get_pipe_height: A function which randomly generates the height of the next pipe. Only called when a new
                                pipe is created.
        """
        new_pipes = []
        
        for left_x, top_height in self.pipes:
            # Wrap pipes around
            if left_x <= -PIPE_WIDTH:
                left_x = FRAME_WIDTH + 1 # +1 so we have a frame with it offscreen
                top_height = get_pipe_height()  # re-randomize the height
            
            new_pipes.append((left_x - 1, top_height))
        
        velocity = BIRD_TAP_VELOCITY if tap else (self.bird_velocity + BIRD_ACCELERATION)
        
        return Frame(pipes=new_pipes, bird_height=(self.bird_height + self.bird_velocity), bird_velocity=velocity)
    
    @property
    def done(self):
        """
        Is the game over? Returns true if the bird has hit a pipe (or a wall).
        
        NOTE: This function only detects if the bird died _on this frame_. If you ignore the value of this function and
              keep calling .next(), subsequent states' .done will be False.
        """
        return self.reward == CRASH_REWARD

    @property
    def reward(self):
        """
        The neural network's reward for this frame. CRASH_REWARD if the bird hit a pipe on this frame, CLEAR_REWARD if
        the bird just cleared a pipe on this frame, and DEFAULT_REWARD otherwise.
        """
        if self.bird_height < BORDER_HEIGHT or (BIRD_HEIGHT + self.bird_height) >= (FRAME_HEIGHT - BORDER_HEIGHT - 1):
            return CRASH_REWARD
        
        for left_x, top_height in self.pipes:
            right_x = left_x + PIPE_WIDTH
            overlaps_x = left_x <= BIRD_RIGHT_X and right_x >= BIRD_LEFT_X
            hit_top_y = self.bird_height <= (BORDER_HEIGHT + top_height)
            hit_bottom_y = (self.bird_height + BIRD_HEIGHT) >= (BORDER_HEIGHT + top_height + PIPE_VERTICAL_GAP)
            
            if overlaps_x and (hit_top_y or hit_bottom_y):  # did we crash?
                return CRASH_REWARD
            elif right_x + 1 == BIRD_LEFT_X:  # did we just make it past a pipe?
                return CLEAR_REWARD
            
        return DEFAULT_REWARD
            
    def draw(self):
        """
        Render this Frame to a 2D array of numbers representing the screen of the game.
        
        :returns: a NumPy array, because it has way more convenient multi-dimensional indexing than a normal List.
        """
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH), dtype=np.uint8)
        
        frame[0:BORDER_HEIGHT, :] = PIPE_VALUE
        frame[-BORDER_HEIGHT:, :] = PIPE_VALUE

        for left_x, top_height in self.pipes:
            upper_bottom_y = BORDER_HEIGHT + top_height
            lower_top_y = upper_bottom_y + PIPE_VERTICAL_GAP
            frame[0:upper_bottom_y, max(left_x, 0):min(FRAME_WIDTH - 1, left_x + PIPE_WIDTH)] = PIPE_VALUE
            frame[lower_top_y:, max(left_x, 0):min(FRAME_WIDTH - 1, left_x + PIPE_WIDTH)] = PIPE_VALUE
        
        frame[self.bird_height:(self.bird_height + BIRD_HEIGHT), BIRD_LEFT_X:(BIRD_LEFT_X + BIRD_WIDTH)] = BIRD_VALUE
        
        return frame
    
    
class FlappyEnv(object):
    """
    A Flappy Bird environment.
    """
    
    def __init__(self, use_pipes=False, deterministic=False):
        """
        Create a Flappy Bird environment
        :param use_pipes: should any pipes be created/rendered?
        :param deterministic: should the game be deterministic? If so, all pipes will have equal top and bottom lengths.
                              Has no effect if use_pipes is False.
        """
        self.use_pipes = use_pipes
        self.frames = deque(maxlen=FRAMES_PER_OBSERVATION)
        self.generate_pipe_height = lambda: DEFAULT_PIPE_HEIGHT if deterministic else  randrange(TOP_PIPE_MIN_HEIGHT, TOP_PIPE_MAX_HEIGHT)
        
        self.reset()
        
    def reset(self):
        """
        Reset the environment to its starting configuration.
        
        This is exactly equivalent to quitting and starting a new game.
        
        :returns: an observation of the freshly-reset game
        """
        self.frames.clear()

        pipes = []
        if self.use_pipes:
            pipes = [
                (FRAME_HEIGHT, self.generate_pipe_height()),
                (FRAME_HEIGHT + PIPE_WIDTH + PIPE_HORIZONTAL_GAP, self.generate_pipe_height())
            ]
            
        frame = Frame(pipes, floor(FRAME_HEIGHT / 2), 0)
        
        while len(self.frames) < FRAMES_PER_OBSERVATION:
            self.frames.append(frame)
        
        return self.observe()

    def observe(self):
        """
        Generate an observation of the current state, which is a FRAMES_PER_OBSERVATION x FRAME_HEIGHT x FRAME_WIDTH
        (usually 4x50x50) NumPy array representing the four most recent frames of the game, in chronological order.
        """
        assert len(self.frames) == FRAMES_PER_OBSERVATION, "sanity check failed: incorrect number of states"
        
        observation = np.array([frame.draw() for frame in self.frames], dtype=np.uint8)
        
        return observation

    def step(self, action):
        """
        Advance the game by one timestep/frame, returning a new observation.
        
        :param action: an integer in {0, 1} representing the action of the player, where 1 is a tap and 0 is nothing
        :return: a tuple with (in order), an observation, the neural net's reward, and if the game is over
        """
        
        new_frame = self.frames[-1].next(bool(action), self.generate_pipe_height)
        
        self.frames.append(new_frame)

        return self.observe().tolist(), new_frame.reward, new_frame.done

