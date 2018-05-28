import sys

import pygame

from ple.games import base
from pygame.constants import K_a, K_d, K_w, K_j, K_l, K_i, K_F5, K_F15

from Egg import Egg
from Enemy import Enemy
from Platform import Platform
from Player import Player
from sprites import load_sliced_sprites, load_sprite
import numpy as np


# TODO complete getGameState method
class Joust(base.PyGameWrapper):

    def __init__(self, width=900, height=650, config=None, display_screen=True):
        pygame.display.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        self.display_screen = display_screen

        if config is None:
            config = {
                "enemy_count": 0,
                "max_speed": 10,
                "initial_lives" : 5,
            }
        self.config = config

        self.p1_actions = {
            "p1_up": K_w,
            "p1_left": K_a,
            "p1_right": K_d,
            "p1_noop": K_F5
        }

        self.p2_actions = {
            "p2_up": K_i,
            "p2_left": K_j,
            "p2_right": K_l,
            "p2_noop": K_F15
        }

        actions = {}
        actions.update(self.p1_actions)
        actions.update(self.p2_actions)

        base.PyGameWrapper.__init__(self, width, height, actions=actions)

        self.rng = np.random.RandomState(24)
        self.screen = pygame.display.set_mode(self.getScreenDims(), 0, 32)
        self.clear_surface = self.screen.copy()

        self.player1 = Player(1, self, initial_lives=self.config['initial_lives'])
        self.player2 = Player(2, self, initial_lives=self.config['initial_lives'])


        # init sprites
        self._sprites = {
            'digits': load_sliced_sprites(21, 21, "digits.png"),
            'red_digits' : load_sliced_sprites(21, 21, 'red_digits.png'),
            'life': load_sprite("life.png", convert_alpha=True),
        }

    def init(self):
        if self.display_screen:
            self.screen.fill((0, 0, 0))
            pygame.display.update()
        # init players
        self.player1.init()
        self.player2.init()
        self.player1_r = pygame.sprite.RenderUpdates()
        self.player2_r = pygame.sprite.RenderUpdates()
        self.player1_r.add([self.player1])
        self.player2_r.add([self.player2])

        # init platforms
        self.platforms = pygame.sprite.RenderUpdates()
        self.platforms.add(Platform.get_platforms())

        # init enemies
        self.enemies = pygame.sprite.RenderUpdates()
        self.enemies_to_spawn = self.config['enemy_count']
        self.next_enemy_spawn_time = None

        # init eggs
        self.eggs = pygame.sprite.RenderUpdates()

        # draw updated screen
        if self.display_screen:
            self._draw_screen()

    def getGameState(self):

        state = {
            "player1_x": self.player1.x,
            "player1_x_speed": self.player1.x_speed,
            "player1_y": self.player1.y,
            "player1_y_speed": self.player1.y_speed,
            #"player1_flap": self.player1.flap,
            "player2_x": self.player2.x,
            "player2_x_speed": self.player2.x_speed,
            "player2_y": self.player2.y,
            "player2_y_speed": self.player2.y_speed,
            #"player2_flap": self.player2.flap,
        }
        return state

    def game_over(self):
        if self.player1.lives == 0 and self.player2.lives == 0:
            return True
        if len(self.enemies) > 0:
            for enemy in self.enemies:
                if enemy.alive:
                    return False
            self.player1.score += self.rewards['win']
            self.player2.score += self.rewards['win']
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
        self.player1_r.update(dt)
        self.player2_r.update(dt)

        # update platforms
        self._update_platforms()

        # update enemies
        self._update_enemies(dt)

        # update eggs
        self._update_eggs(dt)

        # draw updated screen
        if self.display_screen:
            self._draw_screen()

    def get_platforms(self):
        return self.platforms

    def get_enemies(self):
        return self.enemies

    def get_eggs(self):
        return self.eggs

    def get_other_players(self,id):
        if id == 1:
            return self.player2_r
        else:
            return self.player1_r


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

        score = int(player.score)
        digit_sprites = self._sprites['digits']
        if score < 0.0:
            digit_sprites = self._sprites['red_digits']
            score = score * -1

        self.screen.blit(digit_sprites[score % 10], [x, 570])
        self.screen.blit(digit_sprites[(score % 100) // 10], [x - 18, 570])
        self.screen.blit(digit_sprites[(score % 1000) // 100], [x - 2 * 18, 570])
        self.screen.blit(digit_sprites[(score % 10000) // 1000], [x - 3 * 18, 570])
        self.screen.blit(digit_sprites[(score % 100000) // 10000], [x - 4 * 18, 570])
        self.screen.blit(digit_sprites[(score % 1000000) // 100000], [x - 5 * 18, 570])

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
        rects = []

        # draw players
        rects.extend(self._draw_players(1))
        rects.extend(self._draw_players(2))

        # draw enemies
        rects.extend(self._draw_enemies())

        # draw eggs
        rects.extend(self._draw_eggs())
        # draw lava
        rects.extend(self._draw_lava())
        # draw platforms
        rects.extend(self._draw_platforms())



        # draw scores and lives
        self._draw_scores()
        self._draw_lives()

        pygame.display.update(rects)
        for ru in [self.player1_r, self.player2_r, self.platforms, self.enemies, self.eggs]:
            ru.clear(self.screen, self.clear_surface)

    def _update_platforms(self):
        return self.platforms.update()

    def _update_enemies(self, dt):
        return self.enemies.update(dt)

    def _update_eggs(self, dt):
        return self.eggs.update(dt, self.platforms)


    def _draw_players(self,id):
        if id == 1:
            return self.player1_r.draw(self.screen)
        else:
            return self.player2_r.draw(self.screen)


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

    def _draw_lava(self):
        lava_rect = [0, 600, 900, 50]
        lava_rect2 = [0, 620, 900, 30]
        return [pygame.draw.rect(self.screen, (255, 0, 0), lava_rect), pygame.draw.rect(self.screen, (255, 0, 0), lava_rect2)]
