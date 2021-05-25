from display import *
from engine import *


# Character Skills:
class Skill(pygame.sprite.Sprite):
    def __init__(self, name, image, cd, target_type, range=0, radius=0 , effect=None, projectile=None):
        super().__init__()
        self.name = name
        self.image = image
        self.cd = cd
        self.timer = cd

        self.effect = effect
        self.projectile = projectile
        self.range = range
        self.radius = radius
        self.target_type = target_type
        self.target_area = None  # Single / Trap Area / Line?

        self.dmg_counter = 0


class Talent(pygame.sprite.Sprite):  # ez azért kell mert kell grafika, és adatok
    def __init__(self, image, hp=0, dmg=0, speed=0, cost_red=0, upkeep_output=0, comfort_trap_dmg=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.status = 'Inactive'

        self.hp = hp
        self.dmg = dmg
        self.speed = speed
        self.cost_red = cost_red
        self.upkeep_output = upkeep_output
        self.comfort_trap_dmg = comfort_trap_dmg
        # minden szint buffjainak összegét szorozza a megfelelő stattal.

        self.text = ''
        # a talent ikonok alatt ki kéne írnia mit is csinál. Tehát a szív ikon adna pl '+ 5 hp'-t.
        # Ezt a szöveget pedig az adatokból állítaná össze, a létrehozásukkor.

    def __copy__(self):
        return Talent(
            self.image, hp=self.hp, dmg=self.dmg, speed=self.speed, cost_red=self.cost_red,
            upkeep_output=self.upkeep_output, comfort_trap_dmg=self.comfort_trap_dmg)


hp_buff = Talent(heart_icon, hp=4)
dmg_buff = Talent(damage_icon, dmg=4)
speed_buff = Talent(speed_icon, speed=4)
cost_red_buff = Talent(cost_red_icon, cost_red=4)
upkeep_output_buff = Talent(upkeep_output_icon, upkeep_output=4)
comfort_trap_dmg_buff = Talent(comfort_trap_dmg_icon, comfort_trap_dmg=4)

talent_dict = {
    1: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    2: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    3: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    4: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    5: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    6: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    7: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    8: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    9: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    10: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    11: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    12: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    13: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    14: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    15: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    16: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    17: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    18: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    19: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__())),
    20: ((hp_buff.__copy__(), dmg_buff.__copy__(), speed_buff.__copy__()), (cost_red_buff.__copy__(), upkeep_output_buff.__copy__(), comfort_trap_dmg_buff.__copy__()))
}


