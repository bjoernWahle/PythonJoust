import pygame

from sprites import load_sliced_sprites


class Egg(pygame.sprite.Sprite):
    def __init__(self, x, y, x_speed, y_speed):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.images  = load_sliced_sprites(40, 33, "egg.png")
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

    def update(self, dt, platforms):
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
