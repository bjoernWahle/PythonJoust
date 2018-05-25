import logging
import sys

import pygame

from ple import PLE
from sklearn.preprocessing import MinMaxScaler

from Joust import Joust
from test_agent import NaiveAgent
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sklearn

y_speed_scaler = MinMaxScaler((-1, 1))
x_speed_scaler = MinMaxScaler((-1, 1))
x_scaler = MinMaxScaler((-1, 1))
y_scaler = MinMaxScaler((-1, 1))

x_speed_scaler.fit(np.array([-10, 10]).reshape(-1,1))
y_speed_scaler.fit(np.array([-10, 10]).reshape(-1,1))
x_scaler.fit(np.array([0, 900]).reshape(-1,1))
y_scaler.fit(np.array([0, 600]).reshape(-1,1))


def process_state(state):
    return np.array([
        x_scaler.transform(state['player1_x'])[0],
        x_scaler.transform(state['player2_x'])[0],
        y_scaler.transform(state['player1_y'])[0],
        y_scaler.transform(state['player2_y'])[0],
        y_speed_scaler.transform(state['player1_y_speed'])[0],
        y_speed_scaler.transform(state['player2_y_speed'])[0],
        x_speed_scaler.transform(state['player1_x_speed'])[0],
        x_speed_scaler.transform(state['player2_x_speed'])[0]
    ]).reshape(1, -1)


game = Joust(display_screen=True)

p = PLE(game, fps=30, display_screen=False, state_preprocessor=process_state, force_fps=False)
p.init()
player1 = game.player1
player2 = game.player2
agent1 = NaiveAgent(player1, game.p1_actions, p.getGameStateDims(), log_level=logging.INFO)
agent2 = NaiveAgent(player2, game.p2_actions, p.getGameStateDims(), log_level=logging.INFO)

game.adjustRewards(
    {
        "positive": 0.1,
        "tick": 0.001,
        "negative": -0.1,
        "win": 1,
        "loss": -1
    }
)

nb_frames = 500
num_epoch = 100
rewards = np.array([0.0, 0.0])
observation = 0
train_start = 1000

r1_list = []
r2_list = []

for epoch in range(num_epoch):
    for f in range(nb_frames):
        if p.game_over():  # check if the game is over
            p.reset_game()
            break

        state = p.getGameState()

        # obs = p.getScreenRGB()
        action1 = agent1.pick_action(state, rewards, observation)
        action2 = agent2.pick_action(state, rewards, observation)
        rewards = np.array(p.act([action1, action2]))
        agent1.store_reward(rewards)
        agent2.store_reward(rewards)

        new_state = p.getGameState()

        if observation == train_start:
            print("Start training!")
            agent1.exploration_prob = agent1.exploration_prob_train
            agent2.exploration_prob = agent2.exploration_prob_train
            print("Player 1 has learnt:")
            for layer in agent1.nn.layers:
                print(layer.get_weights())
            print("Player 2 has learnt:")
            for layer in agent2.nn.layers:
                print(layer.get_weights())

        if observation >= train_start:
            agent1.train(rewards, new_state)
            agent2.train(rewards, new_state)

        observation += 1

    # player 1 rewards
    final_reward1 = np.array([agent1.rewards]).sum()
    print("Player 1: %f" % final_reward1)
    r1_list.append(final_reward1)
    agent1.rewards = []

    # player 2 rewards
    final_reward2 = np.array([agent2.rewards]).sum()
    print("Player 2: %f" % final_reward2)
    r2_list.append(final_reward2)
    agent2.rewards = []

    if agent1.player.lives > 0:
        agent1.replay_memories(game.rewards['win'])
    else:
        agent1.replay_memories(game.rewards['loss'])
    if agent2.player.lives > 0:
        agent2.replay_memories(game.rewards['win'])
    else:
        agent2.replay_memories(game.rewards['loss'])

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
