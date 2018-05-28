import logging
import sys

import pygame

from ple import PLE

from Joust import Joust
from rule_base_agent import RuleBasedAgent
import numpy as np

def process_state(state):
    return np.array([
        state['player1_x'],
        state['player1_x_speed'],
        state['player1_y'],
        state['player1_y_speed'],
        state['player2_x'],
        state['player2_x_speed'],
        state['player2_y'],
        state['player2_y_speed'],
    ]).reshape(1, -1)[0]


game = Joust(display_screen=True)

p = PLE(game, fps=30, display_screen=False, state_preprocessor=process_state, force_fps=False)
p.init()
player1 = game.player1
player2 = game.player2
agent1 = RuleBasedAgent(player1, game.p1_actions, cooperating=True, log_level=logging.WARN)
agent2 = RuleBasedAgent(player2, game.p2_actions, cooperating=False, log_level=logging.WARN)

game.adjustRewards(
    {
        "positive": 10.0,
        "tick": 0.0,
        "defect": 5,
        "negative": -5,
        "cooperative": 15,
        "win": 0,
        "loss": 0,
    }
)

nb_frames = 500
num_epoch = 100
rewards = np.array([0.0, 0.0])
observation = 0
train_start = 1000

r1_list = []
r2_list = []

p1_other_player_kills = []
p2_other_player_kills = []
p1_enemy_kills = []
p2_enemy_kills = []
cooperating_victories = 0
p1_victories = 0
p2_victories = 0

for epoch in range(num_epoch):
    for f in range(nb_frames):
        if p.game_over():  # check if the game is over
            break

        state = p.getGameState()

        # obs = p.getScreenRGB()
        action1 = agent1.pick_action(state, rewards, observation)
        action2 = agent2.pick_action(state, rewards, observation)
        rewards = np.array(p.act([action1, action2]))
        agent1.store_reward(rewards)
        agent2.store_reward(rewards)

        observation += 1

    # player 1 rewards
    final_reward1 = player1.score
    r1_list.append(final_reward1)
    agent1.rewards = []

    # player 2 rewards
    final_reward2 = player2.score
    r2_list.append(final_reward2)
    agent2.rewards = []

    # save player kill counts
    p1_other_player_kills.append(agent1.player.other_player_kill_count)
    p2_other_player_kills.append(agent2.player.other_player_kill_count)
    p1_enemy_kills.append(agent1.player.enemy_kill_count)
    p2_enemy_kills.append(agent2.player.enemy_kill_count)

    if game.was_cooperative_victory():
        cooperating_victories += 1

    if player1.has_won:
        p1_victories += 1
    if player2.has_won:
        p2_victories += 1

    p.reset_game()
    print("End epoch %i" % (epoch+1))

# plt.plot(range(num_epoch), r1_list, color='red')
# plt.plot(range(num_epoch), r2_list, color='blue')
# plt.grid()
# plt.title("Reward evolution")
# plt.xlabel("Epoch")
# plt.ylabel("Reward")
# plt.show()

print("Player 1 was cooperating: %r" % agent1.cooperating)
print("Player 2 was cooperating: %r" % agent2.cooperating)

print("Player 1 killed player 2 %i times" % np.sum(np.array(p1_other_player_kills)))
print("Player 2 killed player 1 %i times" % np.sum(np.array(p2_other_player_kills)))

print("Player 1 killed %i enemies" % np.sum(np.array(p1_enemy_kills)))
print("Player 2 killed %i enemies" % np.sum(np.array(p2_enemy_kills)))
print("Total number of cooperative victories: %i" % cooperating_victories)
print("Total number of Player 1 victories: %i" % p1_victories)
print("Total number of Player 2 victories: %i" % p2_victories)

print("Average score Player 1: %f" % np.array(r1_list).mean())
print("Average score Player 2: %f" % np.array(r2_list).mean())

pygame.quit()
sys.exit()
