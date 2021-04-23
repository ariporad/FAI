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

