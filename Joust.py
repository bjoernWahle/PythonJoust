import sys

import pygame

from ple.games import base
from pygame.constants import K_a, K_d, K_w, K_j, K_l, K_i

from Egg import Egg
from Enemy import Enemy
from Platform import Platform
from Player import Player
from sprites import load_sliced_sprites, load_sprite
import numpy as np


# TODO add lava (see joust.py)
# TODO add player-player collisions
# TODO complete getGameState method
# TODO get scores from self.rewards instead of config (needs to be figured out since no documentation about that)
# TODO use with ple-gym (https://github.com/lusob/gym-ple)
# TODO figure out how headless / stateless works
class Joust(base.PyGameWrapper):

    def __init__(self, width=900, height=650, config=None):
        pygame.display.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        if config is None:
            config = {
                "enemy_kill_score": 10,
                "egg_collect_score": 10,
                "player_kill_score": 0,
                "enemy_count": 6,
                "max_speed": 10
            }
        self.config = config

        actions = {
            "p1_up": K_w,
            "p1_left": K_a,
            "p1_right": K_d,
            "p2_up": K_i,
            "p2_left": K_j,
            "p2_right": K_l
        }

        base.PyGameWrapper.__init__(self, width, height, actions=actions)
        self.rng = np.random.RandomState(24)
        self.screen = pygame.display.set_mode(self.getScreenDims(), 0, 32)

        self.player1 = Player(1, self)
        self.player2 = Player(2, self)


        # init sprites
        self._sprites = {
            'digits': load_sliced_sprites(21, 21, "digits.png"),
            'life': load_sprite("life.png", convert_alpha=True),
        }

    def init(self):
        # init players
        self.player1.init()
        self.player2.init()
        self.players = pygame.sprite.RenderUpdates()
        self.players.add([self.player1, self.player2])

        # init platforms
        self.platforms = pygame.sprite.RenderUpdates()
        self.platforms.add(Platform.get_platforms())

        # init enemies
        self.enemies = pygame.sprite.RenderUpdates()
        self.enemies_to_spawn = self.config['enemy_count']
        self.next_enemy_spawn_time = None

        # init eggs
        self.eggs = pygame.sprite.RenderUpdates()

    def getGameState(self):

        state = {
            "player1_x": self.player1.x,
            "player1_xspeed": self.player1.x_speed,
            "player2_x": self.player1.x,
            "player2_xspeed": self.player1.x_speed,

            # TODO add enemies and eggs
        }

        return state

    def game_over(self):
        if self.player1.lives == 0 and self.player2.lives == 0:
            return True
        if len(self.enemies) > 0:
            for enemy in self.enemies:
                if enemy.alive:
                    return False
            return True
        return False

    def getScore(self):
        return np.array([self.player1.score, self.player2.score])

    def step(self, dt):
        current_time = pygame.time.get_ticks()
        if self.next_enemy_spawn_time is None:
            self.next_enemy_spawn_time = current_time + 2000
        if current_time > self.next_enemy_spawn_time and self.enemies_to_spawn > 0:
            self._spawn_enemies()
            self.next_enemy_spawn_time = current_time + 5000
        self._handle_player_events()

        # update players
        self.players.update(dt)

        # update platforms
        self._update_platforms()

        # update enemies
        self._update_enemies(dt)

        # update eggs
        self._update_eggs(dt)

        # draw updated screen
        self._draw_screen()

    def get_platforms(self):
        return self.platforms

    def get_enemies(self):
        return self.enemies

    def get_eggs(self):
        return self.eggs

    def add_egg(self, x, y, xspeed, yspeed):
        self.eggs.add(Egg(x, y, xspeed, yspeed))

    def end_game(self):
        sys.exit()

    def _spawn_enemies(self):
        new_enemies = Enemy.generate_enemies(self, 2)
        self.enemies_to_spawn -= 2
        self.enemies.add(new_enemies)

    def _draw_player_lives(self, player):
        if player.id == 1:
            startx = 375
        else:
            startx = 612
        for num in range(player.lives):
            x = startx + num * 20
            self.screen.blit(self._sprites['life'], [x, 570])

    def _draw_player_score(self, player):
        if player.id == 1:
            x = 353
        else:
            x = 590
        self.screen.blit(self._sprites['digits'][player.score % 10], [x, 570])
        self.screen.blit(self._sprites['digits'][(player.score % 100) // 10], [x - 18, 570])
        self.screen.blit(self._sprites['digits'][(player.score % 1000) // 100], [x - 2 * 18, 570])
        self.screen.blit(self._sprites['digits'][(player.score % 10000) // 1000], [x - 3 * 18, 570])
        self.screen.blit(self._sprites['digits'][(player.score % 100000) // 10000], [x - 4 * 18, 570])
        self.screen.blit(self._sprites['digits'][(player.score % 1000000) // 100000], [x - 5 * 18, 570])

    def _handle_player_events(self):
        self.dx = 0.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end_game()

            if event.type == pygame.KEYDOWN:
                key = event.key

                self._handle_key_event(key)

    def _handle_key_event(self, key):
        if key == pygame.constants.K_ESCAPE:
            self.end_game()
        if key == self.actions['p1_up']:
            self.player1.up()
        if key == self.actions['p2_up']:
            self.player2.up()
        if key == self.actions['p1_left']:
            self.player1.left()
        if key == self.actions['p2_left']:
            self.player2.left()
        if key == self.actions['p1_right']:
            self.player1.right()
        if key == self.actions['p2_right']:
            self.player2.right()

    def _draw_screen(self):
        self.screen.fill((0,0,0))
        rects = []
        # draw players
        rects.extend(self._draw_players())

        # draw enemies
        rects.extend(self._draw_enemies())

        # draw eggs
        rects.extend(self._draw_eggs())

        # draw platforms
        rects.extend(self._draw_platforms())

        # draw scores and lives
        self._draw_scores()
        self._draw_lives()

        pygame.display.update(rects)

    def _update_platforms(self):
        return self.platforms.update()

    def _update_enemies(self, dt):
        return self.enemies.update(dt)

    def _update_eggs(self, dt):
        return self.eggs.update(dt, self.platforms)


    def _draw_players(self):
        return self.players.draw(self.screen)

    def _draw_enemies(self):
        return self.enemies.draw(self.screen)

    def _draw_eggs(self):
        return self.eggs.draw(self.screen)

    def _draw_platforms(self):
        return self.platforms.draw(self.screen)

    def _draw_scores(self):
        self._draw_player_score(self.player1)
        self._draw_player_score(self.player2)

    def _draw_lives(self):
        self._draw_player_lives(self.player1)
        self._draw_player_lives(self.player2)
