"""File to hold the player inventory class."""
import pygame as pg
import utils

spritedict = utils.make_dict("./sprites/inventory/")
# subsurface = a_surface.subsurface((x, y, width, height))
class Inventory():
    """Child of the player class, to be initialized with the
    players itself and items to add by default."""
    basesprite = pg.Surface((1, 1)).convert_alpha()
    lightcolour = pg.Surface((1, 1)).convert_alpha()
    darkcolour = pg.Surface((1, 1)).convert_alpha()
    basesprite.fill((35, 35, 35))
    lightcolour.fill((37, 39, 39))
    darkcolour.fill((28, 28, 28))
    boxsprite = pg.image.load("./sprites/inventory/box.png")

    def __init__(self, player):
        """Initializes inventory pointers and attributes.
        generate_sprite() should be called separately before
        the main game loop begins.
        """
        self.open = False
        self.opening = False
        self.closing = False
        self.items = []
        self.capacity = 0
        self.pointer = 0
        self.item_broke = False
        self.upindex = None
        self.downindex = None
        self.rightindex = None
        self.leftindex = None
    
    def generate_sprite(self, assets):
        """Routine used to set up the size of the menu,
        requires Globals as a parameter for computing
        proportions and positions.
        """
        self.width = int(assets.resolutionx * 0.4)
        self.height = int(assets.resolutionx * 0.2)
        self.screenheight = assets.resolutiony
        self.incrementvalue = int(0.05 * assets.resolutiony)
        self.current_position = assets.resolutiony
        self.renderposx = int(assets.resolutionx - self.width - 10)
        self.renderposy = int(assets.resolutiony - self.height - 10)

        self.contour_width = int(self.height * 0.025)
        contour_width = self.contour_width
        self.usable_dimensions = (self.width - contour_width * 2, self.height - contour_width * 2)
        cornerpiece = pg.image.load("./sprites/inventory/corner.png").convert_alpha()
        cornerpiece = pg.transform.scale(cornerpiece, (contour_width, contour_width))

        self.sprite = pg.transform.scale(self.basesprite, (self.width, self.height))
        self.sprite.blit(cornerpiece, (0, 0))
        self.sprite.blit(cornerpiece, (self.width - contour_width, self.height - contour_width))
        self.sprite.blit(pg.transform.scale(self.darkcolour, (contour_width, self.height - contour_width)), (0, contour_width))
        self.sprite.blit(pg.transform.scale(self.lightcolour, (self.width - contour_width, contour_width)), (contour_width, 0))
        self.sprite.blit(pg.transform.scale(self.darkcolour, (self.width - 2*contour_width, contour_width)), (contour_width, self.height - contour_width))
        self.sprite.blit(pg.transform.scale(self.lightcolour, (contour_width, self.height - 2 * contour_width)), (self.width - contour_width, contour_width))
        self.sprite.convert_alpha()

        headertext = assets.textfont_40p.render("Inventory", True, (255, 255, 255))
        headertext_shadow = assets.textfont_40p.render("Inventory", True, (0, 0, 0))
        right = int((self.width - headertext.get_width()) / 2)
        down = int((self.height * 0.15))
        self.sprite.blit(headertext_shadow, (right + 2, down + 2))
        self.sprite.blit(headertext, (right, down))

        self.boxspritedim = (int(self.width * 0.2), int(self.width * 0.2))
        self.boxsprite = pg.transform.scale(self.boxsprite, self.boxspritedim).convert_alpha()
        for key in spritedict:
            spritedict[key] = pg.transform.scale(spritedict[key], self.boxspritedim).convert_alpha()
        
        backglow = pg.Surface((self.boxspritedim[0] - 1, self.boxspritedim[0] - 1))
        backglow.fill((100, 100, 100))
        self.sprite.blit(backglow, (int((self.width - self.boxspritedim[0])/ 2) + 3, self.height * 0.4 + 4))

        self.slotswitharrows = {}
        arrow = spritedict["arrowup"]
        pg.transform.scale(arrow, self.boxspritedim)
        arrowbox = pg.Surface(self.boxspritedim).convert_alpha()
        for direction in ["up", "left", "down", "right"]:
            arrowbox.fill((20, 20, 20, 230))
            arrowbox.blit(arrow.copy(), (0, 0))
            arrow = pg.transform.rotate(arrow, 90)
            arrowbox.blit(self.boxsprite, (0, 0))
            self.slotswitharrows[direction] = arrowbox.copy()



    def input(self, key):
        """Changes inventory attributes based on the key parameter."""
        if key == "d":
            self.pointer += 1
            if self.pointer == self.capacity:
                self.pointer = 0
        elif key == "a":
            self.pointer -= 1
            if self.pointer == -1:
                self.pointer = self.capacity - 1
        if self.pointer > -1:
            if key == "up":
                self.upindex = self.pointer
            elif key == "down":
                self.downindex = self.pointer
            elif key == "right":
                self.rightindex = self.pointer
            elif key == "left":
                self.leftindex = self.pointer
        if key == "space":
            if self.capacity != 0:
                self.items[self.pointer].use(self)

    def make_wheel(self) -> "Item Wheel Surface":
        # there will always be five items on display, regardless of dimensions
        p = self.pointer
        c = self.capacity
        if c == 0:
            wheeldata = None
        elif self.capacity == 1:
            wheeldata = [0, 0, 0, 0, 0]
        elif c == 2:
            if p == 0:
                wheeldata = [0, 1, 0, 1, 0]
            else:
                wheeldata = [1, 0, 1, 0, 1]
        elif c == 3:
            if p == 0:
                wheeldata = [1, 2, 0, 1, 2]
            elif p == 1:
                wheeldata = [2, 0, 1, 2, 0]
            else:
                wheeldata = [0, 1, 2, 0, 1]
        elif c == 4:
            if p == 0:
                wheeldata = [2, 3, 0, 1, 2]
            elif p == 1:
                wheeldata = [3, 0, 1, 2, 3]
            elif p == 2:
                wheeldata = [0, 1, 2, 3, 0]
            else:
                wheeldata = [1, 2, 3, 0, 1]
        else:
            if p == 0:
                wheeldata = [-2, -1, 0, 1, 2]
            elif p == 1:
                wheeldata = [-1, 0, 1, 2, 3]
            elif p == c - 1:
                wheeldata = [c - 3, c - 2, c - 1, 0, 1]
            elif p == c - 2:
                wheeldata = [c - 4, c - 3, c - 2, c - 1, 0]
            else:
                wheeldata = [p-2, p-1, p, p+1, p+2]
        transparent = pg.Color(0, 0, 0, 0)
        wheelsurface = pg.Surface((self.boxspritedim[0] * 6, self.boxspritedim[0]), pg.SRCALPHA).convert_alpha()
        sizedsurface = pg.Surface((self.usable_dimensions[0], self.boxspritedim[0]), pg.SRCALPHA).convert_alpha()
        for i in range(5):
            if wheeldata != None:
                wheelsurface.blit(self.items[wheeldata[i]].render_sprite, (int(1.25 * self.boxspritedim[0]) * i, 0))
            else:
                box = pg.Surface(self.boxspritedim)
                box.fill((20, 20, 20, 230))
                wheelsurface.blit(box,(int(1.25 * self.boxspritedim[0]) * i, 0))
                wheelsurface.blit(self.boxsprite,(int(1.25 * self.boxspritedim[0]) * i, 0))
        sizedsurface.blit(wheelsurface, (0, 0), ((self.boxspritedim[0] * 6 - self.usable_dimensions[0])/2, 0, self.usable_dimensions[0], self.boxspritedim[0]))
        return sizedsurface

    def update(self):
        """Checks to see if an item has been broken and removes
        it from the inventory.
        """
        for i in range(len(self.items)):
             if self.items[i].breakable and self.items[i].durability <= 0:
                if self.leftindex == i:
                    self.leftindex = None
                if self.rightindex == i:
                    self.rightindex = None
                if self.upindex == i:
                    self.upindex = None
                if self.downindex == i:
                    self.downindex = None
                self.decrement_indices(i)
                self.items.pop(i)
                self.capacity -= 1
                if self.pointer > 0:
                    self.pointer -= 1
                elif self.capacity > 0:
                    self.pointer = self.capacity - 1
                else:
                    self.pointer = 0
                return

    def decrement_indices(self, index):
        """Shift items when one before them in the list is broken."""
        if self.leftindex is not None and self.leftindex >= index:
            self.leftindex -= 1
        if self.rightindex is not None and self.rightindex >= index:
            self.rightindex -= 1
        if self.upindex is not None and self.upindex >= index:
            self.upindex -= 1
        if self.downindex is not None and self.downindex >= index:
            self.downindex -= 1

    def frame_update(self):
        """Call every frame to update the inventory's
        position based on whether it is opening or closing.
        """
        if not self.open and self.opening:
            self.current_position -= self.incrementvalue
            if self.current_position < self.renderposy:
                self.current_position = self.renderposy
                self.opening = False
                self.open = True
        elif self.open and self.closing:
            self.current_position += self.incrementvalue
            if self.current_position > self.screenheight:
                self.current_position = self.screenheight
                self.open = False
                self.closing = False

    def render(self, surface):
        """Renders the inventory to the screen surface given."""
        invsprite = self.sprite.copy()
        itemwheel = self.make_wheel()
        invsprite.blit(itemwheel, (self.contour_width, int(self.height * 0.4)))
        topleft = (self.renderposx, self.current_position)
        surface.blit(invsprite, topleft)

    
    def add(self, item):
        """Adds one item to the inventory to be passed in the string
        format "Item(attribute1="foo", attribute2="bar") for use of eval().
        """
        item = eval(item)
        item.generate_box(self)
        self.items.append(item)
        self.capacity += 1

    def item(self, request):
        """Return the item used based on gameplay input."""
        if request == "left" and self.leftindex != None:
            return self.items[self.leftindex].use(self)
        elif request == "right" and self.rightindex != None:
            return self.items[self.rightindex].use(self)
        elif request == "down" and self.downindex != None:
            return self.items[self.downindex].use(self)
        elif request == "up" and self.upindex != None:
            return self.items[self.upindex].use(self)
        elif request == "selected" and self.capacity > 0:
            return self.items[self.pointer].use(self)
        self.update()