class TalentTree:
    def __init__(self, width, height, talent_dict, style='comicsans'):
        self.size = (width, height)
        self.width = width * 8/10
        self.height = height * 8/10
        self.x = width * 1/10
        self.y = height * 1/10

        self.talent_dict = talent_dict

        # Rectangles
        self.talent_tree_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.xp_bar_rect = pygame.Rect(self.size[0] * 18/100, height * 7/65, self.size[0] * 64/100, height * 3/65)
        self.xp_rect = pygame.Rect(self.size[0] * 18/100, height * 7/65, 0, height * 3/65)

        # Colors
        self.border_color = (0, 0, 0)
        self.background_color = (50, 50, 50)
        self.xp_background_color = (100, 100, 100)
        self.green = (0, 255, 0)
        self.text_color = (255, 255, 255)

        # Text
        self.style = style
        self.font_size1 = int(self.height / 20)
        self.font_size2 = int(self.height / 30)
        self.font1 = pygame.font.SysFont(self.style, self.font_size1)
        self.font2 = pygame.font.SysFont(self.style, self.font_size2)

    def update(self, game_data):
        for lvl, xp in game_data.lvl_dict.items():
            if xp > game_data.xp:
                game_data.lvl = lvl - 1
                break
        self.rendered_text1 = self.font1.render(f'Level {game_data.lvl}', 1, self.text_color)
        self.rendered_text2 = self.font2.render(f'{game_data.xp} / {game_data.lvl_dict[game_data.lvl + 1]}', 1, self.text_color)

        self.xp_rect.width = self.xp_bar_rect.width * (game_data.xp - game_data.lvl_dict[game_data.lvl]) / \
                             (game_data.lvl_dict[game_data.lvl + 1] - game_data.lvl_dict[game_data.lvl])

        for lvl, talents in self.talent_dict.items():
            body_talents = talents[0]
            wrench_talents = talents[1]
            for i, talent in enumerate(body_talents):
                self.talent_dict[lvl][0][i].rect.x = self.x + (self.width * 1 / 20 - talent.rect.width) / 2 + self.width * (lvl - 1) / 20
                self.talent_dict[lvl][0][i].rect.y = self.y + self.height * 1 / 13 - talent.rect.height / 2 + self.height * 6 / 4 * (i + 1) / 13
                if lvl <= game_data.lvl and talent.status == 'Inactive':
                    self.talent_dict[lvl][0][i].status = 'Active'
            for i, talent in enumerate(wrench_talents):
                self.talent_dict[lvl][1][i].rect.x = self.x + (self.width * 1 / 20 - talent.rect.width) / 2 + self.width * (lvl - 1) / 20
                self.talent_dict[lvl][1][i].rect.y = self.y + self.height * 7 / 13 - talent.rect.height / 2 + self.height * 6 / 4 * (i + 1) / 13
                if lvl <= game_data.lvl and talent.status == 'Inactive':
                    self.talent_dict[lvl][1][i].status = 'Active'

    def set_status(self, coord, game_data):
        for lvl, talents in self.talent_dict.items():
            body_talents = talents[0]
            wrench_talents = talents[1]

            for i, talent in enumerate(body_talents):
                if talent.status == 'Active':
                    if talent.rect.collidepoint(coord):
                        for n, talent in enumerate(self.talent_dict[lvl][0]):
                            self.talent_dict[lvl][0][n].status = 'Inactive'
                        self.talent_dict[lvl][0][i].status = 'Picked'
                        return True

            for i, talent in enumerate(wrench_talents):
                if talent.status == 'Active':
                    if talent.rect.collidepoint(coord):
                        for n, talent in enumerate(self.talent_dict[lvl][1]):
                            self.talent_dict[lvl][1][n].status = 'Inactive'
                        self.talent_dict[lvl][1][i].status = 'Picked'
                        return True

    def draw(self, SCREEN):
        # Background
        pygame.draw.rect(SCREEN, self.background_color, self.talent_tree_rect)

        # Borders
        pygame.draw.line(SCREEN, self.border_color, (self.x, self.y + self.height * 1/13),
                         (self.x + self.width, self.y + self.height * 1/13), 4)
        pygame.draw.line(SCREEN, self.border_color, (self.x, self.y + self.height * 7/13),
                         (self.x + self.width, self.y + self.height * 7/13), 4)

        for x in range(1,20):
            pygame.draw.line(SCREEN, self.border_color, (self.x + self.width * x/20, self.y + self.height * 1/13),
                             (self.x + self.width * x/20, self.y + self.height), 2)
        pygame.draw.rect(SCREEN, self.border_color, self.talent_tree_rect, 4)

        # Top XP bar
        pygame.draw.rect(SCREEN, self.xp_background_color, self.xp_bar_rect)
        pygame.draw.rect(SCREEN, self.green, self.xp_rect)
        pygame.draw.rect(SCREEN, self.border_color, self.xp_bar_rect, 1)
        SCREEN.blit(self.rendered_text1, (self.x + self.width * 1/20 - round(self.rendered_text1.get_width() / 2),
                                          self.xp_bar_rect.centery - round(self.rendered_text1.get_height() / 2)))
        SCREEN.blit(self.rendered_text2, (self.x + self.width * 19/20 - round(self.rendered_text2.get_width() / 2),
                                          self.xp_bar_rect.centery - round(self.rendered_text2.get_height() / 2)))

        for lvl, talents in self.talent_dict.items():
            for i, talent in enumerate(talents[0]):
                SCREEN.blit(talent.image, talent.rect)
                if talent.status in ['Inactive', 'Declined']:
                    SCREEN.blit(black, talent.rect)
                    SCREEN.blit(frame_grey_icon, talent.rect)
                else:
                    SCREEN.blit(frame_green_icon, talent.rect)
            for i, talent in enumerate(talents[1]):
                SCREEN.blit(talent.image, talent.rect)
                if talent.status in ['Inactive', 'Declined']:
                    SCREEN.blit(black, talent.rect)
                    SCREEN.blit(frame_grey_icon, talent.rect)
                else:
                    SCREEN.blit(frame_green_icon, talent.rect)


