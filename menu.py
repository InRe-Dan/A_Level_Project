import pygame as pg
import os

class Menu():
    def __init__(self, assets):
        self.textfont = assets.textfont_40p
        self.textfont_s = assets.textfont_30p
        self.titletext = self.textfont.render("Dungeon Crawler", True, (255, 255, 255))
        self.playtext = self.textfont_s.render("Play", True, (255, 255, 0))
        self.state = "main"
        self.height = 600
        self.width = 600
        self.pointer = LevelSelector(self)
        self.movesound = pg.mixer.Sound("audio/sounds/menumove.wav")
        self.selectsound = pg.mixer.Sound("audio/sounds/menuconfirm.wav")
        self.assets = assets
    def process(self, game) -> "Name of selected level":
        """Call once to start the process routine."""
        done = False
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                if event.type == pg.KEYDOWN:
                    if self.state == "main":
                        if event.key == pg.K_SPACE:
                            self.selectsound.play()
                            self.state = "levels"
                        if event.key == pg.K_ESCAPE:
                            self.selectsound.play()
                            quit()
                    elif self.state == "levels":
                        if event.key == pg.K_ESCAPE:
                            self.state = "main"
                            self.movesound.play()
                        elif event.key == pg.K_s and self.pointer.pos < len(self.pointer.level_list) - 1:
                            self.pointer.pos += 1
                            self.movesound.play()
                        elif event.key == pg.K_w and self.pointer.pos > 0:
                            self.pointer.pos -= 1
                            self.movesound.play()
                        elif event.key == pg.K_SPACE:
                            self.selectsound.play()
                            selected = self.pointer.level_list[self.pointer.pos]
                            self.state = "main"
                            return selected
            self.render()
            pg.event.pump()

    def render(self):
        """Renders the main menu - this function is accounts for and
        is dependend on the Menu.state attribute.
        """
        self.assets.screen.fill((0, 0, 0))
        self.assets.screen.blit(self.titletext, (int(self.width/2) - int(self.titletext.get_width()/2),
                                          100 - self.titletext.get_height()))
        if self.state == "main":
            self.assets.screen.blit(self.playtext, (int(self.width/2) - int(self.playtext.get_width()/2),
                                             int(self.height/3) - self.playtext.get_height()))
        elif self.state == "levels":
            page = self.pointer.get_page()
            for i in range(len(page)):
                lvname = self.textfont_s.render(page[i], True, (255, 255, 255))
                if i == self.pointer.get_pos_on_page():
                    lvname = self.textfont_s.render(page[i], True, (255, 255, 0))
                else:
                    lvname = self.textfont_s.render(page[i], True, (255, 255, 255))
                self.assets.screen.blit(lvname, (int(self.width/2) - int(lvname.get_width()/2), 155 + (i * lvname.get_height())))
            i += 2
            pagetext = self.textfont_s.render(f"Page {self.pointer.get_page_number()}/{len(self.pointer.pages)}", True, (200, 200, 200))
            self.assets.screen.blit(pagetext, (int(self.width/2) - int(pagetext.get_width()/2), 155 + (i * pagetext.get_height())))
        pg.display.flip()

class LevelSelector():
    """Object to be embedded in the Menu object, used to determine
    where the player is pointing to on the level select screen.
    """
    def __init__(self, menu):
        self.pos = 0
        self.level_list = []
        levels_temp = sorted(os.listdir("levels"))
        for i in range(len(levels_temp)):
            if not levels_temp[i].startswith("hidden-"):
                self.level_list.append(levels_temp[i])
        self.max_levels_per_page = round(((menu.height * 2/3) - 50)/menu.playtext.get_height())
        self.pages = [[]]
        for i in range(len(self.level_list)):
            if len(self.pages[-1]) < self.max_levels_per_page:
                self.pages[-1].append(self.level_list[i])
            else:
                self.pages.append([])
                self.pages[-1].append(self.level_list[i])

    def get_page(self) -> "Current page index":
        page = self.pages[self.pos // self.max_levels_per_page]
        return page

    def get_page_number(self):
        return self.pos // self.max_levels_per_page + 1

    def get_pos_on_page(self) -> "Current position index":
        return self.pos % self.max_levels_per_page