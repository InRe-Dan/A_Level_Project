import os
import pygame
pygame.display.set_mode((600, 600))
def make_dict(directory):
    """Creates a dictionary of pygame image object of ALL files in a
    directory. To use current script directory, use ./{dir}/{dir}/
    """
    spritenames = os.listdir(directory)
    dictionary = {}
    for spritename in spritenames:
        try:
            dictionary[spritename[:-4]] = pygame.image.load(directory + spritename).convert_alpha()
        except:
            pass
    return dictionary
