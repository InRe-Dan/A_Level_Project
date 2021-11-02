"""Import used by index.py to store all entity objects."""
import random
import pygame as pg
import math
import utils
pg.init()

# General Behaviour of entities:
# Update methods should always return a list of entities that should continue to be processed for the next frame
# Pathfinding methods will simply set the next_move attribute according to data given - movement methods still have to be called as needed.
# Directions are represented using Numpad Notation to avoid string processing: North East South West = 8 6 2 4

def astarlistcheck(current, array):
    checkx, checky = current[0], current[1]
    returnvalue = None
    for element in array:
        if element[0] == checkx and element[1] == checky:
            returnvalue = element[2]
            break
    return returnvalue

def astarremove(element, array):
    for i in range(len(list)):
        if (array[0], array[1], array[2]) == element:
            array.pop(i)
            return array
    return array

class Sprites():
    """Simple class for storing and resizing sprites."""
    def __init__(self):
        self.sprites = { # simple sprites
            "blank": pg.image.load("sprites/blank.png"),
            "teleporter": pg.image.load("sprites/Teleporter.png"),
            "soldier": pg.image.load("sprites/Soldier.png"),
            "bomb": pg.image.load("sprites/inventory/bomb.png"),
            "grunt": pg.image.load("sprites/Grunt.png")
        }
        for key in list(self.sprites.keys()): # flipped horizontally
	        self.sprites[key + "flip"] = pg.transform.flip(self.sprites[key], True, False)
        self.bombexplosions = utils.make_dict("./sprites/bombexplosion/")

        self.swordslashes = utils.make_dict("./sprites/sword/")
        for key in list(self.swordslashes): # Longsword Projectile sprites
            for direction in [("4", 180), ("8", 90), ("2", 270)]:
                newkey = key.replace("6", direction[0])
                self.swordslashes[newkey] = pg.transform.rotate(self.swordslashes[key], direction[1])

        # Fireball projectile sprites
        self.fireballsprites = utils.make_dict("./sprites/fireball/")
        self.fireballsprites["d4"] = pg.transform.rotate(self.fireballsprites["d6"], 180)
        self.fireballsprites["d8"] = pg.transform.rotate(self.fireballsprites["d6"], 90)
        self.fireballsprites["d2"] = pg.transform.rotate(self.fireballsprites["d6"], 270)
        # Potion particle effect sprites
        self.healparticles = utils.make_dict("./sprites/heal/")
        # Red transparent sprite for laying over enemies that have been damaged
        self.redtint = pg.Surface((1, 1)).convert_alpha()
        self.redtint.fill((255, 0, 0, 200))

    def resize(self, ppb):
        """Sets all sprite sizes to the dimensions ppb*ppb"""
        for key in self.sprites:
            self.sprites[key] = pg.transform.scale(self.sprites[key], (ppb, ppb))
        for key in self.fireballsprites:
            self.fireballsprites[key] = pg.transform.scale(self.fireballsprites[key], (ppb, ppb))
        for key in self.swordslashes:
            self.swordslashes[key] = pg.transform.scale(self.swordslashes[key], (ppb, ppb))
        for key in self.bombexplosions:
            self.bombexplosions[key] = pg.transform.scale(self.bombexplosions[key], (ppb, ppb))
        self.redtint = pg.transform.scale(self.redtint, (ppb, ppb))

# global for easy access to all entities
sprites = Sprites()

