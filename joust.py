# Joust by S Paget

import pygame
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ENEMY_KILL_SCORE = 10
EGG_SCORE = 10
ENEMY_COUNT = 6
MAX_SPEED = 10

def load_sliced_sprites(w, h, filename):
    # returns a list of image frames sliced from file
    images = []
    master_image = pygame.image.load('sprites/%s' % filename)
    master_image = master_image.convert_alpha()
    master_width, master_height = master_image.get_size()
    for i in range(int(master_width / w)):
        images.append(master_image.subsurface((i * w, 0, w, h)))
    return images


def load_platforms():
    platform_images = [pygame.image.load("sprites/plat1.png"), pygame.image.load("sprites/plat2.png"), pygame.image.load("sprites/plat3.png"),
                       pygame.image.load("sprites/plat4.png"), pygame.image.load("sprites/plat5.png"), pygame.image.load("sprites/plat6.png"),
                       pygame.image.load("sprites/plat7.png"), pygame.image.load("sprites/plat8.png")]
    return platform_images


def get_keyset(id):
    if id == 1:
        return {'left': pygame.K_a, 'right': pygame.K_d, 'space': pygame.K_w}
    else:
        return {'left': pygame.K_j, 'right': pygame.K_l, 'space': pygame.K_i}


class Egg(pygame.sprite.Sprite):
    def __init__(self, eggimages, x, y, x_speed, y_speed):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.images = eggimages
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.rect.topleft = (x, y)
        self.right = self.rect.right
        self.top = self.rect.top
        self.next_update_time = 0

    def move(self):
        # gravity
        self.y_speed += 0.4
        if self.y_speed > 10:
            self.y_speed = 10
        self.y += self.y_speed
        self.x += self.x_speed
        if self.y > 570:  # hit lava
            self.kill()

    def update(self, current_time, platforms):
        # Update every 30 milliseconds
        if self.next_update_time < current_time:
            self.next_update_time = current_time + 30
            self.move()
            self.rect.topleft = (self.x, self.y)
            collided_platforms = pygame.sprite.spritecollide(self, platforms, False,
                                                             collided=pygame.sprite.collide_mask)
            if (((40 < self.y < 45) or (250 < self.y < 255)) and (
                    self.x < 0 or self.x > 860)):  # catch when it is rolling between screens
                self.y_speed = 0
            else:
                collided = False
                for collided_platform in collided_platforms:
                    collided = self.bounce(collided_platform)
            # wrap round screens
            if self.x < -48:
                self.x = 900
            if self.x > 900:
                self.x = -48

    def bounce(self, collided_thing):
        collided = False
        if self.y < (collided_thing.y - 20) and (
                ((collided_thing.x - 40) < self.x < (collided_thing.rect.right - 10))):
            # coming in from the top?
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


class Platform(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
        self.right = self.rect.right
        self.top = self.rect.top


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemyimages, spawnimages, unmountedimages, start_pos, enemyType):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.images = enemyimages
        self.spawnimages = spawnimages
        self.unmountedimages = unmountedimages
        self.frame_num = 0
        self.enemyType = enemyType
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

    def killed(self, egg_list, egg_images):
        # make an egg appear here
        egg_list.add(Egg(egg_images, self.x, self.y, self.x_speed, self.y_speed))
        self.alive = False

    def update(self, current_time, keys, platforms, god):
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
                if self.y_speed > MAX_SPEED:
                    self.y_speed = MAX_SPEED
                if self.y_speed < -MAX_SPEED:
                    self.y_speed = -MAX_SPEED
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
                    self.image = self.unmountedimages[self.frame_num]
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


