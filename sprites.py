import pygame


def load_sliced_sprites(w, h, filename):
    # returns a list of image frames sliced from file
    images = []
    master_image = pygame.image.load('sprites/%s' % filename)
    master_image = master_image.convert_alpha()
    master_width, master_height = master_image.get_size()
    for i in range(int(master_width / w)):
        images.append(master_image.subsurface((i * w, 0, w, h)))
    return images


def load_sprite(filename, convert_alpha=True):
    sprite = pygame.image.load("sprites/%s" % filename)
    if convert_alpha:
        sprite = sprite.convert_alpha()
    else:
        sprite = sprite.convert()
    return sprite


def load_platforms():
    platform_images = [pygame.image.load("sprites/plat1.png"), pygame.image.load("sprites/plat2.png"),
                       pygame.image.load("sprites/plat3.png"),
                       pygame.image.load("sprites/plat4.png"), pygame.image.load("sprites/plat5.png"),
                       pygame.image.load("sprites/plat6.png"),
                       pygame.image.load("sprites/plat7.png"), pygame.image.load("sprites/plat8.png")]
    return platform_images
