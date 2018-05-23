from ple import PLE

from Joust import Joust
from test_agent import NaiveAgent
import numpy as np

def process_state(state):
    return np.array([state.values()])

game = Joust()

p = PLE(game, fps=30, display_screen=True, state_preprocessor=process_state, force_fps=False, add_noop_action=True)
p.init()
agent1 = NaiveAgent(game.p1_actions, p.getGameStateDims())
agent2 = NaiveAgent(game.p2_actions, p.getGameStateDims())

game.adjustRewards(
    {
        "positive": 10,
        "tick": -0.01,
        "negative": 10,
        "win": 100,
        "loss": -100
    }
)

nb_frames = 1000
reward = 0.0

for f in range(nb_frames):
    if p.game_over():  # check if the game is over
        p.reset_game()

    state = p.getGameState()

    obs = p.getScreenRGB()
    action1 = agent1.pick_action(state)
    action2 = agent2.pick_action(state)
    [reward1,reward2] = p.act([action1, action2])
    if int(reward1) != 0 or int(reward2) != 0:
        print "Reward 1: %f, Reward 2: %f" % (reward1, reward2)
