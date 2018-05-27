#!/usr/bin/env python3
# encoding=utf-8

import matplotlib

# matplotlib.use('agg')
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from Agent import NaiveAgent

from MAS_Checkers import GameEnv

env = GameEnv()
env.reset()

temp = env.render_env()
state = env.get_state()

player1 = env.agent1
player2 = env.agent2

agent1 = NaiveAgent(player1, env.agent1_actions, (3, 18))
agent2 = NaiveAgent(player2, env.agent2_actions, (3, 18))

i = 0
nb_frames = 5000
num_epoch = 100
for epoch in range(num_epoch):
    for f in range(nb_frames):
        temp = env.render_env()
        state = env.get_state()
        # print('temp', temp[0, 0, :])
        # plt.imshow(temp)
        # plt.show(block=False)
        # plt.pause(0.01)
        # plt.clf()
        action1 = agent1.pick_action(state, [], i)
        action2 = agent2.pick_action(state, [], i)
        if env.is_done():
            break
        # Get rewards for every move
        r1, r2 = env.move(action1, action2)
        # print(r1, r2)
        rewards = np.array([r1, r2])
        state = env.get_state()
        agent1.train(rewards, state)
        agent2.train(rewards, state)
        #
        i += 1
    print('Score P1:%d P2:%d' % env.get_final_score())
    env.reset()