common_talent_tree = TalentTree(client_data.width, client_data.height, talent_dict)


class Circle:
    def __init__(self, x, y, rad, color, width):
        self.x = x
        self.y = y
        self.rad = rad
        self.color = color
        self.width = width

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, (self.x, self.y), self.rad, self.width)


class BaseObj:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)


class TextObj(BaseObj):
    def __init__(self, rect, text, font_size, style='comicsans', background_color=None, text_color=(255, 255, 255)):
        super().__init__(rect)
        self.background_color = background_color
        self.text_color = text_color
        self.text = str(text)
        self.font_size = font_size
        self.style = style
        self.font = pygame.font.SysFont(self.style, self.font_size)
        self.rendered_text = self.font.render(self.text, 1, self.text_color)

    def update(self, string):
        if self.text != str(string):
            self.text = str(string)
            self.rendered_text = self.font.render(self.text, 1, self.text_color)

    def draw(self, SCREEN):
        if self.background_color:
            pygame.draw.rect(SCREEN, self.background_color, self.rect)
        SCREEN.blit(self.rendered_text, (self.rect.centerx - round(self.rendered_text.get_width()/2),
                                         self.rect.centery - round(self.rendered_text.get_height()/2)))

    def draw_text(self, SCREEN):  # ez lehet már szükségtelen
        self.rendered_text = self.font.render(self.text, 1, self.text_color)
        SCREEN.blit(
            self.rendered_text, (self.rect.centerx - round(self.rendered_text.get_width() / 2),
                                 self.rect.centery - round(self.rendered_text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        return False


class PictureObj(BaseObj):
    def __init__(self, rect, image):
        super().__init__(rect)
        self.image = image

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.rect.x <= x1 <= self.rect.x + self.rect.width and self.rect.y <= y1 <= self.rect.y + self.rect.height:
            return True
        return False

    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)


class Chat:
    def __init__(self, x, y, width, height):
        self.name_x = x
        self.name_width = 100
        self.y = y
        self.height = height
        self.msg_x = x + self.name_width
        self.msg_width = width - self.name_width
        self.name_area_color = (50, 50, 50)
        self.msg_area_color = (70, 70, 70)
        self.name_colors = [(0, 255, 0), (0, 255, 255), (255, 0, 0), (255, 255, 0)]
        self.msg_color = (255, 255, 255)
        self.font = pygame.font.SysFont('comicsans', 20)
        self.line_pixels = 15
        self.max_lines = 6
        self.name_rect = (self.name_x, self.y, self.name_width, self.height)
        self.msg_rect = (self.msg_x, self.y, self.msg_width, self.height)
        self.chat_data = []

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.name_area_color, self.name_rect)
        pygame.draw.rect(SCREEN, self.msg_area_color, self.msg_rect)

        if self.chat_data:
            for i, [player, text] in enumerate(reversed(self.chat_data)):
                if i >= self.max_lines:
                    break
                name = self.font.render(player.name, 1, self.name_colors[player.id])
                msg = self.font.render(text, 1, self.msg_color)
                SCREEN.blit(name, (self.name_x + 10, self.y + self.height - 20 - i * self.line_pixels))
                SCREEN.blit(msg, (self.msg_x + 10, self.y + self.height - 20 - i * self.line_pixels))


class SettingsButton:
    def __init__(self, x, y, name, data):
        self.name_x = x
        self.y = y
        self.name_width = 150
        self.name_height = 50
        self.data_x = x + 200
        self.data_width = 150
        self.data_height = 50
        self.name = name
        self.data = data
        self.font_size = 24
        self.style = 'comicsans'
        self.color = (40, 40, 40)
        self.font = pygame.font.SysFont(self.style, self.font_size)
        self.open = False

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, (self.name_x, self.y, self.name_width, self.name_height))
        text = self.font.render(self.name, 1, (255, 255, 255))
        SCREEN.blit(text, (self.name_x + round(self.name_width/2) - round(text.get_width()/2),
                           self.y + round(self.name_height/2) - round(text.get_height()/2)))

        pygame.draw.rect(SCREEN, self.color, (self.data_x, self.y, self.data_width, self.data_height))
        text = self.font.render(self.data, 1, (255, 255, 255))
        SCREEN.blit(text, (self.data_x + round(self.data_width / 2) - round(text.get_width() / 2),
                           self.y + round(self.data_height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.data_x <= x1 <= self.data_x + self.data_width and self.y <= y1 <= self.y + self.data_height:
            return True
        return False


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, pic, text=None, font_size=40, style='comicsans', center=False):
        super().__init__()
        self.original_image = pic
        self.image = self.original_image.copy()
        self.text = text
        self.pushed_image = None
        if center:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = self.image.get_rect(topleft=(x, y))
        self.click_sound = pygame.mixer.Sound('Sounds/splat.wav')
        self.click_sound.set_volume(0.2)

        if text:
            self.font = pygame.font.SysFont(style, font_size)
            textsurface = self.font.render(self.text, True, (250, 250, 250))
            textrect = textsurface.get_rect(center=self.image.get_rect().center)  # lehet elég a sima kérpől egy rect
            self.image.blit(textsurface, textrect)


dist = 3
button_width = 150
button_height = 50

# Main menu buttons
sp_button = Button(
    client_data.width / 2, client_data.height / 2 - 200, red_btn_pic, 'Singleplayer', 40)
mp_button = Button(
    client_data.width / 2, client_data.height / 2 - 100, red_btn_pic, 'Multiplayer', 40)
main_menu_options_button = Button(
    client_data.width / 2, client_data.height / 2 + 0, red_btn_pic, 'Options', 40)
main_menu_exit_button = Button(
    client_data.width / 2, client_data.height / 2 + 100, red_btn_pic, 'Exit', 40)

menu_btns_group = pygame.sprite.Group(
    sp_button, mp_button, main_menu_options_button, main_menu_exit_button)

# Settings menu stuff
fullscreen_btn = SettingsButton(client_data.width / 2 - 200, client_data.height / 2 - 150 + dist * 0,
                                'Fullscreen', str(client_data.fullscreen))
resolution_btn = SettingsButton(client_data.width / 2 - 200, client_data.height / 2 - 100 + dist * 1,
                                'Resolution', f'{client_data.width}x{client_data.height}')
framerate_btn = SettingsButton(client_data.width / 2 - 200, client_data.height / 2 - 50 + dist * 2,
                               'Framerate', str(client_data.framerate))
camera_scrolling_btn = SettingsButton(client_data.width / 2 - 200, client_data.height / 2 - 0 + dist * 3,
                                      'Camera Scrolling', str(client_data.cam_smoothing))
prediction_btn = SettingsButton(client_data.width / 2 - 200, client_data.height / 2 + 50 + dist * 4,
                                'Client Prediction', str(client_data.prediction))
player_name_btn = SettingsButton(client_data.width / 2 - 200, client_data.height / 2 + 100 + dist * 5,
                                 'Player Name', '')

options_back_button = Button(
    client_data.width - button_width - 50, client_data.height - 50, red_btn_pic, 'Back', 40)
options_save_button = Button(
    client_data.width - button_width - 200, client_data.height - 50, red_btn_pic, 'Save', 40)

options_btns_group = pygame.sprite.Group(
    options_back_button, options_save_button)


# Multiplayer menu buttons
test_game_button = Button(
    250, client_data.height - 100, red_btn_pic, 'Test Game', 40)
new_game_button = Button(
    50, client_data.height - 100, red_btn_pic, 'New Game', 40)
mp_back_button = Button(
    client_data.width - button_width - 50, client_data.height - 100, red_btn_pic, 'Back', 40)

mp_menu_btns_group = pygame.sprite.Group(
    test_game_button, new_game_button, mp_back_button)

game_lobby_buttons = [TextObj((50, 100 + (button_height + dist) * 0, button_width, button_height), 'Game 1', 40, background_color=(100, 100, 100)),
                      TextObj((50, 100 + (button_height + dist) * 1, button_width, button_height), 'Game 2', 40, background_color=(100, 100, 100)),
                      TextObj((50, 100 + (button_height + dist) * 2, button_width, button_height), 'Game 3', 40, background_color=(100, 100, 100)),
                      TextObj((50, 100 + (button_height + dist) * 3, button_width, button_height), 'Game 4', 40, background_color=(100, 100, 100)),
                      TextObj((50, 100 + (button_height + dist) * 4, button_width, button_height), 'Game 5', 40, background_color=(100, 100, 100))]


# Lobby objects
lobby_start_button = Button(
    client_data.width - button_width - 200, client_data.height - 50, red_btn_pic, 'Start', 40)
ready_button = Button(
    client_data.width - 200, client_data.height - 100, red_btn_pic, 'Not Ready', 40)
lobby_back_button = Button(
    client_data.width - button_width - 50, client_data.height - 50, red_btn_pic, 'Back', 40)
map_picture = Button(
    600, 100, map_pic)
map_name = Button(
    600, 600, red_btn_pic, 'map1', 40)

sp_menu_btns_group = pygame.sprite.Group(
    lobby_start_button, lobby_back_button, map_picture, map_name)
lobby_btns_group = pygame.sprite.Group(
    lobby_start_button, ready_button, lobby_back_button, map_picture, map_name)

icon_width = icon_height = 50
lobby_icon_buttons = [PictureObj((150, 100 + (icon_height + dist) * 0, icon_width, icon_height), question_mark),
                      PictureObj((150, 100 + (icon_height + dist) * 1, icon_width, icon_height), question_mark),
                      PictureObj((150, 100 + (icon_height + dist) * 2, icon_width, icon_height), question_mark),
                      PictureObj((150, 100 + (icon_height + dist) * 3, icon_width, icon_height), question_mark)]

name_objs = []
for btn in lobby_icon_buttons:
    name_objs.append(TextObj((btn.rect.x - 100, btn.rect.y, 50, 50), '', 24, background_color=(0,0,0)))

# Char selection menu objects

img_width = img_height = 100
char_sel_buttons = [PictureObj((200 + (img_width + dist) * 0, 200 + (img_height + dist) * 0, img_width, img_height), gnome_pics[0]),
                    PictureObj((200 + (img_width + dist) * 1, 200 + (img_height + dist) * 0, img_width, img_height), gnome_pics[1]),
                    PictureObj((200 + (img_width + dist) * 2, 200 + (img_height + dist) * 0, img_width, img_height), gnome_pics[2]),
                    PictureObj((200 + (img_width + dist) * 0, 200 + (img_height + dist) * 1, img_width, img_height), gnome_pics[3]),
                    PictureObj((200 + (img_width + dist) * 1, 200 + (img_height + dist) * 1, img_width, img_height), gnome_pics[4]),
                    PictureObj((200 + (img_width + dist) * 2, 200 + (img_height + dist) * 1, img_width, img_height), gnome_pics[5])]

ready_circles = [Circle(400, int(100 + icon_height / 2 + (icon_height + dist) * 0), 10, (255, 0, 0), 0),
                 Circle(400, int(100 + icon_height / 2 + (icon_height + dist) * 1), 10, (255, 0, 0), 0),
                 Circle(400, int(100 + icon_height / 2 + (icon_height + dist) * 2), 10, (255, 0, 0), 0),
                 Circle(400, int(100 + icon_height / 2 + (icon_height + dist) * 3), 10, (255, 0, 0), 0)]

# Map selection
img_width = 300
img_height = 192
map_sel_buttons = [PictureObj((50 + (img_width + 5) * 0, 200, img_width, img_height), map_pic),
                   PictureObj((50 + (img_width + 5) * 1, 200, img_width, img_height), map_pic),
                   PictureObj((50 + (img_width + 5) * 2, 200, img_width, img_height), map_pic)]
map_names = []
for i, btn in enumerate(map_sel_buttons):
    map_names.append(TextObj((btn.rect.x + btn.rect.width / 2, btn.rect.y + btn.rect.height + 20, 0, 0), f'Map {i+1}', 24, background_color=(0,0,0)))


size = 50
width = 100
height = 50
btn_width = 150
btn_height = 75

# General Display areas
timer_area = TextObj(((client_data.width - 150) / 2, 50, 150, 30), '', 30, background_color=(0, 0, 0))
chat_area = Chat(0, client_data.height - 225, 300, 100)
type_area = TextObj((0, client_data.height - 125, 300, 50), '', 20, background_color=(30, 30, 30))

# General Objects and buttons
next_wave_btn = Button(
    client_data.width - btn_width, 0, red_btn_pic, 'Next Wave', 40)

# Resource pictures
wood_res_pic_obj = Button(
    size * 0 + width * 0, 0, wood_res_pic)
stone_res_pic_obj = Button(
    size * 1 + width * 1, 0, stone_res_pic)
gear_res_pic_obj = Button(
    size * 2 + width * 2, 0, gear_res_pic)
squirrel_res_pic_obj = Button(
    size * 3 + width * 3, 0, squirrel_res_pic)
chicken_res_pic_obj = Button(
    size * 4 + width * 4, 0, chicken_res_pic)
chicken_leg_res_pic_obj = Button(
    size * 5 + width * 5, 0, chicken_leg_res_pic)
egg_res_pic_obj = Button(
    size * 6 + width * 6, 0, egg_res_pic)

craft_mode_btns_group = pygame.sprite.Group(
    next_wave_btn, wood_res_pic_obj, stone_res_pic_obj, gear_res_pic_obj, squirrel_res_pic_obj, chicken_res_pic_obj,
    chicken_leg_res_pic_obj, egg_res_pic_obj)

# Resouce numbers  - Ezt nem biztos hogy a jelenlegi Button classal kéne megoldani, hanem csak a szöveget odarakni.
# a hátteret, illetve a játék keretét pedig néhány sávból odarajzolni, ahelyett hogy itt egyesével odaraknám
resource_num_dict = {
    'Wood': TextObj((width * 0 + size * 1, 0, width, height), '0', 30, background_color=(139,69,19)),
    'Stone': TextObj((width * 1 + size * 2, 0, width, height), '0', 30, background_color=(139,69,19)),
    'Gear': TextObj((width * 2 + size * 3, 0, width, height), '0', 30, background_color=(139,69,19)),
    'Squirrel': TextObj((width * 3 + size * 4, 0, width, height), '0', 30, background_color=(139,69,19)),
    'Chicken': TextObj((width * 4 + size * 5, 0, width, height), '0', 30, background_color=(139,69,19)),
    'Chicken leg': TextObj((width * 5 + size * 6, 0, width, height), '0', 30, background_color=(139,69,19)),
    'Egg': TextObj((width * 6 + size * 7, 0, width, height), '0', 30, background_color=(139,69,19))}

# Building Cost:
new_craft_cost_dict = {
    'Wood': TextObj((width * 0 + size * 1 + 30, 0, width, height), '', 30, text_color=(255, 0, 0)),
    'Stone': TextObj((width * 1 + size * 2 + 30, 0, width, height), '', 30, text_color=(255, 0, 0)),
    'Gear': TextObj((width * 2 + size * 3 + 30, 0, width, height), '', 30, text_color=(255, 0, 0)),
    'Squirrel': TextObj((width * 3 + size * 4 + 30, 0, width, height), '', 30, text_color=(255, 0, 0)),
    'Chicken': TextObj((width * 4 + size * 5 + 30, 0, width, height), '', 30, text_color=(255, 0, 0)),
    'Chicken leg': TextObj((width * 5 + size * 6 + 30, 0, width, height), '', 30, text_color=(255, 0, 0)),
    'Egg': TextObj((width * 6 + size * 7 + 30, 0, width, height), '', 30, text_color=(255, 0, 0))}

# Energy:
energy = TextObj((width * 7 + size * 8, 0, width, height), '0', 30, background_color=(139,69,19))


# Non Battle Mode
game_menu_btn = Button(client_data.width - btn_width, client_data.height - btn_height,
                       red_btn_pic, 'Menu', 24)
game_menu_btn_group = pygame.sprite.Group(game_menu_btn)


# Base menu buttons
wood_res_pic_obj = Button(
    size * 0 + width * 0, 0, wood_res_pic)
stone_res_pic_obj = Button(
    size * 1 + width * 1, 0, stone_res_pic)
gear_res_pic_obj = Button(
    size * 2 + width * 2, 0, gear_res_pic)
squirrel_res_pic_obj = Button(
    size * 3 + width * 3, 0, squirrel_res_pic)
chicken_res_pic_obj = Button(
    size * 4 + width * 4, 0, chicken_res_pic)
chicken_leg_res_pic_obj = Button(
    size * 5 + width * 5, 0, chicken_leg_res_pic)
egg_res_pic_obj = Button(
    size * 6 + width * 6, 0, egg_res_pic)
energy_pic_obj = Button(
    size * 7 + width * 7, 0, energy_pic)

craft_mode_btns_group = pygame.sprite.Group(
    next_wave_btn, wood_res_pic_obj, stone_res_pic_obj, gear_res_pic_obj, squirrel_res_pic_obj, chicken_res_pic_obj,
    chicken_leg_res_pic_obj, egg_res_pic_obj, energy_pic_obj)


garden_traps_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, 'Q - Garden Traps', 24)
floor_traps_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, 'W - Floor Traps', 24)
wall_traps_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, 'E - Wall Traps', 24)
char_spec_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, 'R - Specials', 24)

