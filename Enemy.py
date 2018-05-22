import random
import pygame

from Egg import Egg
from sprites import load_sliced_sprites

SPAWN_POINTS = [[690, 248], [420, 500], [420, 80], [50, 255]]

class Enemy(pygame.sprite.Sprite):

    @staticmethod
    def generate_enemies(game, enemy_number):
        # makes x enemies at a time, at x random spawn points

        enemy_list = []
        for count in range(enemy_number):
            enemy_list.append(Enemy(game, SPAWN_POINTS[random.randint(0, 3)],0))

        return enemy_list

    def __init__(self, game, start_pos, enemy_type):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.game = game
        self.images = load_sliced_sprites(60, 58, "enemies2.png")
        self.unmounted_images = load_sliced_sprites(60, 60, "unmounted.png")
        self.spawnimages = load_sliced_sprites(60, 60, "spawn1.png")
        self.frame_num = 0
        self.enemyType = enemy_type
        self.image = self.spawnimages[0]
        self.rect = self.image.get_rect()
        self.next_update_time = 0
        self.next_anim_time = 0
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.flap = 0
        self.facing_right = True
        self.x_speed = random.randint(3, 10)
        self.target_x_speed = 10
        self.y_speed = 0
        self.walking = True
        self.flap_count = 0
        self.spawning = True
        self.alive = True

    def killed(self):
        # make an egg appear here
        self.game.addEgg(self.x, self.y, self.x_speed, self.y_speed)
        self.alive = False

    def update(self, current_time):
        platforms = self.game.get_platforms()

        if self.next_update_time < current_time:  # only update every 30 millis
            self.next_update_time = current_time + 50
            if self.spawning:
                self.frame_num += 1
                self.image = self.spawnimages[self.frame_num]
                self.next_update_time += 100
                self.rect.topleft = (self.x, self.y)
                if self.frame_num == 5:
                    self.spawning = False
            else:
                # see if we need to accelerate
                if abs(self.x_speed) < self.target_x_speed:
                    self.x_speed += self.x_speed / abs(self.x_speed) / 2
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
                if self.y_speed > self.game.config['max_speed']:
                    self.y_speed = self.game.config['max_speed']
                if self.y_speed < -self.game.config['max_speed']:
                    self.y_speed = -self.game.config['max_speed']
                if self.y < 0:  # can't go off the top
                    self.y = 0
                    self.y_speed = 2
                if self.y > 570:  # hit lava
                    self.kill()

                if self.x < -48:  # off the left. If enemy is dead then remove entirely
                    if self.alive:
                        self.x = 900
                    else:
                        self.kill()
                if self.x > 900:  # off the right. If enemy is dead then remove entirely
                    if self.alive:
                        self.x = -48
                    else:
                        self.kill()
                self.rect.topleft = (self.x, self.y)
                # check for platform collision
                collided_platforms = pygame.sprite.spritecollide(self, platforms, False,
                                                                 collided=pygame.sprite.collide_mask)
                self.walking = False
                if (((40 < self.y < 45) or (220 < self.y < 225)) and (
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
                if self.alive:
                    self.image = self.images[((self.enemyType * 7) + self.frame_num)]
                else:
                    # show the unmounted sprite
                    self.image = self.unmounted_images[self.frame_num]
                if self.x_speed < 0 or (self.x_speed == 0 and self.facing_right == False):
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing_right = False
                else:
                    self.facing_right = True

    def bounce(self, collided_thing):
        collided = False
        if self.y < (collided_thing.y - 20) and (
                ((collided_thing.x - 40) < self.x < (collided_thing.rect.right - 10))):
            # coming in from the top?
            self.walking = True
            self.y_speed = 0
            self.y = collided_thing.y - self.rect.height + 3
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