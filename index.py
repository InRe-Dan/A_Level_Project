"""Main script. Run to play game."""
import pygame as pg
import menu
import leveldata
import blocks
import entities
import shader

pg.mixer.pre_init(44100, -16, 4, 512)
pg.init()
pg.font.init()
pg.key.set_repeat(200, 100)
clock = pg.time.Clock()
INFO = """
GAME:
WASD - Movement
SPACE - Attack
Q - Shoot Fireball
ESC - Exit
R - Open inventory
Arrows - Use assigned items

INVENTORY:
R or S - Close inventory
Arrows - Assign items
A and D - Navigate items

MENU:
WS - Selection
SPACE - Confirm
"""
print(INFO)

class Globals():
    """Class to contain various constants, assets and objects needed by many classes.
    The whole class can be passed to modules so that they can use rendering constants and
    render on the main game screen.
    """
    screen = pg.display.set_mode((600, 600))
    ppb = 64
    entities.sprites.resize(ppb)
    tilesx = 21
    tilesy = 11
    resolutionx = ppb * tilesx
    resolutiony = ppb * tilesy

    textfont_40p = pg.font.Font("-font.ttf", 40)
    textfont_30p = pg.font.Font("-font.ttf", 30)
    textfont_20p = pg.font.Font("-font.ttf", 20)

    darktexture = pg.Surface((ppb, ppb))
    darktexture.fill((0, 0, 0))
    darktexturesmall = pg.transform.scale(darktexture, (21, 21))
    darktexturelong = pg.transform.scale(darktexture, (22, 21))
    darktexturetall = pg.transform.scale(darktexture, (21, 22))
    darktexturebig = pg.transform.scale(darktexture, (22, 22))
    darktexturedict = {}
    darktexturesmalldict = {}
    darktexturelongdict = {}
    darktexturetalldict = {}
    darktexturebigdict = {}

    for i in range(256):
        darktexture.set_alpha(i)
        darktexturesmall.set_alpha(i)
        darktexturelong.set_alpha(i)
        darktexturetall.set_alpha(i)
        darktexturebig.set_alpha(i)
        darktexturedict[i] = darktexture.copy()
        darktexturesmalldict[i] = darktexturesmall.copy()
        darktexturelongdict[i] = darktexturelong.copy()
        darktexturetalldict[i] = darktexturetall.copy()
        darktexturebigdict[i] = darktexturebig.copy()