class Player(pygame.sprite.Sprite):

    def __init__(self, birdimages, spawnimages, player_unmounted_images, spawn_x, spawn_y, id):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.id = id
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.images = birdimages
        self.unmounted_images = player_unmounted_images
        self.spawnimages = spawnimages
        self.frame_num = 2
        self.image = self.images[self.frame_num]
        self.rect = self.image.get_rect()
        self.next_update_time = 0
        self.next_anim_time = 0
        self.x = spawn_x
        self.y = spawn_y
        self.facing_right = True
        self.x_speed = 0
        self.y_speed = 0
        self.targetx_speed = 10
        self.flap = False
        self.walking = True
        self.player_channel = pygame.mixer.Channel(0)
        self.flapsound = pygame.mixer.Sound("audio/joustflaedit.wav")
        self.skidsound = pygame.mixer.Sound("audio/joustski.wav")
        self.bumpsound = pygame.mixer.Sound("audio/joustthu.wav")
        self.lives = 4
        self.spawning = True
        self.alive = 2
        self.score = 0
        self.keys = get_keyset(id)

    def check_collisions(self, enemies, platforms, egg_list, egg_images, god):
        # check for enemy collision
        collided_birds = pygame.sprite.spritecollide(self, enemies, False, collided=pygame.sprite.collide_mask)
        for bird in collided_birds:
            # check each bird to see if above or below
            if bird.y > self.y and bird.alive:
                self.bounce(bird)
                bird.killed(egg_list, egg_images)
                self.score += ENEMY_KILL_SCORE
                bird.bounce(self)
            elif bird.y < self.y - 5 and bird.alive and not god.on:
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
                self.score += EGG_SCORE

    def update(self, current_time, keys, platforms, enemies, god, egg_list, egg_images):
        # Update every 30 milliseconds
        if self.next_update_time < current_time:
            self.next_update_time = current_time + 30
            if self.alive == 2:
                if self.spawning:
                    self.frame_num += 1
                    self.image = self.spawnimages[self.frame_num]
                    self.next_update_time += 100
                    self.rect.topleft = (self.x, self.y)
                    if self.frame_num == 5:
                        self.frame_num = 4
                        self.spawning = False
                else:
                    if keys[self.keys['left']]:
                        if self.x_speed > -10:
                            self.x_speed -= 0.5
                    elif keys[self.keys['right']]:
                        if self.x_speed < 10:
                            self.x_speed += 0.5
                    if keys[self.keys['space']]:
                        if not self.flap:
                            self.player_channel.stop()
                            self.flapsound.play(0)
                            if self.y_speed > -250:
                                self.y_speed -= 3
                            self.flap = True
                    else:
                        self.flap = False
                    self.x = self.x + self.x_speed
                    self.y = self.y + self.y_speed
                    if not self.walking:
                        self.y_speed += 0.4
                    if self.y_speed > 10:
                        self.y_speed = 10
                    if self.y_speed < -10:
                        self.y_speed = -10
                    if self.y < 0:
                        self.y = 0
                        self.y_speed = 2
                    if self.y > 570:
                        self.die()
                    if self.x < -48:
                        self.x = 900
                    if self.x > 900:
                        self.x = -48
                    self.rect.topleft = (self.x, self.y)
                    self.check_collisions(enemies, platforms, egg_list, egg_images, god)
                    self.rect.topleft = (self.x, self.y)
                    if self.walking:
                        # if walking
                        if self.next_anim_time < current_time:
                            if self.x_speed != 0:
                                if (self.x_speed > 5 and keys[pygame.K_LEFT]) or (
                                        self.x_speed < -5 and keys[pygame.K_RIGHT]):

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
                    self.next_update_time = current_time + 2000
                if self.x > 900:  # off the right. remove entirely
                    self.image = self.images[7]
                    self.alive = 0
                    self.next_update_time = current_time + 2000
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
                self.respawn()

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


