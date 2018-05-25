import logging
import sys

import pygame

from ple import PLE

from Joust import Joust
from test_agent import NaiveAgent
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def process_state(state):
    return np.array([state.values()])


game = Joust(display_screen=True)

p = PLE(game, fps=30, display_screen=False, state_preprocessor=process_state, force_fps=False)
p.init()
player1 = game.player1
player2 = game.player2
agent1 = NaiveAgent(player1, game.p1_actions, p.getGameStateDims(), log_level=logging.INFO)
agent2 = NaiveAgent(player2, game.p2_actions, p.getGameStateDims(), log_level=logging.INFO)

game.adjustRewards(
    {
        "positive": 1,
        "tick": 0.1,
        "negative": 1,
        "win": 1,
        "loss": -10
    }
)

nb_frames = 500
num_epoch = 100
rewards = np.array([0.0, 0.0])
observation = 0

r1_list = []
r2_list = []

for epoch in range(num_epoch):
    for f in range(nb_frames):
        if p.game_over():  # check if the game is over
            p.reset_game()
            break

        state = p.getGameState()

        #obs = p.getScreenRGB()
        action1 = agent1.pick_action(state, rewards, observation)
        action2 = agent2.pick_action(state, rewards, observation)
        rewards = np.array(p.act([action1, action2]))

        new_state = p.getGameState()

        agent1.train(rewards, new_state)
        agent2.train(rewards, new_state)

        observation += 1



    # player 1 rewards
    history1 = agent1.history
    rewards1 = np.array([r[0] for s, a, r in history1])
    #print("P1 reward: %f" % rewards1.sum())
    r1_list.append(rewards1.sum())
    agent1.history = []
    #print("P1 nn weights: ")
    #for layer in agent1.nn.layers:
    #    print(layer.get_weights())

    # player 2 rewards
    history2 = agent2.history
    rewards2 = np.array([r[1] for s, a, r in history2])
    r2_list.append(rewards2.sum())
    #print("P2 reward: %f" % rewards2.sum())
    agent2.history = []
    #print("P2 nn weights: ")
    #for layer in agent2.nn.layers:
        #print(layer.get_weights())

    p.reset_game()
    print("End epoch %i" % epoch)

plt.plot(range(num_epoch), r1_list, color='red')
plt.plot(range(num_epoch), r2_list, color='blue')
plt.grid()
plt.xlabel("Epoch")
plt.ylabel("Reward")
plt.show()

pygame.quit()
sys.exit()