class Game():
    """Main class required for the game. Initialize to start the game.
    Call .process() to begin the main game loop."""
    def __init__(self):
        """Instantiate game before starting."""
        self.tick = 1
        self.shader = shader.Shader()
        self.maxtick = 60
        self.menu = menu.Menu(Globals)
        self.state = "start"
        self.defaulttexture = blocks.Void(Globals.ppb)
        self.running = True
        self.to_reload = None
        self.action_timer = 0
        pg.display.set_icon(pg.image.load("-icon.png"))
        pg.display.set_caption("Dungeon Crawler")

    def process(self):
        """Main processing loop for the game.
        While loop is contained within.
        """
        while self.running:
            self.tick += 1
            clock.tick(60)
            if self.tick > self.maxtick:
                self.tick = 1

            if self.state == "start":
                # the main menu process terminates when the player has selected a level
                # and returns the name of the level chosen.
                level_selection = self.menu.process(self)
                self.level = leveldata.LevelData(level_selection, Globals)
                self.shader.set_dimensions(self.level)
                self.player = self.level.player
                self.state = "gameplay"

            elif self.state == "gameplay":
 
                if self.to_reload is not None:
                    self.reload()
                    self.shader.set_dimensions(self.level)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        quit()

                    # Player input
                    if event.type == pg.KEYDOWN and self.action_timer == 0:
                        ########################################################

                        self.action_timer = 2
                        if event.key == pg.K_a:
                            if self.player.inventory.open:
                                self.player.inventory.input("a")
                            else:
                                self.player.left(self.level)
                        elif event.key == pg.K_d:
                            if self.player.inventory.open:
                                self.player.inventory.input("d")
                            else:
                                self.player.right(self.level)
                        elif event.key == pg.K_w:
                            if not self.player.inventory.open:
                                self.player.up(self.level)
                        elif event.key == pg.K_s:
                            if self.player.inventory.open:
                                self.player.inventory.closing = True
                            else:
                                self.player.down(self.level)
                        elif event.key == pg.K_e and not self.player.inventory.open:
                            for entity in self.level.entities:
                                if entity.interactable and (entity.x, entity.y) == tuple(self.player.facing_tile):
                                    entity.interacted = True
                            self.player.interacted = True
                            self.player.turn = False
                        elif event.key == pg.K_f and not self.player.inventory.open:
                            self.level.entities.append(entities.Fireball(self.player.facing_tile, (self.player.x, self.player.y), friendly=True))
                            self.player.turn = False
                        elif event.key == pg.K_q and not self.player.inventory.open:
                            self.player.turn = False
                            self.player.casting = True
                        elif event.key == pg.K_SPACE and not self.player.inventory.open:
                            self.player.attacked = True
                            self.player.turn = False
                        elif event.key == pg.K_ESCAPE:
                            ...
                            # self.running = False
                        elif event.key == pg.K_r:
                            if not self.player.inventory.open:
                                self.player.inventory.opening = True
                            else:
                                self.player.inventory.closing = True
                        itemused = None
                        if self.player.inventory.open:
                            if event.key == pg.K_LEFT:
                                self.player.inventory.input("left")
                            elif event.key == pg.K_RIGHT:
                                self.player.inventory.input("right")
                            elif event.key == pg.K_DOWN:
                                self.player.inventory.input("down")
                            elif event.key == pg.K_UP:
                                self.player.inventory.input("up")
                            elif event.key == pg.K_SPACE:
                                itemused = self.player.inventory.item("selected")
                        else:
                            if event.key == pg.K_LEFT:
                                itemused = self.player.inventory.item("left")
                            elif event.key == pg.K_RIGHT:
                                itemused = self.player.inventory.item("right")
                            elif event.key == pg.K_DOWN:
                                itemused = self.player.inventory.item("down")
                            elif event.key == pg.K_UP:
                                itemused = self.player.inventory.item("up")
                        if itemused != None:
                            self.player.turn = False
                            self.useitem(itemused)
                        ############################################################

                    if self.action_timer > 0:
                        self.action_timer -= 1
                        if self.action_timer < 0:
                            self.action_timer = 0

                # Processing
                self.frame_update()
                if not self.player.turn:
                    for entity in self.level.entities:
                        entity.call_pathfind(self.level, (self.player.x, self.player.y), self.level.entities)
                    self.update()
                self.render()

            elif self.state == "win":
                # Looping for victory screen
                self.winscreen()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            pg.display.set_mode((600, 600))
                            self.state = "start"

            elif self.state == "lose":
                # Looping for loss screen
                self.losescreen()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            pg.display.set_mode((600, 600))
                            self.state = "start"
            pg.event.pump()

    def useitem(self, item):
        name = item.name
        if name == "Fireball Spell":
            self.level.entities.append(entities.Fireball(self.player.facing_tile, (self.player.x, self.player.y), damage=item.damage))
            self.player.sprite_state = "cast-"
            self.player.animation_frame = 0
        elif name == "Bomb Spell":
            self.level.entities.append(entities.Bomb((self.player.x, self.player.y)))
            self.player.sprite_state = "die-"
            self.player.animation_frame = 0
        elif name == "Bow":
            print("Not yet implemented!")
        elif name == "Potion":
            self.player.heal(item.heal)
            self.level.entities.append(entities.HealParticle((self.player.x, self.player.y)))
            self.player.sprite_state = "die-"
            self.player.animation_frame = 0
        elif name == "Longsword":
            self.player.sprite_state = "attack-2-"
            self.player.animation_frame = 0
            self.level.entities.append(entities.Sword("0", self.player.facing_tile, self.player.facing))
            secondprojectile = [self.player.facing_tile[0], self.player.facing_tile[1]]
            if self.player.facing == 4:
                secondprojectile[0] -= 1
            elif self.player.facing == 6:
                secondprojectile[0] += 1
            elif self.player.facing == 8:
                secondprojectile[1] -= 1
            elif self.player.facing == 2:
                secondprojectile[1] += 1   
            self.level.entities.append(entities.Sword("1", secondprojectile, self.player.facing))
        self.player.inventory.update()

    def sort_entities(self):
        temp = []
        for entity in self.level.entities:
            if entity.list_priority:
                temp.insert(0, entity)
            else:
                temp.append(entity)
        self.level.entities = temp

    def render(self):
        """Renders all assets to the screen based on their current sprites
        and position attributes.
        """
        # setting up variables for more comprehensible pg method calls
        Globals.screen.fill((0, 0, 0))
        midpointx = int(Globals.tilesx / 2)
        midpointy = int(Globals.tilesy / 2)
        offsetx = self.player.x - midpointx
        offsety = self.player.y - midpointy
        dim = (Globals.ppb, Globals.ppb)
        ppb = Globals.ppb
        sp = self.player.arrowsprites # sprites
        po = int(ppb * 0.05) # player offset
        facing_interactable = False

        self.sort_entities()
        render_array = []
        for i in range(Globals.tilesy):
            render_array.append([])
            for j in range(Globals.tilesx):
                render_array[i].append(self.defaulttexture)
                if i + offsety > -1 and j + offsetx > -1 and i + offsety < self.level.height and j + offsetx < self.level.width:
                    render_array[i][j] = self.level.rows[i + offsety][j + offsetx]
                Globals.screen.blit(render_array[i][j].sprite, (ppb*j, ppb*i))
        for entity in self.level.entities:
            if entity.x - offsetx in range(Globals.tilesx) and entity.y - offsety in range(Globals.tilesy):
                Globals.screen.blit(entity.get_sprite(), (ppb*(entity.x - offsetx), (entity.y - offsety)*ppb))
                if entity.interactable and (entity.x, entity.y) == tuple(self.player.facing_tile):
                    facing_interactable = True
        Globals.screen.blit(self.player.sprite, (midpointx*ppb, midpointy*ppb - po))
        self.render_arrows(facing_interactable)
        self.render_shading(offsetx, offsety, dim, ppb)
        if self.player.inventory.open or self.player.inventory.opening:
            self.player.inventory.render(Globals.screen)
        self.player.ui.render(self.player, Globals, self.player.inventory)
        
        pg.display.flip()

    def render_arrows(self, facing_interactable):
        """Subroutine for the render() method. Overlays arrows dependent on
        where the player is facing and on whether or not they are facing
        an interactable object (boolean to be passed).
        """
        cycle = round(4 * self.tick / self.maxtick)
        if cycle == 4:
            cycle = 2
        elif cycle == 0:
            cycle = 2
        sp = self.player.arrowsprites
        ppb = Globals.ppb
        midpointx = int(Globals.tilesx / 2)
        midpointy = int(Globals.tilesy / 2)
        if self.player.facing == 4:
            location = ((midpointx - 1)*ppb, midpointy*ppb)
        elif self.player.facing == 6:
            location = ((midpointx + 1)*ppb, midpointy*ppb)
        elif self.player.facing == 8:
            location = (midpointx*ppb, (midpointy - 1)*ppb)
        elif self.player.facing == 2:
            location = (midpointx*ppb, (midpointy + 1)*ppb)
        spritecode = str(self.player.facing)
        if facing_interactable:
            spritecode = "c"
        spritecode += str(cycle)
        Globals.screen.blit(sp[spritecode], location)

    def render_shading(self, offsetx, offsety, dim, ppb):
        """Subroutine for the render() method. Gets a shadow map from
        shader.py and draws it on the screen. Upscaling is currently not
        working as intended, but can be tested by setting self.shader.upscale
        to True. If upscaling is enabled, the routine will enlarge the shadow map
        and use bilinear interpolation to smoothen the lighting."""
        if self.shader.upscale == True:
            offsetx *= 3
            offsety *= 3
            resolution = 3
            ppb = int(Globals.ppb /3)
        else:
            resolution = 1
        lightlist = []
        lightlist.append([self.player.light, self.player.x, self.player.y])
        for entity in self.level.entities:
            if entity.luminescent:
                lightlist.append([entity.light, entity.x, entity.y])
        array = self.shader.generate_shadow_array(lightlist)
        render_array = []
        for i in range(Globals.tilesy * resolution):
            render_array.append([])
            for j in range(Globals.tilesx * resolution):
                render_array[i].append(0)
                if i + offsety > -1 and j + offsetx > -1 and i + offsety < len(array) and j + offsetx < len(array[0]):
                    render_array[i][j] = array[i + offsety][j + offsetx]
                if render_array[i][j] != None and render_array[i][j] < 255:
                    if self.shader.upscale:
                        if i % 3 == 0 == j % 3:
                            Globals.screen.blit(Globals.darktexturebigdict[255 - render_array[i][j]], (ppb*j, ppb*i))
                        elif i % 3 == 0:
                            Globals.screen.blit(Globals.darktexturetalldict[255 - render_array[i][j]], (ppb*j, ppb*i))
                        elif j % 3 == 0:
                            Globals.screen.blit(Globals.darktexturelongdict[255 - render_array[i][j]], (ppb*j, ppb*i))
                        else:
                            Globals.screen.blit(Globals.darktexturesmalldict[255 - render_array[i][j]], (ppb*j, ppb*i))
                    else:
                        Globals.screen.blit(Globals.darktexturedict[255 - render_array[i][j]], (round(ppb*j), round(ppb*i)))
        # self.debug(array)

    def debug(self, array):
        """Not part of the game, but could be converted to a method to render a minimap.
        Currently displays a representation of a shadowmap array on an arbitrary location
        on-screen. This is intended for debugging the upscaling algorithm in Shader.
        """
        size = 2
        white = pg.image.load("./sprites/whitepixel.png").convert()
        white = pg.transform.scale(white, (size, size))
        purple = pg.image.load("./sprites/purple.png").convert()
        purple = pg.transform.scale(purple, (size, size))
        black = pg.transform.scale(Globals.darktexture, (size, size))
        black.set_alpha(0)
        for i in range(len(array)):
            for j in range(len(array[0])):
                if array[i][j] == None:
                    Globals.screen.blit(purple, (j * size + Globals.resolutionx / 2 + 200, i * size + Globals.resolutiony))
                elif 0 <= array[i][j] <= 255:
                    Globals.screen.blit(black, (j * size + Globals.resolutionx / 2 + 200, i * size + Globals.resolutiony))
                    white.set_alpha(array[i][j])
                    Globals.screen.blit(white, (j * size + Globals.resolutionx / 2 + 200, i * size + Globals.resolutiony))

    def update(self):
        """Calls all entities on the screen to update. All update methods
        should return either None or a list of entity objects to add to the game.
        This list should include the entity called, otherwise they are removed
        from the level.
        """
        self.sort_entities()
        # ensure projectiles behave as intended with collision order
        temp_entities = []
        for i in range(len(self.level.entities)):
            temp_entities = self.level.entities[i].update(self.level.rows, self.player, Globals, self.level.entities) + temp_entities
        for entity in temp_entities:
            if entity.__class__.__name__ == "Teleporter":
                if entity.interacted is True:
                    if entity.destination == "LEVELCLEAR":
                        self.state = "win"
                        return
                    self.to_reload = entity.destination
        self.level.entities = temp_entities
        self.player.update(self)
    
    def frame_update(self):
        """Calls all entities.frame_update() methods.
        These methods work much the same as normal update() methods,
        but should be used to update sprites or remove entities that
        should not be rendered anymore (i.e. projectiles that are fading out),
        and to call entities to update their sprites if they are animated.
        """
        temp_entities = []
        for i in range(len(self.level.entities)):
            temp_entities = self.level.entities[i].frame_update() + temp_entities
        self.level.entities = temp_entities
        self.player.frame_update(self)
        self.player.inventory.frame_update()
    
    def reload(self):
        """Loads a game.to_reload but retains the player
        object, only changing their position attributes.
        """
        self.level = leveldata.LevelData(self.to_reload, Globals)
        xdiff = self.player.x - self.level.player.x
        ydiff = self.player.y - self.level.player.y
        self.player.facing_tile = [self.player.facing_tile[0] - xdiff, self.player.facing_tile[1] - ydiff]
        self.player.x = self.level.player.x
        self.player.y = self.level.player.y
        self.to_reload = None
        self.shader.set_dimensions(self.level)

    def winscreen(self):
        """Renders the victory screen and flips the surface"""
        Globals.screen.fill((0, 0, 0))
        youwin = Globals.textfont_40p.render("Victory Achieved!", True, (255, 255, 255))
        instruction = Globals.textfont_30p.render("Press SPACE to go back to the main menu.", True, (255, 255, 0))
        Globals.screen.blit(youwin, (int((Globals.resolutionx - youwin.get_width())/2), int(Globals.resolutiony - youwin.get_height())/2))
        Globals.screen.blit(instruction, (int((Globals.resolutionx - instruction.get_width())/2), int(Globals.resolutiony - instruction.get_height())/2 + 60))
        pg.display.flip()

    def losescreen(self):
        """Renders the loss screen and flips the surface"""
        Globals.screen.fill((0, 0, 0))
        youlose = Globals.textfont_40p.render("YOU DIED", True, (255, 0, 0))
        instruction = Globals.textfont_30p.render("Press SPACE to go back to the main menu.", True, (255, 255, 0))
        Globals.screen.blit(youlose, (int((Globals.resolutionx - youlose.get_width())/2), int(Globals.resolutiony - youlose.get_height())/2))
        Globals.screen.blit(instruction, (int((Globals.resolutionx - instruction.get_width())/2), int(Globals.resolutiony - instruction.get_height())/2 + 60))
        pg.display.flip()


game = Game()
try:
    game.process()
except SystemExit:
    pg.quit()
    input()