tiles_btn = Button((btn_width + dist) * 4, client_data.height - btn_height, red_btn_pic, 'A. Garden Obj.', 24)
garden_obj_btn = Button((btn_width + dist) * 5, client_data.height - btn_height, red_btn_pic, 'S. Floor Obj.', 24)
floor_obj_btn = Button((btn_width + dist) * 6, client_data.height - btn_height, red_btn_pic, 'D. Wall Obj.', 24)
wall_obj_btn = Button((btn_width + dist) * 7, client_data.height - btn_height, red_btn_pic, 'F. Tiles', 24)

destroy_btn = Button((btn_width + dist) * 9, client_data.height - btn_height, red_btn_pic, 'X - Destroy', 24)

base_menu_btns_group = pygame.sprite.Group(
    garden_traps_btn, floor_traps_btn, wall_traps_btn, char_spec_btn,
    tiles_btn, garden_obj_btn, floor_obj_btn, wall_obj_btn,
    destroy_btn)


# Tiles buttons
grass_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Grass', 24)
floor_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Floor', 24)
wall_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Wall', 24)

tile_btns_group = pygame.sprite.Group(
    grass_btn, floor_btn, wall_btn)

# Garden object buttons
tree_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Tree', 24)
flower_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Flower', 24)
fence_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Fence', 24)
dog_house_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, '4. Dog House', 24)

