from ple import PLE

from Joust import Joust
from test_agent import NaiveAgent

game = Joust()

p = PLE(game, fps=30, display_screen=True, force_fps=False, add_noop_action=True)
p.init()
myAgent = NaiveAgent(p.getActionSet())

nb_frames = 1000
reward = 0.0

for f in range(nb_frames):
    if p.game_over():  # check if the game is over
        p.reset_game()

    obs = p.getScreenRGB()
    action = myAgent.pickAction(reward, obs)
    reward = p.act(action)
