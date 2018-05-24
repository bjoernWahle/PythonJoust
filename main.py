from ple import PLE

from Joust import Joust
from test_agent import NaiveAgent
import numpy as np

def process_state(state):
    return np.array([state.values()])

game = Joust()

p = PLE(game, fps=30, display_screen=True, state_preprocessor=process_state, force_fps=False)
p.init()
agent1 = NaiveAgent(1, game.p1_actions, p.getGameStateDims())
agent2 = NaiveAgent(2, game.p2_actions, p.getGameStateDims())

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
rewards = np.array([0.0, 0.0])
for epoch in range(10):
    for f in range(nb_frames):
        if p.game_over():  # check if the game is over
            p.reset_game()
            break

        state = p.getGameState()

        obs = p.getScreenRGB()
        action1 = agent1.pick_action(state, rewards)
        action2 = agent2.pick_action(state, rewards)
        rewards[:] = p.act([action1, action2])
        if rewards.astype(int).any() > 0:
            print "Reward 1: %f, Reward 2: %f" % (rewards[0], rewards[1])


    # player 1 rewards
    history1 = agent1.history
    avg_reward1 = np.array([r[0] for (s, a, r) in history1]).mean()
    print("P1 avg reward: %f" % avg_reward1)
    agent1.history = []

    # player 2 rewards
    history2 = agent2.history
    avg_reward2 = np.array([r[1] for (s, a, r) in history2]).mean()
    print("P2 avg reward: %f" % avg_reward2)
    agent2.history = []