garden_obj_btns_group = pygame.sprite.Group(
    tree_btn, flower_btn, fence_btn, dog_house_btn)

# floor_obj_btn
science_machine_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Science Machine', 24)
squirrel_wheel_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Squirrel Wheel', 24)
cabinet_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Cabinet', 24)
bed_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, '4. Bed', 24)
cupboard_btn = Button((btn_width + dist) * 4, client_data.height - btn_height, red_btn_pic, '5. Cupboard', 24)
table_btn = Button((btn_width + dist) * 5, client_data.height - btn_height, red_btn_pic, '6. Table', 24)
chest_btn = Button((btn_width + dist) * 6, client_data.height - btn_height, red_btn_pic, '7. Chest', 24)

floor_obj_btns_group = pygame.sprite.Group(
    science_machine_btn, squirrel_wheel_btn, cabinet_btn, bed_btn, cupboard_btn, table_btn, chest_btn)

# wall_obj_btn
window_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Window', 24)
door_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Door', 24)

wall_obj_btns_group = pygame.sprite.Group(
    window_btn, door_btn)

# garden_traps_btn
bear_trap_1_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Bear Trap', 24)
garden_trap_2_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Garden Trap 2', 24)
garden_trap_3_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Garden Trap 3', 24)
garden_trap_4_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, '4. Garden Trap 4', 24)