class Entity():
    """Base class for most entities, and should
    only be used for the purposes of inheritance.
    """
    def __init__(self, position):
        self.x = position[0]
        self.y = position[1]
        self.luminescent = False
        # emits light
        self.interactable = False
        # player pointer changes form
        self.walkable = False
        # can be stepped on by player & other entities
        self.friendly = False
        # (projectiles only) does not hurt the player
        self.projectile = False
        # projectile marker
        self.enemy = False
        # enemy marker
        self.pickup = False
        # item entity that can be picked up (unimplemented)
        self.direction = 6
        # see numpad documentation
        self.sprite = None
        # overridden by specific entities
        self.next_move = (self.x, self.y)
        self.health = -1
        # default value
        self.list_priority = False
        # for ordering collision and render lists
        self.collided = False
        # marker for projectiles
    
    def frame_update(self):
        """Overridden by entities, used for animation."""
        return [self]

    def update(self, layout, player, assets, entlist):
        """Overridden by entities."""
        return [self]
    
    def process_projectile_collisions(self, layout, entlist):
        """Checks if a projectile has hit the entity."""
        for entity in entlist:
            if (entity.x, entity.y) == (self.x, self.y) and entity.projectile:
                self.health -= entity.damage
                entity.collided = True


    def call_pathfind(self, level, target, entities):
        """Overridden by entities, if they use pathfinding."""
        ...
    
    def move(self):
        """Moves an entity to their next tile, or turns them towards it.
        Does NOT check for collision - this should be done in e.update(),
        after which this method should be called.
        If the next movement is more than one tile away, the entity is teleported
        without any regard for the direction in which it's facing.
        """
        if self.next_move == (self.x, self.y):
            return
        dx = self.next_move[0] - self.x
        dy = self.next_move[1] - self.y
        if abs(dx) > 1 or abs(dy) > 1:
            self.x = self.next_move[0]
            self.y = self.next_move[1]
            return
        if dx == 1:
            if self.direction == 6:
                self.x += 1
                return
            self.direction = 6
            return
        if dy == 1:
            if self.direction == 2:
                self.y += 1
                return
            self.direction = 2
            return
        if dx == -1:
            if self.direction == 4:
                self.x -= 1
                return
            self.direction = 4
            return
        if dy == -1:
            if self.direction == 8:
                self.y -= 1
                return
            self.direction = 8
            return
        raise ValueError

    def ent_contact(self, ent):
        """Returns true if an object is within one block away from the entity.
        Does not return true if the player is positioned diagonally one tile away.
        """
        if ent.x == self.x and ent.y == self.y:
            return True
        if ent.x == self.x and (ent.y == self.y + 1 or ent.y == self.y - 1):
            return True
        if ent.y == self.y and (ent.x == self.x + 1 or ent.x == self.x - 1):
            return True
        return False

    def has_los(self, layout, target):
        """Samples some points between the target and entitiy and checks if any 
        of the tiles in the way are not transparent. As a result, it's not 100% reliable.
        Additionally very slow, due to the sampling, but it was previously used for 
        the simple pathfinding.
        """
        dx = self.x - target.x
        dy = self.y - target.y
        if dx == 0:
            for i in range(abs(dy)):
                if not layout[target.y + i][target.x].transparent:
                    return False
            return True
        accuracy = 400
        dy = self.y - target.y
        m = dy/dx
        c = self.y - m * self.x
        for i in range(0, abs(dx * accuracy)):
            if dx > 0:
                currentx = target.x + i/accuracy
            else:
                currentx = target.x - i/accuracy
            currenty = currentx * m + c
            if not layout[round(currenty)][round(currentx)].transparent:
                return False
        return True

    def simple_pathfind(self, level, target, entities):
        """Sets next_move to one tile closer to a given target if there is no obstruction."""
        distancex = self.x - target[0] # positive = left
        distancey = self.y - target[1] # positive = up
        if distancex == 0 and distancey == 0:
            return

        # Very simple placeholder pathfinding - just tries to get one tile closer   

        if abs(distancex) >= abs(distancey):
            if distancex > 0 and level.rows[self.y][self.x - 1].weight > 0:
                self.next_move = (self.x - 1, self.y)
                return
            elif distancex < 0 and level.rows[self.y][self.x + 1].weight > 0:
                self.next_move = (self.x + 1, self.y)
                return
            else:
                if distancey > 0 and level.rows[self.y - 1][self.x].weight > 0:
                    self.next_move = (self.x, self.y - 1)
                    return
                elif distancey < 0 and level.rows[self.y + 1][self.x].weight > 0:
                    self.next_move = (self.x, self.y + 1)
                    return
        else:
            if distancey > 0 and level.rows[self.y - 1][self.x].weight > 0:
                self.next_move = (self.x, self.y - 1)
                return
            elif distancey < 0 and level.rows[self.y + 1][self.x].weight > 0:
                self.next_move = (self.x, self.y + 1) 
                return
            else:
                if distancex > 0 and level.rows[self.y][self.x - 1].weight > 0:
                    self.next_move = (self.x - 1, self.y)
                    return
                elif distancex < 0 and level.rows[self.y][self.x + 1].weight > 0:
                    self.next_move = (self.x + 1, self.y)
                    return
    
    def get_direction_facing(self, position):
        """Find which direction the projectile should travel in when shot by
        the player (or any entity.)
        """
        if self.x > position[0]:
            return 6
        if self.x < position[0]:
            return 4
        if self.y > position[1]:
            return 2
        if self.y < position[1]:
            return 8
        raise ValueError

    def directional_pathfind(self, level):
        """Sets next_move depending on what direction the entity is facing.
        Used for simple projectiles. Will be set to None if tile is out of bounds.
        """
        if self.direction == 6:
            next_move = (self.x + 1, self.y)
        elif self.direction == 4:
            next_move = (self.x - 1, self.y)
        elif self.direction == 8:
            next_move = (self.x, self.y - 1)
        else:
            next_move = (self.x, self.y + 1)
        try:
            level.rows[next_move[1]][next_move[0]]
            self.next_move = next_move
        except IndexError:
            self.next_move = None
        
    
    def seek_pathfind(self, level, target, entities):
        """A* Pathfinding implementation."""
        grid = level.solidmap.copy()
        for entity in entities:
            if not entity.walkable and entity != self:
                grid[entity.y][entity.x] = 0


        openlist = [(self.x, self.y, 0, (self.x, self.y))]
        closedlist = []

        found = False
        while len(openlist) > 0 and not found:

            lowestindex = 0
            for i in range(len(openlist)):
                if openlist[i][2] < openlist[lowestindex][2]:
                    lowestindex = i
            current = openlist.pop(lowestindex)
            closedlist.append(current)

            if (current[0], current[1]) == target:
                found = True

            else:
                if current[0] - 1 >= 0 and current[1] in range(len(grid)):
                    if astarlistcheck((current[0] - 1, current[1]), closedlist) == None:
                        weight = grid[current[1]][current[0] - 1]
                        if weight > 0:
                            h = abs(current[0] - 1 - target[0]) + abs(current[1] - target[1])
                            g = current[2] + weight
                            s = h + g
                            check = astarlistcheck((current[0] - 1, current[1]), openlist)
                            if check == None:
                                openlist.append((current[0] - 1, current[1], s, (current[0], current[1])))
                            elif check > s:
                                openlist = astarremove((current[0] - 1, current[1], check), openlist)
                                openlist.append((current[0] - 1, current[1], s, (current[0], current[1])))

                if current[0] + 1 < len(grid[0]) and current[1] in range(len(grid)):
                    if astarlistcheck((current[0] + 1, current[1]), closedlist) == None:
                        weight = grid[current[1]][current[0] + 1]
                        if weight > 0:
                            h = abs(current[0] + 1 - target[0]) + abs(current[1] - target[1])
                            g = current[2] + weight
                            s = h + g
                            check = astarlistcheck((current[0] + 1, current[1]), openlist)
                            if check == None:
                                openlist.append((current[0] + 1, current[1], s, (current[0], current[1])))
                            elif check > s:
                                openlist = astarremove((current[0] + 1, current[1], check), openlist)
                                openlist.append((current[0] + 1, current[1], s, (current[0], current[1])))

                if current[1] - 1 >= 0 and current[0] in range(len(grid[0])):
                    if astarlistcheck((current[0], current[1] - 1), closedlist) == None:
                        weight = grid[current[1] - 1][current[0]]
                        if weight > 0:
                            h = abs(current[0] - target[0]) + abs(current[1] - 1 - target[1])
                            g = current[2] + weight
                            s = h + g
                            check = astarlistcheck((current[0], current[1] - 1), openlist)
                            if check == None:
                                openlist.append((current[0], current[1] - 1, s, (current[0], current[1])))
                            elif check > s:
                                openlist = astarremove((current[0], current[1] - 1, check), openlist)
                                openlist.append((current[0], current[1] - 1, s, (current[0], current[1])))

                if current[1] + 1 < len(grid) and current[0] in range(len(grid[0])):
                    if astarlistcheck((current[0], current[1] + 1), closedlist) == None:
                        weight = grid[current[1] + 1][current[0]]
                        if weight > 0:
                            h = abs(current[0] - target[0]) + abs(current[1] + 1 - target[1])
                            g = current[2] + weight
                            s = g + h
                            check = astarlistcheck((current[0], current[1] + 1), openlist)
                            if check == None:
                                openlist.append((current[0], current[1] + 1, s, (current[0], current[1])))
                            elif check > s:
                                openlist = astarremove((current[0] + 1, current[1] + 1, check), openlist)
                                openlist.append((current[0] + 1, current[1] + 1, s, (current[0], current[1])))

        if found:
            supposed_path = []
            traversing_back = closedlist.pop(-1)
            supposed_path.append(traversing_back)
            while True:
                if traversing_back[3] == (self.x, self.y):
                    self.next_move = (traversing_back[0], traversing_back[1])
                    break
                else:
                    while True:
                        newnode = closedlist.pop(-1)
                        if traversing_back[3] == (newnode[0], newnode[1]):
                            traversing_back = newnode
                            supposed_path.append(traversing_back)
                            break

    def call_pathfind(self, level, target, entities):
        pass

    def get_sprite(self):
        """Default, normally overridden by animated entities."""
        return sprites.sprites[self.sprite]

    def get_tile_in_front(self, layout):
        """Returns the object for the tile that the player is facing.
        If the coordinates are out of bounds, returns None."""
        try:
            if self.direction == 6 :
                return layout[self.y][self.x + 1]
            elif self.direction == 4:
                return layout[self.y][self.x - 1]
            elif self.direction == 8:
                return layout[self.y - 1][self.x + 1]
            elif self.direction == 2:
                return layout[self.y + 1][self.x + 1]
        except IndexError:
            return None




