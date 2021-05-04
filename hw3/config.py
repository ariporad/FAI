"""
Some configuration values for the Flappy Bird environment.

NOTE: For all coordinate systems, the origin is in the top left.
"""

from math import ceil

FRAME_HEIGHT = 50
""" The height of a frame, in pixels. """
FRAME_WIDTH = 50
""" The width of a frame, in pixels. """

BORDER_HEIGHT = 2
""" The height of the border along the top and bottom of the frame, in pixels. Made of the same material as pipes. """

DEFAULT_PIPE_HEIGHT = 13
""" A default pipe height to use in deterministic mode, in pixels. 13px results in vertically centered pipes. Does not include the border. """
PIPE_WIDTH = 7
""" The width of each pipe, in pixels. """
PIPE_HORIZONTAL_GAP = 22
""" The horizontal gap between each pair of pipes, in pixels. """
PIPE_VERTICAL_GAP = 20
"""
The vertical gap between the top and bottom halves of each pipe. The height of the bottom half of the pipe grows (or
shrinks) to maintain this gap with whatever the height of the top pipe is. Measured in pixels.
"""

TOP_PIPE_MIN_HEIGHT = 3
""" The minimum height of the top pipe, in pixels. Does not include the border. """
TOP_PIPE_MAX_HEIGHT = 22
""" The maximum height of the top pipe, in pixels. Does not include the border. """

BIRD_WIDTH = 5
""" The width of the bird, in pixels. """
BIRD_HEIGHT = 5
""" The height of the bird, in pixels. """


BIRD_ACCELERATION = 2   # positive, because higher y-coords are visually lower
""" The y acceleration of the bird, in pixels/frame/frame. """
BIRD_TAP_VELOCITY = -5  # negative, because lower y-coords are visually higher
""" When the screen is tapped, the bird's y velocity will be reset to this, in pixels/frame."""

PIPE_VALUE = 1
""" The pixel value of a pipe/border (ie. a pixel that represents a pipe will be set to this) """
BIRD_VALUE = 2
""" The pixel value of the bird (ie. a pixel that represents the bird will be set to this) """

FRAMES_PER_OBSERVATION = 4
""" How many frames should be returned in an observation. """

CRASH_REWARD = -1
""" The neural network's reward for if the bird crashed. """
CLEAR_REWARD = 1
""" The neural network's reward for if the bird successfully cleared a pipe. """
DEFAULT_REWARD = 0
""" The neural network's default reward. """

# Calculated values: the bird always remains horizontally centered
BIRD_LEFT_X = ceil((FRAME_WIDTH - BIRD_WIDTH) / 2)  # rounds to handle even-width frames
BIRD_RIGHT_X = BIRD_LEFT_X + BIRD_WIDTH
