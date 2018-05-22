import sys

import pygame

from ple.games import base
from pygame.constants import K_a, K_d, K_w, K_j, K_l, K_i

from Egg import Egg
from Enemy import Enemy
from Platform import Platform
from Player import Player
from sprites import load_sliced_sprites


class Joust(base.PyGameWrapper):

    def __init__(self, width=900, height=650, config=None):

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

        self.player1 = Player(1, self)
        self.player2 = Player(2, self)
        self.enemies = []
        self.platforms = []
        self.eggs = []

        base.PyGameWrapper.__init__(self, width, height, actions=actions)

        # init sprites
        self._sprites = {
            'digits': load_sliced_sprites(21, 21, "sprites/digits.png"),
            'life': pygame.image.load("sprites/life.png").convert_alpha(),
        }

    def init(self):
        # init players
        self.player1.init()
        self.player2.init()

        # init platforms
        self.platforms = Platform.get_platforms()

        # init enemies
        self.enemies_to_spawn = self.config['enemy_count']
        self.next_enemy_spawn_time = pygame.time.get_ticks() + 2000

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
        return {
            'p1': self.player1.score,
            'p2': self.player2.score
        }

    def step(self, dt):
        if dt > self.next_enemy_spawn_time and self.enemies_to_spawn > 0:
            self._spawn_enemies()
            self.next_enemy_spawn_time = dt + 5000
        self._handle_player_events()

        # update players
        self.player1.update(dt)
        self.player2.update(dt)

        # update platforms
        self._update_platforms()

        # update enemies
        self._update_enemies()

        # update eggs
        self._update_eggs()

        self._draw_screen()

    def get_platforms(self):
        return self.platforms

    def get_enemies(self):
        return self.enemies

    def get_eggs(self):
        return self.eggs

    def _spawn_enemies(self):
        new_enemies = Enemy.generate_enemies(self, 2)
        self.enemies_to_spawn -= 2
        self.enemies.extend(new_enemies)

    def add_egg(self, x, y, xspeed, yspeed):
        self.eggs.append(Egg(x, y, xspeed, yspeed))

    def end(self):
        pygame.quit()
        sys.exit()

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
                self.end()

            if event.type == pygame.KEYDOWN:
                key = event.key

                self._handle_key_event(key)

    def _handle_key_event(self, key):
        if key == pygame.constants.K_ESCAPE:
            self.end()
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
        # draw players
        self._draw_players()

        # draw enemies
        self._draw_enemies()

        # draw eggs
        self._draw_eggs()

        # draw platforms
        self._draw_platforms()

        # draw scores and lives
        self._draw_scores()
        self._draw_lives()

    def _update_platforms(self):
        for platform in self.platforms:
            platform.update()

    def _update_enemies(self):
        for enemy in self.enemies:
            enemy.update()

    def _update_eggs(self):
        for egg in self.eggs:
            egg.update()

    def _draw_players(self):
        self._draw_player(self.player1)
        self._draw_player(self.player1)

    def _draw_enemies(self):
        for enemy in self.enemies:
            self._draw_enemy(enemy)

    def _draw_eggs(self):
        for egg in self.eggs:
            self._draw_egg(egg)

    def _draw_platforms(self):
        for platform in self.platforms:
            self._draw_platform(platform)

    def _draw_scores(self):
        self._draw_player_score(self.player1)
        self._draw_player_score(self.player2)

    def _draw_lives(self):
        self._draw_player_lives(self.player1)
        self._draw_player_lives(self.player2)

    def _draw_player(self, player):
        self.screen.blit(player.image, player.rect.center)

    def _draw_enemy(self, enemy):
        self.screen.blit(enemy.image, enemy.rect.center)

    def _draw_egg(self, egg):
        self.screen.blit(egg.image, egg.rect.center)

    def _draw_platform(self, platform):
        self.screen.blit(platform.image, platform.rect.center)