garden_trap_btns_group = pygame.sprite.Group(
    bear_trap_1_btn, garden_trap_2_btn, garden_trap_3_btn, garden_trap_4_btn)

# floor_traps_btn
floor_trap_1_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Spike Trap', 24)
floor_trap_2_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Autocannon', 24)
floor_trap_3_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Catapult', 24)
floor_trap_4_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, '4. Glue Gun', 24)
floor_trap_5_btn = Button((btn_width + dist) * 4, client_data.height - btn_height, red_btn_pic, '5. Machine Gunner', 24)
floor_trap_6_btn = Button((btn_width + dist) * 5, client_data.height - btn_height, red_btn_pic, '6. Decoy', 24)

floor_trap_btns_group = pygame.sprite.Group(
    floor_trap_1_btn, floor_trap_2_btn, floor_trap_3_btn, floor_trap_4_btn, floor_trap_5_btn, floor_trap_6_btn)

# wall_traps_btn
wall_trap_1_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Grinder', 24)
wall_trap_2_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Wall Blades', 24)
wall_trap_3_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Snow Blower', 24)
wall_trap_4_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, '4. Air Vent', 24)
wall_trap_5_btn = Button((btn_width + dist) * 4, client_data.height - btn_height, red_btn_pic, '5. Push Trap', 24)
wall_trap_6_btn = Button((btn_width + dist) * 5, client_data.height - btn_height, red_btn_pic, '6. Arrow Wall', 24)

