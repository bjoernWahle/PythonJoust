import pygame

from sprites import load_sprite


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

    @staticmethod
    def load_platforms():
        platform_images = [load_sprite("plat1.png"), load_sprite("plat2.png"),
                           load_sprite("plat3.png"),
                           load_sprite("plat4.png"), load_sprite("plat5.png"),
                           load_sprite("plat6.png"),
                           load_sprite("plat7.png"), load_sprite("plat8.png")]
        return platform_images

    @staticmethod
    def get_platforms():
        platform_images = Platform.load_platforms()
        plat1 = Platform(platform_images[0], 200, 550)
        plat2 = Platform(platform_images[1], 350, 395)
        plat3 = Platform(platform_images[2], 350, 130)
        plat4 = Platform(platform_images[3], 0, 100)
        plat5 = Platform(platform_images[4], 759, 100)
        plat6 = Platform(platform_images[5], 0, 310)
        plat7 = Platform(platform_images[6], 759, 310)
        plat8 = Platform(platform_images[7], 600, 290)
        #return [plat1, plat2, plat3, plat4, plat5, plat6, plat7, plat8]
        return [plat2]