import pygame as pg
class UserInterface():
    """Child Class of Game, represents the UI for a specific level.
    Uses data from game.player to add stats and items.
    """
    def __init__(self, player, assets):
        self.width = assets.resolutionx
        self.height = 192
        self.vert_location = assets.resolutiony - self.height
        self.sprite = pg.image.load("sprites/uimenu.png").convert_alpha()
        # todo - transform sprites here for optimization
        sp1 = pg.image.load("sprites/goldheart.png")
        sp2 = pg.image.load("sprites/heart.png")
        sp3 = pg.image.load("sprites/heartbroken.png")
        self.heartsprites = [sp1, sp2, sp3]
        self.max_health = player.max_health
        self.max_hearts = int(self.width / 140)
        self.heart_value = self.max_health / self.max_hearts
        self.base_surface = pg.Surface((self.width, self.height)).convert_alpha()
        self.base_surface.blit(self.sprite, (0, 0))
        self.itemdisplayborders = 10
        self.bsi_dimensions = (player.inventory.boxspritedim[0] * 3 + 4 * self.itemdisplayborders, player.inventory.boxspritedim[0] * 2 + self.itemdisplayborders * 3)
        self.baseitemsurface = pg.Surface(self.bsi_dimensions).convert_alpha()
        self.baseitemsurface.fill((0, 0, 0, 0))


    def calculate_hearts(self, player):
        """Returns a tuple of gold hearts, regular hearts and broken
        hearts to be rendered considering player health. Pass the player
        object.
        """
        if player.health > self.max_health:
            return (self.max_hearts, 0, 0)
        halfhearts = int(round((player.health / self.heart_value) * 2))
        if halfhearts % 2 == 0:
            return (0, int(round(halfhearts / 2)), 0)
        return (0, int(halfhearts / 2), 1)

    def render(self, player, assets, inventory):
        """Renders the UI given the player and Globals."""
        surface = self.base_surface.copy()
        hp = "Life: " + str(player.health) + " / " + str(player.max_health)
        if player.max_health < player.health:
            lifetext = assets.textfont_30p.render(hp, True, (255, 255, 0))
        elif player.health * 2 < player.max_health:
            lifetext = assets.textfont_30p.render(hp, True, (255, 0, 0))
        else:
            lifetext = assets.textfont_30p.render(hp, True, (255, 255, 255))
        lifetextshadow = assets.textfont_30p.render(hp, True, (0, 0, 0))
        hearts = self.calculate_hearts(player)
        if hearts[0] > 0:
            for i in range(hearts[0]):
                surface.blit(self.heartsprites[0], (20 + i * 70, 20))
        elif hearts[2] > 0:
            for i in range(hearts[1]):
                surface.blit(self.heartsprites[1], (20 + i * 70, 20))
            surface.blit(self.heartsprites[2], (20 + hearts[1] * 70, 20))
        else:
            for i in range(hearts[1]):
                surface.blit(self.heartsprites[1], (20 + i * 70, 20))
        surface.blit(lifetextshadow, (22, 92))
        surface.blit(lifetext, (20, 90))
        assets.screen.blit(surface, (0, assets.resolutiony))

        itemdisplay = self.baseitemsurface.copy()
        bsd = inventory.boxspritedim[0]
        
        # if no item render empty box, if item render item
        if inventory.upindex != None:
            itemdisplay.blit(inventory.items[inventory.upindex].render_sprite, (bsd + 2 * self.itemdisplayborders, self.itemdisplayborders))
        else:
            itemdisplay.blit(inventory.slotswitharrows["up"], (bsd + 2 * self.itemdisplayborders, self.itemdisplayborders))
        if inventory.leftindex != None:
            itemdisplay.blit(inventory.items[inventory.leftindex].render_sprite, (self.itemdisplayborders, bsd + 2 * self.itemdisplayborders))
        else:
            itemdisplay.blit(inventory.slotswitharrows["left"], (self.itemdisplayborders, bsd + 2 * self.itemdisplayborders))
        if inventory.downindex != None:
            itemdisplay.blit(inventory.items[inventory.downindex].render_sprite, (bsd + 2 * self.itemdisplayborders, bsd + 2 * self.itemdisplayborders))
        else:
            itemdisplay.blit(inventory.slotswitharrows["down"], (bsd + 2 * self.itemdisplayborders, bsd + 2 * self.itemdisplayborders))
        if inventory.rightindex != None:
            itemdisplay.blit(inventory.items[inventory.rightindex].render_sprite, ((bsd + self.itemdisplayborders) * 2 + self.itemdisplayborders, bsd + 2 * self.itemdisplayborders))
        else:
            itemdisplay.blit(inventory.slotswitharrows["right"], ((bsd + self.itemdisplayborders) * 2 + self.itemdisplayborders, bsd + 2 * self.itemdisplayborders))

        height = int(0.8 * self.height)
        scaling = height / itemdisplay.get_height()
        width = int(scaling * self.bsi_dimensions[0])
        itemdisplay = pg.transform.scale(itemdisplay, (width, height))
        location = (int(assets.resolutionx * 3 / 4) - int(width / 2), assets.resolutiony + int((self.height - height) / 2))
        assets.screen.blit(itemdisplay, location)

        