# Enemies

class Soldier(Entity):
    """Simplest AI and lowest stats.
    Moves one tile closer to the player every other turn provided that
    there is a clear line of sight.
    Should remember where the player was when it loses line of sight.
    Otherwise, wanders aimlessly around its last active location."""
    def __init__(self, position, health=50, damage=20):
        super().__init__(position)
        self.luminescent = True
        self.light = 50
        self.health = health
        self.damage = damage
        self.sprite = sprites.sprites["soldier"].copy()
        self.damagedsprite = self.sprite.copy()
        self.damagedsprite.blit(sprites.redtint, (0,0), special_flags = pg.BLEND_RGBA_MULT)
        # turn red briefly when damaged
        self.enemy = True
        self.actiontick = 0
        self.damagetick = 0
        self.walkable = False

    def call_pathfind(self, level, target, entities):
        self.seek_pathfind(level, target, entities)

    def frame_update(self):
        # keep track of how long ago since it's been hit
        if self.damagetick > 0:
            self.damagetick -= 1
        return [self]

    def update(self, layout, player, assets, entlist):

        if self.actiontick == 1:
            self.actiontick = 0
            if self.ent_contact(player):
                player.damage(self.damage)
            self.move()
        else:
            self.actiontick = 1

        if player.attacked and player.facing_tile == [self.x, self.y]:
            self.health -= player.dmg
            self.damagetick = 10
        self.process_projectile_collisions(layout, entlist)
        if self.health <= 0:
            return []

        return [self]
    
    def get_sprite(self):
        if self.damagetick == 0:
            return self.sprite
        else:
            return self.damagedsprite

