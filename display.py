import pygame
# from pygame import RESIZABLE
from client_data import client_data

pygame.init()
SCREEN = pygame.display.set_mode((200, 100), pygame.HWSURFACE | pygame.DOUBLEBUF)

# Menu background

background_pic = pygame.transform.scale(pygame.image.load("Pictures/background.png"),
                                        (client_data.width, client_data.height)).convert()

# Gnome pictures
captain_cook_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Captain Cook/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Captain Cook/2.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Captain Cook/3.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Captain Cook/4.png"), (50, 50)).convert()]
fatty_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Fatty/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Fatty/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Fatty/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Fatty/1.png"), (50, 50)).convert()]
flower_sniffer_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Flower Sniffer/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Flower Sniffer/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Flower Sniffer/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Flower Sniffer/1.png"), (50, 50)).convert()]
master_mindcrack_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Master Mindcrack/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Master Mindcrack/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Master Mindcrack/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Master Mindcrack/1.png"), (50, 50)).convert()]
hammer_head_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Hammer Head/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Hammer Head/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Hammer Head/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Hammer Head/1.png"), (50, 50)).convert()]
stinky_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Stinky/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Stinky/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Stinky/1.png"), (50, 50)).convert(),
    pygame.transform.scale(pygame.image.load("Pictures/Characters/Stinky/1.png"), (50, 50)).convert()]

for pic in master_mindcrack_pics:
    pic.set_colorkey((0, 0, 0))

gnome_pics = [pygame.transform.scale(pygame.image.load("Pictures/Characters/Captain Cook/1.png"), (100, 100)).convert(),
              pygame.transform.scale(pygame.image.load("Pictures/Characters/Fatty/1.png"), (100, 100)).convert(),
              pygame.transform.scale(pygame.image.load("Pictures/Characters/Flower Sniffer/1.png"), (100, 100)).convert(),
              pygame.transform.scale(pygame.image.load("Pictures/Characters/Master Mindcrack/1.png"), (100, 100)).convert(),
              pygame.transform.scale(pygame.image.load("Pictures/Characters/Hammer Head/1.png"), (100, 100)).convert(),
              pygame.transform.scale(pygame.image.load("Pictures/Characters/Stinky/1.png"), (100, 100)).convert()]
gnome_icons = [pygame.transform.scale(gnome_pic, (50, 50)) for gnome_pic in gnome_pics]

# Enemy images
goblin_pics = [
    pygame.image.load("Pictures/Enemies/goblin.png").convert()]

for pic in goblin_pics:
    pic.set_colorkey((255, 255, 255))

ogre_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Enemies/ogre.png").convert(), (50, 50))]

for pic in ogre_pics:
    pic.set_colorkey((255, 255, 255))

# Item images
turkey_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/Turkey.png"), (50, 50)).convert()
turkey_pic.set_colorkey((255, 255, 255))

# Effect images
lightning_pics = [
    pygame.image.load("Pictures/Effects/Lightning/0.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/1.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/2.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/3.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/4.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/5.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/6.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/7.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/8.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/9.png").convert(),
    pygame.image.load("Pictures/Effects/Lightning/10.png").convert()]
for pic in lightning_pics:
    pic.set_colorkey((0, 0, 0))

cannonball_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Effects/Cannonball/0.png"), (30, 30)).convert()
]
for pic in cannonball_pics:
    pic.set_colorkey((255, 255, 255))

# Buttons
red_btn_pic = pygame.image.load('Pictures/Menus/Buttons/red_v6.png').convert()
red_btn_pic.set_colorkey((255, 255, 255))

# General images
question_mark = pygame.transform.scale(pygame.image.load("Pictures/question_mark.png"), (50, 50)).convert()
red = pygame.transform.scale(pygame.image.load("Pictures/red.png"), (50, 50)).convert()
green = pygame.transform.scale(pygame.image.load("Pictures/green.png"), (50, 50)).convert()
black = pygame.transform.scale(pygame.image.load("Pictures/black.png"), (50, 50)).convert()
red.set_alpha(150)
green.set_alpha(150)
black.set_alpha(150)
# question_mark.set_colorkey((255,255,255))

map_pic = pygame.image.load("Pictures/map_pic.png").convert()

# Resources
wood_res_pic = pygame.image.load("Pictures/Menus/wood.png").convert()
stone_res_pic = pygame.image.load("Pictures/Menus/stone.png").convert()
gear_res_pic = pygame.image.load("Pictures/Menus/gear.png").convert()
squirrel_res_pic = pygame.image.load("Pictures/Menus/squirrel.png").convert()
chicken_res_pic = pygame.image.load("Pictures/Menus/chicken.png").convert()
chicken_leg_res_pic = pygame.image.load("Pictures/Menus/chicken_leg.png").convert()
egg_res_pic = pygame.image.load("Pictures/Menus/egg.png").convert()
energy_pic = pygame.transform.scale(pygame.image.load("Pictures/Menus/energy.png"), (50, 50)).convert()


