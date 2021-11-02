"""File to hold the main player class."""
import pygame as pg
import random
from inventory import Inventory
import utils
import time
import os

class Player():
    """Main player class. Takes the mandatory parameter of position, as a tuple (x, y)
    and is used to construct the player object from a level file.

    Alongside position, this class also takes starting_health, max_health, base_dmg and a list of items
    to place in the inventory on generation.
    """
    def __init__(self, position, starting_health=100, max_health=100, inventory_items=[], base_dmg=20):
        """Initializes a player object. This should not overwrite the current game.player object
        unless a new level series is loaded. Takes a variety of optional parameters, with the only compusory
        one being a position tuple."""
        self.x = position[0]
        self.y = position[1]
        self.health = starting_health
        self.max_health = max_health
        self.dmg = base_dmg
        self.light = 150
        self.moved = False
        self.turn = True
        self.inventory = Inventory(self)

        self.rsprites = utils.make_dict("./sprites/player/")
        # extending idle animation artificially
        self.rsprites["idle-1-7"] = self.rsprites["idle-1-3"]
        self.rsprites["idle-1-6"] = self.rsprites["idle-1-3"]
        self.rsprites["idle-1-5"] = self.rsprites["idle-1-2"]
        self.rsprites["idle-1-4"] = self.rsprites["idle-1-2"]
        self.rsprites["idle-1-3"] = self.rsprites["idle-1-1"]
        self.rsprites["idle-1-2"] = self.rsprites["idle-1-1"]
        self.rsprites["idle-1-1"] = self.rsprites["idle-1-0"]
        self.lsprites = {}
        for key in self.rsprites.keys():
            self.lsprites[key] = pg.transform.flip(self.rsprites[key], True, False)
        self.animation_tick = 0
        self.arrowsprites = utils.make_dict("./sprites/arrows/")
        self.sprite = self.lsprites["idle-1-0"]
        self.sprite_state = "idle-1-"
        self.animation_delay = 5
        self.animation_frame = 0
        self.facingleft = True

        self.facing = 4 
        # numpad direction notation
        # 7 8 9 
        # 4 5 6 -> 4 is left
        # 1 2 3 
        self.facing_tile = [self.x - 1, self.y]
        self.interacted = False
        self.attacked = False
        self.casting = False
        self.turn = True

    def heal(self, amount):
        self.health += amount
        if self.health > amount + self.max_health:
            self.health = self.max_health + amount
            
        


    def add_inventory_items(self, itemlist):
        """Adds a list of items to the inventory,
        intended for initalisation.
        """
        for item in itemlist:
            self.inventory.add(item)

    def face_left(self):
        """Used to update where the player is facing when a level is reloaded."""
        self.facing = 4
        self.facing_left = True
        self.facing_tile = [self.x -1, self.y]
        
    def left(self, level):
        """Shifts player x by - 1 if they already facing left.."""
        if self.facing == 4 and self.tile_traversible(level, (self.x - 1, self.y)):
            self.x -= 1
            self.moved = True
            self.turn = False
            self.facing_tile[0] -= 1
        else:
            self.facing = 4
            self.facing_tile = [self.x - 1, self.y]
            self.facingleft = True

    def right(self, level):
        """Shifts player x by + 1 if they already facing right."""
        if self.facing == 6 and self.tile_traversible(level, (self.x + 1, self.y)):
            self.x += 1
            self.moved = True
            self.turn = False
            self.facing_tile[0] += 1
        else:
            self.facing = 6
            self.facing_tile = [self.x + 1, self.y]
            self.facingleft = False

    def up(self, level):
        """Shifts player y by - 1 if they are already facing up."""
        if self.facing == 8 and self.tile_traversible(level, (self.x, self.y - 1)):
            self.y -= 1
            self.moved = True
            self.turn = False
            self.facing_tile[1] -= 1
        else:
            self.facing_tile = [self.x, self.y - 1]
            self.facing = 8

    def down(self, level):
        """Shifts player y by + 1 if they are already facing down."""
        if self.facing == 2 and self.tile_traversible(level, (self.x, self.y + 1)):
            self.y += 1
            self.moved = True
            self.turn = False
            self.facing_tile[1] += 1
        else:
            self.facing = 2
            self.facing_tile = [self.x, self.y + 1]

    def tile_traversible(self, level, position) -> "Boolean":
        """Checks if a particular tile has a solid block or entity on it."""
        if level.rows[position[1]][position[0]].weight == 0:
            return False
        for entity in level.entities:
            if entity.walkable == False and (entity.x, entity.y) == position:
                return False
        return True

    def update(self, game):
        """Processes player attributes on move or action."""
        self.moved = False
        if self.attacked:
            self.sprite_state = random.choice(["attack-0-", "attack-1-", "attack-2-"])
            self.animation_frame = 0
        if self.casting:
            self.sprite_state = "cast-"
            self.animation_frame = 0
        if self.health <= 0:
            pg.mixer.Sound("audio/sounds/death.wav").play()
            game.state = "lose"
        self.attacked = False
        self.moved = False
        self.turn = True
        self.interacted = False
        self.attacked = False
        self.casting = False
    
    def frame_update(self, game):
        """Processes player animation changes, to be called every frame."""
        self.animation_tick += 1
        if not self.animation_tick == self.animation_delay:
            return
        self.animation_tick = 0
        self.animation_frame += 1

        if self.sprite_state + str(self.animation_frame) not in self.rsprites.keys():
            self.animation_frame = 0
            if self.sprite_state != "idle-1-":
                self.sprite_state = "idle-1-"
        if self.facingleft:
            self.sprite = self.lsprites[self.sprite_state + str(self.animation_frame)]
        else:
            self.sprite = self.rsprites[self.sprite_state + str(self.animation_frame)]

    def resize_sprites(self, size):
        """Resize all sprites for the player, to be called after initializing them.
        MUST be called inside Game, as the routine requires pixels per block as a
        parameter.
        """
        # not particularly efficient as a result of using eval() when calling __init__
        for key in self.rsprites.keys():
            self.rsprites[key] = pg.transform.scale(self.rsprites[key], (size, size))
        for key in self.lsprites.keys():
            self.lsprites[key] = pg.transform.scale(self.lsprites[key], (size, size))
        for key in self.arrowsprites.keys():
            self.arrowsprites[key] = pg.transform.scale(self.arrowsprites[key], (size, size))
    
    def damage(self, damage, extras=None):
        self.health -= damage