class Grunt(Entity):
    """Simplest AI and lowest stats.
    Moves one tile closer to the player every other turn provided that
    there is a clear line of sight.
    Should remember where the player was when it loses line of sight.
    Otherwise, wanders aimlessly around its last active location."""
    def __init__(self, position, health=50, damage=20):
        super().__init__(position)
        self.luminescent = True
        self.light = 50
        self.health = health
        self.damage = damage
        self.sprite = sprites.sprites["grunt"].copy()
        self.damagedsprite = self.sprite.copy()
        self.damagedsprite.blit(sprites.redtint, (0,0), special_flags = pg.BLEND_RGBA_MULT)
        self.enemy = True
        self.actiontick = 0
        self.damagetick = 0
        self.walkable = False

    def call_pathfind(self, level, target, entities):
        self.directional_pathfind(level)

    def frame_update(self):
        # keep track of how long ago since it's been hit
        if self.damagetick > 0:
            self.damagetick -= 1
        return [self]

    def update(self, layout, player, assets, entlist):
        if self.actiontick == 1:
            self.actiontick = 0
    
            if self.next_move is not None and layout[self.next_move[1]][self.next_move[0]].weight > 0:
                    self.move()
            else:
                self.direction = random.choice([2, 4, 8, 6])

            if self.ent_contact(player):
                player.damage(self.damage)
            
        else:
            self.actiontick = 1

        if player.attacked and player.facing_tile == [self.x, self.y]:
            self.health -= player.dmg
            self.damagetick = 10
        self.process_projectile_collisions(layout, entlist)
        if self.health <= 0:
            return []

        return [self]
    
    def get_sprite(self):
        if self.damagetick == 0:
            return self.sprite
        else:
            return self.damagedsprite
# Projectiles

class Sword(Entity):
    def __init__(self, id, position, direction):
        """Creates two projectiles in front of the user."""
        super().__init__(position)
        self.id = id
        self.projectile = True
        self.damage = 50
        self.friendly = True
        self.walkable = True
        self.frame = 0
        self.tick = 0
        if self.id == 0:
            self.ticklimit = 7
        else:
            self.ticklimit = 5
        self.direction = str(direction)
    def frame_update(self):
        self.frame = self.tick // 2
        self.tick += 1
        if self.tick > self.ticklimit:
            return []
        return [self]
    def get_sprite(self):
        return sprites.swordslashes[self.direction + self.id + str(self.frame)]