# Tiles
wall_pic = pygame.transform.scale(pygame.image.load("Pictures/Tiles/wall_pic.png"), (50, 50)).convert()
floor_pic = pygame.transform.scale(pygame.image.load("Pictures/Tiles/floor_pic.png"), (50, 50)).convert()
grass_pic = pygame.transform.scale(pygame.image.load("Pictures/Tiles/grass_pic.png"), (50, 50)).convert()

opq_wall_pic = wall_pic.copy()
opq_floor_pic = floor_pic.copy()
opq_grass_pic = grass_pic.copy()
opq_tiles_pics = [opq_wall_pic, opq_floor_pic, opq_grass_pic]
for tile_pic in opq_tiles_pics:
    tile_pic.set_alpha(150)


# Objects
garden_obj_1_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/tree.png"), (50, 50)).convert()
garden_obj_2_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/flowers.png"), (50, 50)).convert()
garden_obj_3_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/fence.png"), (50, 50)).convert()
garden_obj_4_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/dog_house.png"), (50, 50)).convert()
garden_obj_5_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
garden_obj_6_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
garden_obj_7_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
floor_obj_1_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/science_machine.png"), (50, 50)).convert()
floor_obj_2_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/squirrel_wheel.png"), (50, 50)).convert()
floor_obj_3_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/cabinet.png"), (50, 50)).convert()
floor_obj_4_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/bed.png"), (50, 50)).convert()
floor_obj_5_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/cupboard.png"), (50, 50)).convert()
floor_obj_6_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/table.png"), (50, 50)).convert()
floor_obj_7_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/chest.png"), (50, 50)).convert()
wall_obj_1_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
wall_obj_2_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
wall_obj_3_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
wall_obj_4_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
wall_obj_5_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
wall_obj_6_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()
wall_obj_7_pic = pygame.transform.scale(pygame.image.load("Pictures/Objects/question_mark.png"), (50, 50)).convert()

# Traps / Weapons
garden_trap_1_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
garden_trap_2_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
garden_trap_3_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
garden_trap_4_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
garden_trap_5_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
garden_trap_6_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
garden_trap_7_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
floor_trap_1_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/spike_trap.png"), (50, 50)).convert()
floor_trap_2_pic = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("Pictures/Traps/autocannon.png"), (50, 50)).convert(), -180)
floor_trap_3_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/catapult.png"), (50, 50)).convert()
floor_trap_4_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/glue_gun.png"), (50, 50)).convert()
floor_trap_5_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/machine_gunner.png"), (50, 50)).convert()
floor_trap_6_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/decoy.png"), (50, 50)).convert()
floor_trap_7_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()
wall_trap_1_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/grinder.png"), (50, 50)).convert()
wall_trap_2_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/wall_blades.png"), (50, 50)).convert()
wall_trap_3_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/snow_blower.png"), (50, 50)).convert()
wall_trap_4_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/air_vent.png"), (50, 50)).convert()
wall_trap_5_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/push_trap.png"), (50, 50)).convert()
wall_trap_6_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/arrow_wall.png"), (50, 50)).convert()
wall_trap_7_pic = pygame.transform.scale(pygame.image.load("Pictures/Traps/question_mark.png"), (50, 50)).convert()

floor_trap_1_pic.set_colorkey((255,255,255))

# Character talent images
heart_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/heart.png"), (50, 50)).convert()
damage_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/axe.png"), (50, 50)).convert()
speed_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/wind.png"), (50, 50)).convert()
cost_red_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/hammer.png"), (50, 50)).convert()
upkeep_output_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/power.png"), (50, 50)).convert()
comfort_trap_dmg_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/explosion_sky.png"), (50, 50)).convert()
frame_green_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/frame_green.png"), (50, 50)).convert()
frame_grey_icon = pygame.transform.scale(pygame.image.load("Pictures/Talents/Talent Tree Icons/frame_grey.png"), (50, 50)).convert()

frame_green_icon.set_colorkey((0, 0, 0))
frame_grey_icon.set_colorkey((0, 0, 0))


# Character skill images
tesla_coil_pics = [pygame.transform.scale(pygame.image.load("Pictures/Traps/tesla_coil.png"), (50, 50)).convert()]
for pic in tesla_coil_pics:
    pic.set_colorkey((0, 0, 0))

overcharger_pic = pygame.transform.scale(pygame.image.load("Pictures/Upgrades/question_mark.png"), (50, 50)).convert()
overcharger_pic.set_colorkey((0, 0, 0))

pygame.display.quit()


def spectator(game_data, server_data):
    pygame.init()
    SCREEN = pygame.display.set_mode((1000, 800), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Gnomes! - Spectator Mode")
    clock = pygame.time.Clock()

    while True:
        # Buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Background
        SCREEN.fill((128, 128, 128))
        # továbbiakban csak azt kéne megjeleníteni, amit a játékos láthat, ami a képernyőre ráfér.

        # Cells
        for cell in game_data.cells_dict.values():
            cell.draw(SCREEN, client_data.base_scroll)

        # Players
        for player in game_data.players:
            server_data.chars[player.char_id].draw(SCREEN, server_data.base_scroll)

        pygame.display.update()
        clock.tick(server_data.framerate)