class godmode(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.pic = pygame.image.load("sprites/god.png")
        self.image = self.pic
        self.on = False
        self.rect = self.image.get_rect()
        self.rect.topleft = (850, 0)
        self.timer = pygame.time.get_ticks()

    def toggle(self, current_time):
        if current_time > self.timer:
            self.on = not self.on
            self.timer = current_time + 1000


class points_marker(pygame.sprite.Sprite):
    pass


def generate_enemies(enemyimages, spawnimages, unmountedimages, enemy_list, spawn_points, enemies_to_spawn):
    # makes 2 enemies at a time, at 2 random spawn points
    for count in range(2):
        enemy_list.add(Enemy(enemyimages, spawnimages, unmountedimages, spawn_points[random.randint(0, 3)],
                             0))  # last 0 is enemytype
        enemies_to_spawn -= 1

    return enemy_list, enemies_to_spawn


def draw_lava(screen):
    lavaRect = [0, 600, 900, 50]
    pygame.draw.rect(screen, (255, 0, 0), lavaRect)
    return lavaRect


def draw_lava2(screen):
    lavaRect = [0, 620, 900, 30]
    pygame.draw.rect(screen, (255, 0, 0), lavaRect)
    return lavaRect


def draw_lives(lives, screen, lifeimage, player_id):
    if player_id == 1:
        startx = 375
    else:
        startx = 612
    for num in range(lives):
        x = startx + num * 20
        screen.blit(lifeimage, [x, 570])


def draw_score(score, screen, digits, player_id):
    if player_id == 1:
        x = 353
    else:
        x = 590
    screen.blit(digits[score % 10], [x, 570])
    screen.blit(digits[(score % 100) // 10], [x - 18, 570])
    screen.blit(digits[(score % 1000) // 100], [x - 2 * 18, 570])
    screen.blit(digits[(score % 10000) // 1000], [x - 3 * 18, 570])
    screen.blit(digits[(score % 100000) // 10000], [x - 4 * 18, 570])
    screen.blit(digits[(score % 1000000) // 100000], [x - 5 * 18, 570])


def check_game_end(playerbird, enemies):
    if playerbird.lives == 0:
        return True
    if len(enemies) > 0:
        for enemy in enemies:
            if enemy.alive:
                return False
        return True
    return False


def init_platforms():
    platform_images = load_platforms()
    plat1 = Platform(platform_images[0], 200,550)
    plat2 = Platform(platform_images[1], 350, 395)
    plat3 = Platform(platform_images[2], 350, 130)
    plat4 = Platform(platform_images[3], 0, 100)
    plat5 = Platform(platform_images[4], 759, 100)
    plat6 = Platform(platform_images[5], 0, 310)
    plat7 = Platform(platform_images[6], 759, 310)
    plat8 = Platform(platform_images[7], 600, 290)
    return [plat1, plat2, plat3, plat4, plat5, plat6, plat7, plat8]


def main():
    window = pygame.display.set_mode((900, 650))
    pygame.display.set_caption('Joust')
    screen = pygame.display.get_surface()
    clear_surface = screen.copy()
    player = pygame.sprite.RenderUpdates()
    enemy_list = pygame.sprite.RenderUpdates()
    egg_list = pygame.sprite.RenderUpdates()
    platforms = pygame.sprite.RenderUpdates()
    god_sprite = pygame.sprite.RenderUpdates()
    birdimages = load_sliced_sprites(60, 60, "playerMounted.png")
    enemyimages = load_sliced_sprites(60, 58, "enemies2.png")
    spawnimages = load_sliced_sprites(60, 60, "spawn1.png")
    unmountedimages = load_sliced_sprites(60, 60, "unmounted.png")
    player_unmounted_images = load_sliced_sprites(60, 60, "playerUnmounted.png")
    eggimages = load_sliced_sprites(40, 33, "egg.png")
    lifeimage = pygame.image.load("sprites/life.png")
    lifeimage = lifeimage.convert_alpha()
    digits = load_sliced_sprites(21, 21, "digits.png")
    player1 = Player(birdimages, spawnimages, player_unmounted_images, 300, 450, 1)
    player2 = Player(birdimages, spawnimages, player_unmounted_images, 600, 450, 2)
    player.add(player1)
    player.add(player2)
    god = godmode()
    god_sprite.add(godmode())
    spawn_points = [[690, 248], [420, 500], [420, 80], [50, 255]]
    platforms.add(init_platforms())
    pygame.display.update()
    next_spawn_time = pygame.time.get_ticks() + 2000
    enemies_to_spawn = ENEMY_COUNT
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        # make enemies
        if current_time > next_spawn_time and enemies_to_spawn > 0:
            enemy_list, enemies_to_spawn = generate_enemies(enemyimages, spawnimages, unmountedimages, enemy_list,
                                                            spawn_points, enemies_to_spawn)
            next_spawn_time = current_time + 5000
        keys = pygame.key.get_pressed()
        pygame.event.clear()
        # If they have pressed Escape, close down Pygame
        if keys[pygame.K_ESCAPE]:
            running = False
        # check for God mode toggle
        if keys[pygame.K_g]:
            god.toggle(current_time)
        player.update(current_time, keys, platforms, enemy_list, god, egg_list, eggimages)
        platforms.update()
        enemy_list.update(current_time, keys, platforms, god)
        egg_list.update(current_time, platforms)
        enemies_rects = enemy_list.draw(screen)
        if god.on:
            godrect = god_sprite.draw(screen)
        else:
            godrect = pygame.Rect(850, 0, 50, 50)
        player_rect = player.draw(screen)
        egg_rects = egg_list.draw(screen)
        lava_rect = draw_lava(screen)
        plat_rects = platforms.draw(screen)
        lavarect2 = draw_lava2(screen)
        draw_lives(player1.lives, screen, lifeimage, 1)
        draw_lives(player2.lives, screen, lifeimage, 2)
        draw_score(player1.score, screen, digits, 1)
        draw_score(player2.score, screen, digits, 2)
        pygame.display.update(player_rect)
        pygame.display.update(lava_rect)
        pygame.display.update(lavarect2)
        pygame.display.update(plat_rects)
        pygame.display.update(enemies_rects)
        pygame.display.update(egg_rects)
        pygame.display.update(godrect)
        player.clear(screen, clear_surface)
        enemy_list.clear(screen, clear_surface)
        egg_list.clear(screen, clear_surface)
        god_sprite.clear(screen, clear_surface)

        if check_game_end(player1, enemy_list):
            running = False


main()
pygame.quit()