class Item():
    """Base class for items, and contains the generate_box(),
    update_render_sprite() and use() methods.
    """    
    def generate_box(self, inventory):
        """Creates the item frame for the item."""
        self.box = pg.Surface(inventory.boxspritedim).convert_alpha()
        self.box.fill((20, 20, 20, 230))
        self.box.blit(self.sprite, (0, 0))
        self.box.blit(inventory.boxsprite, (0, 0))
        self.render_sprite = self.box
    def update_render_sprite(self):
        """Updates the item frame to reflect durability. Call
        on every use().
        """
        if self.breakable and self.durability != self.max_durability:
            self.render_sprite = self.box.copy().convert_alpha()
            fraction = self.durability/self.max_durability
            length = int(self.box.get_width() * 0.8 * fraction)
            bar = pg.Surface((length, int(self.render_sprite.get_height() * 0.03))).convert_alpha()
            green = int(fraction * 255)
            red = 255 - green
            bar.fill((red, green, 0))
            self.render_sprite.blit(bar, (int(self.box.get_width() * 0.1), int(0.9 * self.box.get_height())))

    def use(self, inv):
        """If the item is breakable, durability is decremented and sprite
        is updated. Returns itself."""
        if self.breakable:
            self.durability -= 1
            if self.durability > 0:
                self.update_render_sprite()
        return self

# Item effects are dictated in index. These classes simply help inventory management.

class Longsword(Item):
    def __init__(self, breakable=True, durability=3):
        self.name = "Longsword"
        self.sprite = spritedict["sword"]
        self.breakable = breakable
        self.durability, self.max_durability = durability, durability

class Fireball(Item):
    def __init__(self, breakable=True, durability=3, damage=50):
        self.name = "Fireball Spell"
        self.damage = damage
        self.sprite = spritedict["fireball"]
        self.breakable = breakable
        self.durability, self.max_durability = durability, durability

class Bomb(Item):
    def __init__(self, breakable=True, durability=1):
        self.name = "Bomb Spell"
        self.sprite = spritedict["bomb"]
        self.breakable = breakable
        self.durability, self.max_durability = durability, durability

class Potion(Item):
    def __init__(self, breakable=True, durability=1, heal=50):
        self.heal = heal
        self.name = "Potion"
        self.sprite = spritedict["potion"]
        self.breakable = breakable
        self.durability, self.max_durability = durability, durability

class Bow(Item):
    def __init__(self, breakable=False, durability=1):
        self.name = "Bow"
        self.sprite = spritedict["bow"]
        self.breakable = breakable
        self.durability, self.max_durability = durability, durability
        