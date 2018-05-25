import random

import pygame

from sprites import load_sliced_sprites


class Player(pygame.sprite.Sprite):

    def __init__(self, id, game, spawn_x=None, spawn_y=None, initial_lives=3):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.id = id
        self.game = game
        self.initial_lives = initial_lives
        if spawn_x is None or spawn_y is None:
            if self.id == 1:
                spawn_x = 600
                spawn_y = 450
            else:
                spawn_x = 600
                spawn_y = 450
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.images = load_sliced_sprites(60, 60, "playerMounted.png")
        self.unmounted_images = load_sliced_sprites(60, 60, "unmounted.png")
        self.spawnimages = load_sliced_sprites(60, 60, "spawn1.png")
        self.player_channel = pygame.mixer.Channel(0)
        self.flapsound = pygame.mixer.Sound("audio/joustflaedit.wav")
        self.skidsound = pygame.mixer.Sound("audio/joustski.wav")
        self.bumpsound = pygame.mixer.Sound("audio/joustthu.wav")
        self.reset_actions()
        self.init()

    def init(self):
        self.reset_actions()
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.frame_num = 1
        self.image = self.images[self.frame_num]
        self.rect = self.image.get_rect()
        self.lives = self.initial_lives
        self.next_anim_time = 0
        self.targetx_speed = 10
        self.x_speed = 0
        self.y_speed = 0
        self.facing_right = True
        self.flap = False
        self.walking = True
        self.spawning = True
        self.alive = 2
        self.score = 0

    def reset_actions(self):
        self.actions = {
            'up': False,
            'left': False,
            'right' : False
        }

    def up(self):
        self.actions['up'] = True

    def left(self):
        self.actions['left'] = True

    def right(self):
        self.actions['right'] = True

    # TODO move to game
    def check_collisions(self, enemies, platforms, egg_list):
        # check for enemy collision
        collided_birds = pygame.sprite.spritecollide(self, enemies, False, collided=pygame.sprite.collide_mask)
        for bird in collided_birds:
            # check each bird to see if above or below
            if bird.y > self.y and bird.alive:
                self.bounce(bird)
                bird.killed()
                self.score += self.game.rewards['positive']
                bird.bounce(self)
            elif bird.y < self.y - 5 and bird.alive:
                self.bounce(bird)
                bird.bounce(self)
                self.die()

                break
            elif bird.alive:
                self.bounce(bird)
                bird.bounce(self)
        # check for platform collision
        collided_platforms = pygame.sprite.spritecollide(self, platforms, False, collided=pygame.sprite.collide_mask)
        self.walking = False
        if (((40 < self.y < 45) or (250 < self.y < 255)) and (
                self.x < 0 or self.x > 860)):  # catch when it is walking between screens
            self.walking = True
            self.y_speed = 0
        else:
            collided = False
            for collided_platform in collided_platforms:
                collided = self.bounce(collided_platform)
            if collided:
                # play a bump sound
                self.player_channel.play(self.bumpsound)
        # check for egg collission
        collided_eggs = pygame.sprite.spritecollide(self, egg_list, False, collided=pygame.sprite.collide_mask)
        if len(collided_eggs) > 0:
            for collided_egg in collided_eggs:
                collided_egg.kill()
                self.score += self.game.rewards['positive']

    # TODO modularize
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        platforms = self.game.get_platforms()
        enemies = self.game.get_enemies()
        egg_list = self.game.get_eggs()

        if self.alive == 2:
            if self.spawning:
                self.frame_num += 1
                self.image = self.spawnimages[self.frame_num]
                self.rect.topleft = (self.x, self.y)
                if self.frame_num == 5:
                    self.frame_num = 4
                    self.spawning = False
            else:
                self.score += self.game.rewards['tick']
                if self.actions['left']:
                    if self.x_speed > -self.game.config['max_speed']:
                        self.x_speed -= 0.5
                elif self.actions['right']:
                    if self.x_speed < self.game.config['max_speed']:
                        self.x_speed += 0.5
                if self.actions['up']:
                    #if not self.flap:
                    self.player_channel.stop()
                    self.flapsound.play(0)
                    if self.y_speed > -250:
                        self.y_speed -= 2
                    self.flap = True
                else:
                    self.flap = False
                self.x = self.x + self.x_speed
                self.y = self.y + self.y_speed
                if not self.walking:
                    self.y_speed += 0.4
                if self.y_speed > self.game.config['max_speed']:
                    self.y_speed = self.game.config['max_speed']
                if self.y_speed < -self.game.config['max_speed']:
                    self.y_speed = -self.game.config['max_speed']
                if self.x_speed > self.game.config['max_speed']:
                    self.x_speed = self.game.config['max_speed']
                if self.x_speed < -self.game.config['max_speed']:
                    self.x_speed = -self.game.config['max_speed']
                if self.y < 0:
                    self.y = 0
                    self.y_speed = 2
                # when falling into lava
                if self.y > 570:
                    self.die()
                if self.x < -48:
                    self.x = 900
                if self.x > 900:
                    self.x = -48
                self.rect.topleft = (self.x, self.y)
                self.check_collisions(enemies, platforms, egg_list)
                self.rect.topleft = (self.x, self.y)
                if self.walking:
                    # if walking
                    if self.next_anim_time < current_time:
                        if self.x_speed != 0:
                            if (self.x_speed > 5 and self.actions['left']) or (
                                    self.x_speed < -5 and self.actions['right']):

                                if self.frame_num != 4:
                                    self.player_channel.play(self.skidsound)
                                self.frame_num = 4
                            else:
                                self.next_anim_time = current_time + 200 / abs(self.x_speed)
                                self.frame_num += 1
                                if self.frame_num > 3:
                                    self.frame_num = 0
                        elif self.frame_num == 4:
                            self.frame_num = 3
                            self.player_channel.stop()

                    self.image = self.images[self.frame_num]
                else:
                    if self.flap:
                        self.image = self.images[6]

                    else:
                        self.image = self.images[5]
                if self.x_speed < 0 or (self.x_speed == 0 and self.facing_right == False):
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing_right = False
                else:
                    self.facing_right = True
        elif self.alive == 1:
            # unmounted player, lone bird
            # see if we need to accelerate
            if abs(self.x_speed) < self.targetx_speed:
                if abs(self.x_speed) > 0:
                    self.x_speed += self.x_speed / abs(self.x_speed) / 2
                else:
                    self.x_speed += 0.5
            # work out if flapping...
            if self.flap < 1:
                if random.randint(0, 10) > 8 or self.y > 450:  # flap to avoid lava
                    self.y_speed -= 3
                    self.flap = 3
            else:
                self.flap -= 1

            self.x = self.x + self.x_speed
            self.y = self.y + self.y_speed
            if not self.walking:
                self.y_speed += 0.4
            if self.y_speed > 10:
                self.y_speed = 10
            if self.y_speed < -10:
                self.y_speed = -10
            if self.y < 0:  # can't go off the top
                self.y = 0
                self.y_speed = 2

            if self.x < -48:  # off the left. remove entirely
                self.image = self.images[7]
                self.alive = 0
            if self.x > 900:  # off the right. remove entirely
                self.image = self.images[7]
                self.alive = 0
            self.rect.topleft = (self.x, self.y)
            # check for platform collision
            collided_platforms = pygame.sprite.spritecollide(self, platforms, False,
                                                             collided=pygame.sprite.collide_mask)
            self.walking = False
            if (((self.y > 40 and self.y < 45) or (self.y > 220 and self.y < 225)) and (
                    self.x < 0 or self.x > 860)):  # catch when it is walking between screens
                self.walking = True
                self.y_speed = 0
            else:
                for collided_platform in collided_platforms:
                    self.bounce(collided_platform)
            self.rect.topleft = (self.x, self.y)
            if self.walking:
                if self.next_anim_time < current_time:
                    if self.x_speed != 0:
                        self.next_anim_time = current_time + 100 / abs(self.x_speed)
                        self.frame_num += 1
                        if self.frame_num > 3:
                            self.frame_num = 0
                        else:
                            self.frame_num = 3
            else:
                if self.flap > 0:
                    self.frame_num = 6
                else:
                    self.frame_num = 5
            self.image = self.unmounted_images[self.frame_num]
            if self.x_speed < 0 or (self.x_speed == 0 and self.facing_right == False):
                self.image = pygame.transform.flip(self.image, True, False)
                self.facing_right = False
            else:
                self.facing_right = True
        else:
            # player respawn
            if self.lives > 0:
                self.respawn()
        self.reset_actions()

    def bounce(self, collided_thing):
        collided = False
        if self.y < (collided_thing.y - 20) and (
                ((collided_thing.x - 40) < self.x < (collided_thing.rect.right - 10))):
            # coming in from the top?
            self.walking = True
            self.y_speed = 0
            self.y = collided_thing.y - self.rect.height + 1
        elif self.x < collided_thing.x:
            # colliding from left side
            collided = True
            self.x = self.x - 10
            self.x_speed = -2
        elif self.x > collided_thing.rect.right - 50:
            # colliding from right side
            collided = True
            self.x = self.x + 10
            self.x_speed = 2
        elif self.y > collided_thing.y:
            # colliding from bottom
            collided = True
            self.y = self.y + 10
            self.y_speed = 0
        return collided

    def die(self):
        self.score += self.game.rewards['loss']
        self.lives -= 1
        self.alive = 1

    def respawn(self):
        self.frame_num = 1
        self.image = self.images[self.frame_num]
        self.rect = self.image.get_rect()
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.facing_right = True
        self.x_speed = 0
        self.y_speed = 0
        self.flap = False
        self.walking = True
        self.spawning = True
        self.alive = 2