class Bomb(Entity):
    def __init__(self, position, friendly=True):
        """After two moves, explode and leave behind nine explosion objects."""
        super().__init__(position)
        self.health = -1
        self.damage = 0
        self.explosive_damage = 100
        self.luminescent = True
        self.light = 255
        self.friendly = friendly
        self.projectile = True
        self.walkable = True
        self.fuse = 3
        self.sprite = "bomb"
        self.flicker_timer = 0
    
    def frame_update(self):
        self.flicker_timer += 1
        if self.flicker_timer > 30:
            self.flicker_timer = 0
            if self.light == 255:
                self.light = 200
            else:
                self.light = 255
        return [self]

    def update(self, layout, player, assets, entities):
        self.fuse -= 1
        if self.fuse == 0:
            explosion = self.explode(layout, player, entities)
            return explosion
        return [self]
    
    def explode(self, layout, player, entities):
        explosions = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for entity in entities:
                    if entity.x == self.x + j and entity.y == self.y + i:
                        entity.health -= self.explosive_damage
                explosions.append(Explosion((self.x + j, self.y + i)))
        return explosions

class Explosion(Entity):
    def __init__(self, position):
        """COSMETIC ONLY - Damage was already dealt in the initial explosion."""
        super().__init__(position)
        self.health = -1
        self.luminescent = True
        self.light = 400
        self.sprite = sprites.bombexplosions["1"]
        self.damage = 0
        self.friendly = True
        self.projectile = True
        self.walkable = True
        self.tick = 0

    def frame_update(self):
        self.tick += 1
        if self.tick == 24:
            return []
        else:
            self.sprite = sprites.bombexplosions[str(self.tick // 3)]
            self.light -= 10
        return [self]

    def get_sprite(self):
        return self.sprite



class Fireball(Entity):
    """Simple projectile that explodes and damages enemies upon collision. Can fly over water."""
    def __init__(self, position, playerpos, friendly=True, damage=50):
        super().__init__(position)
        self.damage = damage
        self.luminescent = True
        self.light = 255
        self.friendly = friendly
        self.projectile = True
        self.walkable = True
        self.direction = self.get_direction_facing(playerpos)
        self.frame = 0
        self.just_spawned = True

    def frame_update(self):
        if self.collided:
            self.frame += 1
            self.light -= 10
            if self.frame > 28:
                return []
        return [self]
            
                

    def update(self, layout, player, assets, entlist):
        if self.just_spawned:
            self.just_spawned = False
            self.next_move = (self.x, self.y)
        if self.collided == True:
            return [self]
        try:
            if self.next_move[0] < 0 or self.next_move[1] < 0:
                raise IndexError
            if layout[self.next_move[1]][self.next_move[0]].solid == True:
                self.collided = True
                self.light = 300
                return [self]
        except IndexError:
            self.collided == True
            self.light = 255
        self.move()
        return [self]
    
    def call_pathfind(self, level, target, entities):
        self.directional_pathfind(level)
    
    def get_sprite(self):
        if self.collided:
            return sprites.fireballsprites[str(self.frame // 4)]
        return sprites.fireballsprites["d" + str(self.direction)]

class HealParticle(Entity):
    """Cosmetic particle effect. Used for potions."""
    def __init__(self, position):
        super().__init__(position)
        self.walkable = True
        self.tick = 0
    def frame_update(self):
        self.tick += 1
        if self.tick < 24:
            return [self]
        return []
    def get_sprite(self):
        return sprites.healparticles[str(self.tick // 3)]

# Gameplay entities

class Teleporter(Entity):
    """This is an entity that when interacted with by the player, will cause them
     to transport to another level, while keeping their character intact.

    Pass a tuple for position, as well as a destination variable with the name of
    the next level. By default, the teleporter places the game in a "win" state.
    """
    def __init__(self, position, destination="LEVELCLEAR"):
        super().__init__(position)
        self.interactable = True
        self.luminescent = True
        self.light = 50
        self.brighter = True
        self.destination = destination
        self.interacted = False
        self.sprite = "teleporter"
        self.walkable = True
    
    def frame_update(self):
        if random.randint(1, 20) == 1:
            self.brighter = not self.brighter
        if self.brighter:
            self.light += 1
            if self.light < 20:
                self.light = 20
                self.brighter = True
        else:
            self.light -= 1
            if self.light > 60:
                self.light = 60
                self.brighter = False
        return [self]