wall_trap_btns_group = pygame.sprite.Group(
    wall_trap_1_btn, wall_trap_2_btn, wall_trap_3_btn, wall_trap_4_btn, wall_trap_5_btn,wall_trap_6_btn)

# Direction buttons
turn_1_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, 'Q. Turn 1', 24)
turn_2_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, 'E. Turn 2', 24)

directions_btns_group = pygame.sprite.Group(
    turn_1_btn, turn_2_btn)


# Character Spec skill buttons
spec_1_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, '1. Spec 1', 24)
spec_2_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, '2. Spec 2', 24)
spec_3_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, '3. Spec 3', 24)
spec_4_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, '4. Spec 4', 24)
# valahogy karakter specifikusan kell ezt kezelnem.
char_spec_btns_group = pygame.sprite.Group(
    spec_1_btn, spec_2_btn, spec_3_btn, spec_4_btn)


# Battle Mode
attack_btn = Button((btn_width + dist) * 0, client_data.height - btn_height, red_btn_pic, 'A - Attack', 24)
battle_skill_1_btn = Button((btn_width + dist) * 1, client_data.height - btn_height, red_btn_pic, 'Q - Skill 1', 24)
battle_skill_2_btn = Button((btn_width + dist) * 2, client_data.height - btn_height, red_btn_pic, 'W - Skill 2', 24)
battle_skill_3_btn = Button((btn_width + dist) * 3, client_data.height - btn_height, red_btn_pic, 'E - Skill 3', 24)
battle_skill_4_btn = Button((btn_width + dist) * 4, client_data.height - btn_height, red_btn_pic, 'R - Ultimate', 24)

battle_skill_btns_group = pygame.sprite.Group(
    attack_btn, battle_skill_1_btn, battle_skill_2_btn, battle_skill_3_btn, battle_skill_4_btn)