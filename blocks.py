"""Import used by index.py to store all block objects."""
import pygame as pg
import utils
import random
pg.init()

SPRITES = { # misc sprites
    "Void": pg.image.load("./sprites/void.png")
}
# full tile sprites
grassdict = utils.make_dict("./sprites/Grass/")
grass_extras_dict = utils.make_dict("./sprites/misc/grassdeco/")
walldict = utils.make_dict("./sprites/Wall/")
cavedict = utils.make_dict("./sprites/CaveFloor/")
waterdict = utils.make_dict("./sprites/water/")
for key in waterdict.keys():
    tempsurface = grassdict[key].copy()
    tempsurface.blit(waterdict[key], (0, 0))
    waterdict[key] = tempsurface

class Block():
    """Any tile that inherits from this class will have a choose_sprite method"""
    def choose_sprite(self, position, layout, size):
        """
        0  |  1  |  2  - An 8 binary digit string is stored to denote whether or not a particular 
        3  | pos |  4  - index is occupied by a tile of the same type as the centre tile
        5  |  6  |  7  - 1 is a different tile and 0 is a tile of the same type/style.
        """
        info = [1,1,1,1,1,1,1,1]
        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                blocky = position[1] + y
                blockx = position[0] + x
                if len(layout[0]) >blockx > -1 and len(layout) > blocky > -1:
                    target = layout[blocky][blockx]
                    if target.group == self.group:
                        if y == -1 and x == -1:
                            info[0] = 0
                        elif y == -1 and x == 0:
                            info[1] = 0
                        elif y == -1 and x == 1:
                            info[2] = 0
                        elif y == 0 and x == -1:
                            info[3] = 0
                        elif y == 0 and x == 1:
                            info[4] = 0
                        elif y == 1 and x == -1:
                            info[5] = 0
                        elif y == 1 and x == 0:
                            info[6] = 0
                        elif y == 1 and x == 1:
                            info[7] = 0
        id = info.copy()
        if info[1] == 1:
            id[0] = 1
            id[2] = 1
        if info[4] == 1:
            id[2] = 1
            id[7] = 1
        if info[3] == 1:
            id[0] = 1
            id[5] = 1
        if info[6] == 1:
            id[5] = 1
            id[7] = 1
        self.sprite = pg.transform.scale(self.spritedict[str(id).strip("[]").replace(", ", "")], (size, size))
        self.do_additional_generation(position, layout, size)

    def do_additional_generation(self, position, layout, size):
        pass

class Void():
    """Solid texture used for filling empty space on the screen,
    and can also be used by editors as a regular, full tile."""
    def __init__(self, size, weight=0):
        self.group = "Void"
        self.weight = weight
        self.transparent = True
        self.light = 0
        self.sprite = pg.transform.scale(SPRITES["Void"], (size, size))
        self.luminous = False
        self.solid = False

class Grass(Block):
    """Normal ground block that emits 255 light."""
    def __init__(self, size):
        self.weight = 1
        self.transparent = True
        self.group = "Grass"
        self.spritedict = grassdict
        self.sprite = pg.transform.scale(grassdict["00000000"], (size, size))
        self.light = 255
        self.luminous = True
        self.solid = False

    def do_additional_generation(self, position, layout, size):
        """Generates flowers and grass patches on the tile randomly."""
        if random.randint(1, 4) == 1:
            offset1 = random.randint(-20, 20)
            offset2 = random.randint(-20, 20)
            blittable = random.choice(list(grass_extras_dict.values()))
            location = ((self.sprite.get_width() - blittable.get_width()) / 2 + offset1, (self.sprite.get_height() - blittable.get_height()) / 2 + offset2)
            self.sprite.blit(blittable, location)

class Wall(Block):
    """Used for normal solid walls and for hidden walls that entities can walk through."""
    def __init__(self, size,  weight=0, transparent=False):
        self.weight = weight
        self.transparent = transparent
        self.group = "Wall"
        self.spritedict = walldict
        self.light = 0
        self.luminous = False
        self.sprite = pg.transform.scale(walldict["00000000"], (size, size))
        self.solid = True
        

class CaveFloor(Block):
    """Walkable tile that emits no light."""
    def __init__(self, size):
        self.weight = 10000
        # enemies will avoid this tile
        self.transparent = True
        self.light = 0
        self.luminous = False
        self.spritedict = cavedict
        self.sprite = pg.transform.scale(cavedict["00000000"], (size, size))
        self.group = "Cave"
        # Group used for tile texture selection
        self.solid = False

class Water(Block):
    """Non-walkable but transparent tile, that entities can see through for pathfinding.
    Emits light, same as grass."""
    def __init__(self, size):
        self.weight = 0
        self.transparent = True
        self.light = 255
        self.luminous = True
        self.spritedict = waterdict
        self.sprite = pg.transform.scale(cavedict["00000000"], (size, size))
        self.group = "Water"
        self.solid = False