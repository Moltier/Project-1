import random
from static_objects import *
from dicts import *


class Matrix:
    def __init__(self, matrix_dict, width, height, node_size):
        self.dict = matrix_dict
        self.width = width
        self.height = height
        self.node_size = node_size
        self.open_list = []
        self.closed_dict = {}

    def update(self, coord):
        self.dict[coord]['Blocker'] = self.dict[coord]['Tile'].blocker

        if not self.dict[coord]['Blocker']:
            if self.dict[coord]['Object']:
                if self.dict[coord]['Object'].blocker:
                    self.dict[coord]['Blocker'] = True
            elif self.dict[coord]['Trap']:
                if self.dict[coord]['Trap'].blocker:
                    self.dict[coord]['Blocker'] = True


class GameObject:
    def __init__(self, map='map1'):
        self.map = map
        self.cell_size = 50
        self.node_size = 50
        self.grid_dict = {}  # for Floodfill
        self.matrix = None
        self.waypoints_dict = {}  # ezt az adatot lehet nem is kell tárolni majd
        self.waypoint_paths_dict = {}
        self.cost_div = 0

        # Entity groups
        self.characters_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.my_char_group = pygame.sprite.GroupSingle()
        self.chars_dict = {}
        self.enemy_wave = {}

        # Object groups
        self.tile_group = pygame.sprite.Group()
        self.object_group = pygame.sprite.Group()
        self.trap_group = pygame.sprite.Group()
        self.blocker_group = pygame.sprite.Group()
        self.transparent_group = pygame.sprite.GroupSingle()
        self.effect_group = pygame.sprite.Group()  # sprites with function, might be outdated
        self.projectiles_group = pygame.sprite.Group()
        self.infobox = InfoBox(self.cell_size)
        self.spawn_positions = [(600, 400)]
        self.blocker_lines = set()

        # Energy
        self.energy_multi = 1

    def draw_path(self, SCREEN, base_scroll, char):
        path = [x[0] for x in char.path]
        path.insert(0, char.coord)
        i = 0
        thichness = 3
        while i+1 < len(path):
            first_coord = path[i][0] - base_scroll[0], path[i][1] - base_scroll[1]
            second_coord = path[i+1][0] - base_scroll[0], path[i+1][1] - base_scroll[1]
            pygame.draw.line(SCREEN, (255, 0, 0), first_coord, second_coord, thichness)
            i += 1
            thichness += 2

    def generate_waypoints(self):  # ezt majd inkább az algorithm mappába kéne pakolni mint különálló algorithmus
        start_time = time.time()

        blockers_set = {tile_blocker.rect.topleft for tile_blocker in self.blocker_group}
        self.waypoints_dict = {}
        nieghbor_waypoints_dict = {}
        waypoint_paths_dict = {}

        for coord in blockers_set:
            rect = pygame.Rect(coord, (self.cell_size, self.cell_size))

            neighbors = {'E': False, 'S': False, 'W': False, 'N': False,
                         'SE': False, 'SW': False, 'NE': False, 'NW': False}
            east_coord = (coord[0] + self.cell_size, coord[1])
            south_coord = (coord[0], coord[1] + self.cell_size)
            west_coord = (coord[0] - self.cell_size, coord[1])
            north_coord = (coord[0], coord[1] - self.cell_size)

            southeast_coord = (coord[0] + self.cell_size, coord[1] + self.cell_size)
            southwest_coord = (coord[0] - self.cell_size, coord[1] + self.cell_size)
            northeast_coord = (coord[0] + self.cell_size, coord[1] - self.cell_size)
            northwest_coord = (coord[0] - self.cell_size, coord[1] - self.cell_size)

            if east_coord in blockers_set:
                neighbors['E'] = True
            if south_coord in blockers_set:
                neighbors['S'] = True
            if west_coord in blockers_set:
                neighbors['W'] = True
            if north_coord in blockers_set:
                neighbors['N'] = True

            if southeast_coord in blockers_set:
                neighbors['SE'] = True
            if southwest_coord in blockers_set:
                neighbors['SW'] = True
            if northeast_coord in blockers_set:
                neighbors['NE'] = True
            if northwest_coord in blockers_set:
                neighbors['NW'] = True

            if not neighbors['S'] and not neighbors['E'] and not neighbors['SE']:
                self.waypoints_dict[rect.bottomright] = 'BR'
            if not neighbors['S'] and not neighbors['W'] and not neighbors['SW']:
                if rect.left - 1 >= 0:
                    self.waypoints_dict[(rect.left - 1, rect.bottom)] = 'BL'
            if not neighbors['N'] and not neighbors['W'] and not neighbors['NW']:
                if rect.left - 1 >= 0 and rect.top - 1 >= 0:
                    self.waypoints_dict[(rect.left - 1, rect.top - 1)] = 'TL'
            if not neighbors['N'] and not neighbors['E'] and not neighbors['NE']:
                if rect.top -1 >= 0:
                    self.waypoints_dict[(rect.right, rect.top - 1)] = 'TR'

        for first_waypoint in self.waypoints_dict.keys():
            for second_waypoint in self.waypoints_dict.keys():
                if first_waypoint == second_waypoint:
                    continue
                if (first_waypoint, second_waypoint) in waypoint_paths_dict:
                    continue

                waypoint_paths_dict[(first_waypoint, second_waypoint)] = ()
                waypoint_paths_dict[(second_waypoint, first_waypoint)] = ()

                if first_waypoint not in nieghbor_waypoints_dict.keys():
                    nieghbor_waypoints_dict[first_waypoint] = []
                elif second_waypoint in nieghbor_waypoints_dict[first_waypoint]:
                    continue
                if second_waypoint not in nieghbor_waypoints_dict.keys():
                    nieghbor_waypoints_dict[second_waypoint] = []

                if not intersect(first_waypoint, second_waypoint, self.blocker_lines):
                    distance = abs(complex(*first_waypoint) - complex(*second_waypoint))
                    nieghbor_waypoints_dict[first_waypoint].append((distance, second_waypoint))
                    nieghbor_waypoints_dict[second_waypoint].append((distance, first_waypoint))

        for endpoints in waypoint_paths_dict.keys():
            start_waypoint, target_waypoint = endpoints
            unfinished_paths_set = {(0, ((start_waypoint),))}
            used_waypoints_set = {start_waypoint}
            shortest_path = ()

            while unfinished_paths_set:
                new_paths = set()
                old_paths = set()
                neighbors = set()
                for path_data in unfinished_paths_set:
                    path_distance, current_path = path_data
                    waypoint = current_path[-1]
                    old_paths.add(path_data)

                    for neighbor_data in nieghbor_waypoints_dict[waypoint]:
                        neighbor_distance, neighbor = neighbor_data
                        if neighbor in used_waypoints_set:
                            continue

                        new_path_distance = path_distance + neighbor_distance
                        new_path = list(current_path)
                        new_path.append(neighbor)
                        new_path = tuple(new_path)

                        if neighbor == target_waypoint:
                            if shortest_path:
                                if new_path_distance < shortest_path[0]:
                                    shortest_path = (new_path_distance, new_path)
                            else:
                                shortest_path = (new_path_distance, new_path)
                        else:
                            if shortest_path:
                                if new_path_distance < shortest_path[0]:
                                    new_paths.add((new_path_distance, new_path))
                            else:
                                new_paths.add((new_path_distance, new_path))

                        neighbors.add(neighbor)

                for old_path in old_paths:
                    unfinished_paths_set.remove(old_path)
                for new_path in new_paths:
                    unfinished_paths_set.add(new_path)
                for neighbor in neighbors:
                    used_waypoints_set.add(neighbor)

            waypoint_paths_dict[endpoints] = shortest_path

        for endpoints, path_data in waypoint_paths_dict.items():
            dist, path = path_data
            path = [(coord, self.waypoints_dict[coord]) for coord in path]
            waypoint_paths_dict[endpoints] = (dist, tuple(path))

        self.waypoint_paths_dict = waypoint_paths_dict.copy()
        cp(7134, 'Final runtime:', time.time() - start_time)

    def update_modifiers(self, game_data):
        """ Calculates all the static modifiers, but doesnt apply them. """

        # Character talentss:
        # Karakterek talent módosítóinak számítása.

        # Traps, Objects, and their Upgrades
        for trap in self.trap_group:
            for upg in trap.upgrades:
                # multiplier frissítés az upgrade-ket a created_by karakter talentjei alapján
                # trap.talent_dmg_multi = ...
                # trap.talent_range_multi = ...
                # trap.talent_xp_multi = ...
                trap.upg_dmg_multi = upg.damage_multi
                trap.upg_range_multi = upg.range_multi
                trap.upg_xp_multi = upg.xp_multi
                trap.upg_loot_multi = upg.loot_multi
            # multiplier frissítés a csapdákat a created_by karakter talentjei alapján
            pass

        for obj in self.object_group:
            for upg in obj.upgrades:
                # multiplier frissítés az upgrade-ket a created_by karakter talentjei alapján
                # obj.talent_output_multi = ...
                obj.upg_output_multi = upg.output_multi
            pass
            # itt frissíteném az objecteket a created_by karakter talentjei alapján

        # Energy:
        global_energy_output = 0
        global_energy_upkeep = 0
        game_data.energy_percent = 100

        for obj in self.object_group:
            global_energy_output += obj.output
            global_energy_upkeep += obj.upkeep
        for trap in self.trap_group:
            global_energy_upkeep += trap.upkeep

        if global_energy_output < global_energy_upkeep:
            game_data.energy_percent = int(global_energy_output / global_energy_upkeep * 100)
        self.energy_multi = game_data.energy_percent / 100

        # Base stat, actual stat előnye, hogy ennek a func-nak a végén ki lehetne számolni a legtöbb számítást.
        # Char skill buffs = temporary, recalculated every time its used, as long as it last

    def update_spawn_timers(self, dt):
        wave_num = 1
        while dt > 0 and wave_num <= len(self.enemy_wave):
            timer = 1
            if self.enemy_wave[wave_num][timer] > 0:
                if self.enemy_wave[wave_num][timer] > dt:
                    self.enemy_wave[wave_num][timer] -= dt
                    break
                else:
                    dt -= self.enemy_wave[wave_num][timer]
                    self.enemy_wave[wave_num][timer] = 0
            wave_num += 1

    def generate_enemy_teams(self, wave, spawn_time_mlt):
        self.enemy_wave = {}  # ez a sor lehet nem is fog kelleni
        for i, enemy_team in enumerate(wave):
            self.enemy_wave[i+1] = [enemy_team, 0]

        for i, enemy_team_data in enumerate(self.enemy_wave.values()):
            enemy_team = enemy_team_data[0]
            if i + 1 < len(self.enemy_wave):
                for enemy in enemy_team:
                    self.enemy_wave[i + 2][1] += enemy.time_val * spawn_time_mlt

    def spawn_enemies(self, game_data):
        if not self.enemy_wave:
            return
        elif self.enemy_wave[1][1] > 0:
            return

        spawn_positions = self.spawn_positions.copy()
        max_idx = len(spawn_positions) - 1

        for i, spawn_point in enumerate(reversed(self.spawn_positions)):
            for enemy in self.enemies_group:
                if enemy.rect.colliderect((spawn_point), (100, 100)):
                    index = max_idx - i
                    spawn_positions.pop(index)
                    break

        for wave_num, team_data in self.enemy_wave.items():
            team, timer = team_data
            if len(spawn_positions) == 0 or timer > 0:
                break
            else:
                i = len(team) - 1
                while i >= 0:
                    spawn_point = random.choice(spawn_positions)
                    spawn_positions.remove(spawn_point)

                    game_data.enemy_count += 1
                    enemy = team[i]
                    new_enemy = enemy.__copy__()  # ebben még nevet kéne generálni,
                    new_enemy.rect.topleft = spawn_point
                    new_enemy.coord = list(new_enemy.rect.center)
                    new_enemy.name = game_data.enemy_count  # ez csak ideiglenes

                    self.enemies_group.add(new_enemy)
                    self.enemy_wave[wave_num][0].pop(i)

                    if len(spawn_positions) == 0:
                        break
                    i -= 1

    def next_wave(self, game_data):
        next_wave_btn.click_sound.play()

        if client_data.sp_game:
            game_data.wave_num += 1
            num_of_chars = len(self.characters_group)

            for obj in self.object_group:
                if obj.item_cap > 1:  # ami karakter számtól függő mennyiségű
                    game_data.fatigue_multi = game_data.base_fatigue_multi + obj.fatigue / num_of_chars / 100
                    game_data.comfort_multi = game_data.base_comfort_multi + obj.comfort / num_of_chars / 100
                    game_data.xp_multi = game_data.base_xp_multi + (obj.xp_multi - 1) / num_of_chars
                else:
                    pass

            game_data.battle_mode = True
        else:
            # ide kéne valami ready rendszer
            send_object(('Next Wave', ''), client_data.socket)

    def new_obj(self, code):
        self.transparent_group.add(create_object(code, transp=True))
        return code

    def create_characters(self):
        self.chars_dict = {
            0: Character(
                0, captain_cook_pics, 'Captain Cook', 'Bard', 'Placeholder description.', 300, 125, 200, 200,
                ['Skill 1', 'Skill 2', 'Skill 3', 'Skill 4'],
                battle_skills=[captain_cook_basic_attack, tazer_attack, energize, maniacal_laugh, maniacal_laugh],
                talent_tree=common_talent_tree,
                wood=100, stone=100, gear=10, squirrel=10, chicken=10, egg=10, chicken_leg=10),
            1: Character(
                1, fatty_pics, 'Fatty', 'Tank', 'Placeholder description.', 300, 200, 700, 600,
                ['Skill 1', 'Skill 2', 'Skill 3', 'Skill 4'],
                battle_skills=[fatty_basic_attack, tazer_attack, energize, maniacal_laugh, maniacal_laugh],
                talent_tree=common_talent_tree,
                wood=100, stone=100, gear=10, squirrel=10, chicken=10, egg=10, chicken_leg=10),
            2: Character(
                2, flower_sniffer_pics, 'Flower Sniffer', 'Druid', 'Placeholder description.', 300, 125, 800, 600,
                ['Skill 1', 'Skill 2', 'Skill 3', 'Skill 4'],
                battle_skills=[flower_sniffer_basic_attack, tazer_attack, energize, maniacal_laugh, maniacal_laugh],
                talent_tree=common_talent_tree,
                wood=100, stone=100, gear=10, squirrel=10, chicken=10, egg=10, chicken_leg=10),
            3: Character(
                3, master_mindcrack_pics, 'Master Mindcrack', 'Mage', 'Placeholder description.', 300, 75, 900, 600,
                ['O-43', 'O-44', 'O-45', 'O-46'],
                battle_skills=[master_mindcrack_basic_attack, tazer_attack, energize, maniacal_laugh, maniacal_laugh],
                talent_tree=common_talent_tree,
                wood=100, stone=100, gear=10, squirrel=10, chicken=10, egg=10, chicken_leg=10),
            4: Character(
                4, hammer_head_pics, 'Hammer Head', 'Fighter', 'Placeholder description.', 300, 150, 1000, 600,
                ['Skill 1', 'Skill 2', 'Skill 3', 'Skill 4'],
                battle_skills=[hammer_head_basic_attack, tazer_attack, energize, maniacal_laugh, maniacal_laugh],
                talent_tree=common_talent_tree,
                wood=100, stone=100, gear=10, squirrel=10, chicken=10, egg=10, chicken_leg=10),
            5: Character(
                5, stinky_pics, 'Stinky', 'Rogue', 'Placeholder description.', 300, 75, 1100, 600,
                ['Skill 1', 'Skill 2', 'Skill 3', 'Skill 4'],
                battle_skills=[stinky_basic_attack, tazer_attack, energize, maniacal_laugh, maniacal_laugh],
                talent_tree=common_talent_tree,
                wood=100, stone=100, gear=10, squirrel=10, chicken=10, egg=10, chicken_leg=10)}

    def load_map(self):
        with open(f'maps/{str(self.map)}/{str(self.map)}', 'r', encoding='utf-8') as map_file:
            for y, line in enumerate(map_file):
                for x, code in enumerate(line):
                    coord = (x * self.cell_size, y * self.cell_size)
                    if code == '0':
                        self.tile_group.add(Object('Any', 'Tile', 'Grass', [grass_pic], coord, 0, False, transp=False))
                    elif code == '1':
                        self.tile_group.add(Object('Any', 'Tile', 'Floor', [floor_pic], coord, 0, False, wood=2, transp=False))
                    elif code == '2':
                        obj = Object('Any', 'Tile', 'Wall', [wall_pic], coord, 0, True, stone=10, transp=False)
                        self.tile_group.add(obj)
                        self.blocker_group.add(obj)
                    else:
                        continue

    def create_blocker_lines(self):
        for tile_blocker in self.blocker_group:
            for (p1, p2) in (
                    (Point(tile_blocker.rect.topleft), Point(tile_blocker.rect.topright)),
                    (Point(tile_blocker.rect.topright), Point(tile_blocker.rect.bottomright)),
                    (Point(tile_blocker.rect.bottomright), Point(tile_blocker.rect.bottomleft)),
                    (Point(tile_blocker.rect.bottomleft), Point(tile_blocker.rect.topleft))):
                self.blocker_lines.add((p1, p2))

    def create_matrix(self, matrix_width, matrix_height):
        """ Basic matrix for heat/cost maps, or A*, Theta*, LazyTheta* algorithms. """
        start_time = time.time()
        matrix_dict = {}

        for x in range(0, matrix_width, self.cell_size):
            for y in range(0, matrix_height, self.cell_size):
                matrix_dict[(x, y)] = {'Tile': None, 'Object': None, 'Trap': None, 'Blocker': False}

        for tile in self.tile_group:
            matrix_dict[tile.rect.topleft]['Tile'] = tile
        for obj in self.object_group:
            matrix_dict[obj.rect.topleft]['Object'] = obj
        for trap in self.trap_group:
            matrix_dict[trap.rect.topleft]['Trap'] = trap
        for blocker in self.blocker_group:
            matrix_dict[blocker.rect.topleft]['Blocker'] = True

        self.matrix = Matrix(matrix_dict, matrix_width, matrix_height, self.node_size)

        print('Matrix gen time: ', time.time() - start_time)
        # Az ellenörző func-nak lehet radius>0 esetén a környéket is néznie kéne, és a radiust hozzáadni a határhoz.
        # Elég sztem csak azt megnéznie, ami az alap coord (374, 123), és += radius minden irányban. Sarkokat is növelve.
        # Ha bármelyik nem egyezik az alap cellával, akkor az a cella is számít.
        # így elég lenne csak 1 matrixot generálni.


class Game:
    def __init__(self):
        self.connections = []
        self.id = -1
        self.player_count = 1
        self.active_game_ids = []

        self.players = []
        self.chosen_char_ids = []
        self.isReady = [False, False, False, False]
        self.isRunning = False
        self.test_mode = False  # ez késöbb lehetne tutorial
        self.battle_mode = False
        self.alternative_mode = 0
        self.talent_tree_on = False

        self.start_time = None
        self.dt = 0
        self.time_to_act = 0
        self.current_time = time.time()
        self.last_time = self.current_time
        self.game_time = None
        self.update_time = None

        self.crafting_cell_coords = []
        self.completed_crafts = []

        self.msg_num = 0

        self.wave_num = 0
        self.enemy_count = 0

        # Cursor
        self.detect_range = 100
        self.cursor = Cursor(self.detect_range)

        # Team Stats
        self.comfort = 50
        self.energy_percent = 0
        self.xp = 0
        self.lvl = 1
        self.lvl_dict = {
            1: 0,
            2: 100,
            3: 200,
            4: 350,
            5: 550,
            6: 900,
            7: 1450,
            8: 2350,
            9: 3800,
            10: 6150,
            11: 9950,
            12: 16100,
            13: 26050,
            14: 42150,
            15: 68200,
            16: 110350,
            17: 178550,
            18: 288900,
            19: 467450,
            20: 756350,
            21: math.inf}

        # Base Team Multipliers
        self.base_fatigue_multi = 0.8
        self.base_comfort_multi = 0.5
        self.base_dmg_multi = 1
        self.base_hp_multi = 1
        self.base_cd_red_multi = 1
        self.base_xp_multi = 1
        self.base_loot_multi = 1

        # Actual Team Multipliers
        self.fatigue_multi = self.base_fatigue_multi
        self.comfort_multi = self.base_comfort_multi
        self.dmg_multi = self.base_dmg_multi
        self.hp_multi = self.base_hp_multi
        self.cd_red_multi = self.base_cd_red_multi
        self.xp_multi = self.base_xp_multi
        self.loot_multi = self.base_loot_multi

        # Team Resources - ha van láda, ide tudnak pakolni (loot_packs pedig automatikusan szétosztódik)
        self.loot_packs = []

        self.resources = {
            'Wood': 0,
            'Stone': 0,
            'Gear': 0,
            'Squirrel': 0,
            'Chicken': 0,
            'Egg': 0,
            'Chicken leg': 0}

    def handle_loot(self, characters_group):
        wood = stone = gear = squirrel = egg = chicken = chicken_leg = 0

        for loot_pack in self.loot_packs:
            for loot, n in loot_pack.items():
                if loot == 'wood':
                    wood += n
                elif loot == 'stone':
                    stone += n
                elif loot == 'gear':
                    gear += n
                elif loot == 'squirrel':
                    squirrel += n
                elif loot == 'chicken':
                    chicken += n
                elif loot == 'egg':
                    egg += n
                elif loot == 'chicken_leg':
                    chicken_leg += n

        resources = [wood, stone, gear, squirrel, egg, chicken, chicken_leg]
        lucky_guy_idx = random.randint(0, len(characters_group))
        idx = 0

        for char in characters_group:
            for i, res in enumerate(resources):
                if i == 0:
                    char.resources['Wood'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Wood'] += res % self.player_count
                elif i == 1:
                    char.resources['Stone'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Stone'] += res % self.player_count
                elif i == 2:
                    char.resources['Gear'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Gear'] += res % self.player_count
                elif i == 3:
                    char.resources['Squirrel'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Squirrel'] += res % self.player_count
                elif i == 4:
                    char.resources['Chicken'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Chicken'] += res % self.player_count
                elif i == 5:
                    char.resources['Egg'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Egg'] += res % self.player_count
                elif i == 6:
                    char.resources['Chicken leg'] += res // self.player_count
                    if idx == lucky_guy_idx:
                        char.resources['Chicken leg'] += res % self.player_count
            idx += 1

    def remove_player(self, id):
        self.isReady[id] = False
        self.players[id] = Player(id)
        self.player_count -= 1


class Object(pygame.sprite.Sprite):
    def __init__(self, craftable_to, type, name, obj_imgs, coord, radius, blocker, transp=False, degree=0,
                 upkeep=0, output=0, fatigue=0, comfort=0,
                 wood=0, stone=0, gear=0, squirrel=0, chicken=0, egg=0, chicken_leg=0,
                 **kwargs):
        super().__init__()
        self.created_by = None
        self.craftable_to = craftable_to
        self.type = type
        self.name = name
        self.blocker = blocker

        # Base Object Images
        self.degree = degree
        self.obj_img_timer = time.time()
        self.obj_fps = 1
        self.image_idx = 0
        self.obj_imgs = obj_imgs
        self.image_count = len(self.obj_imgs) - 1
        self.image = pygame.transform.rotate(self.obj_imgs[0].copy(), -self.degree)
        self.transp = transp
        if self.transp:
            # cp(723, '!!!minden egyes alkalommal újrakreálja a komplett object listát, mielött választana belőle.')
            self.image.set_alpha(150)
        self.rect = self.image.get_rect(topleft=coord)
        self.radius = radius
        if radius == 0:
            self.rect_radius = int(math.sqrt(self.rect.width ** 2 + self.rect.height ** 2) / 2)

        # Cost
        self.cost = {
            'Wood': wood,
            'Stone': stone,
            'Gear': gear,
            'Squirrel': squirrel,
            'Chicken': chicken,
            'Egg': egg,
            'Chicken leg': chicken_leg}

        # Modifiers
        self.base_upkeep = upkeep
        self.upkeep = upkeep
        self.base_output = output
        self.output = output
        self.base_fatigue = fatigue
        self.fatigue = fatigue
        self.base_comfort = comfort
        self.comfort = comfort

        # Upgrades
        self.item_cap = 1
        self.upg_cap = 2
        self.upgrades = []
        self.icon_size = 8
        self.upg_icons = []
        for n in range(1, self.upg_cap + 1):
            self.upg_icons.append([
                (200, 200, 200),
                pygame.Rect((self.rect.x + (self.rect.width / (self.upg_cap + 1)) * n - self.icon_size / 2,
                             self.rect.bottom - self.rect.height / 5, self.icon_size, self.icon_size))])

        # Multipliers - will have more options...
        self.upg_output_multi = 1

        self.talent_output_multi = 1

        # temporary data
        self.text = str(get_cell_coord(self.rect.topleft, 50))
        self.font = pygame.font.SysFont('comicsans', 20)
        self.rendered_text = self.font.render(self.text, 1, (255, 255, 255))

        self.__dict__.update(kwargs)

    def __copy__(self):
        return Object(
            self.craftable_to, self.type, self.name, self.obj_imgs, self.rect.topleft, self.radius, self.blocker,
            degree=self.degree, cost=self.cost,
            upkeep=self.upkeep, base_output=self.base_output, output=self.output,
            base_fatigue=self.base_fatigue, fatigue=self.fatigue, base_comfort=self.base_comfort, comfort=self.comfort,
            item_cap=self.item_cap, upg_cap=self.upg_cap)

    def image_update(self, current_time):
        if self.obj_img_timer + self.obj_fps < current_time:
            self.image_idx += 1
            if self.image_idx > self.image_count:
                self.image_idx = 0
            self.image = pygame.transform.rotate(self.obj_imgs[self.image_idx].copy(), -self.degree)
            self.obj_img_timer = current_time

    def rotate(self, degree):
        self.image = pygame.transform.rotate(self.image, -degree)
        self.degree += degree
        if self.degree > 270:
            self.degree = 0
        elif self.degree < 0:
            self.degree = 270

    def draw(self, SCREEN, base_scroll):
        if base_scroll[0] - self.rect.width < self.rect.x < base_scroll[0] + client_data.width \
                and base_scroll[1] - self.rect.height < self.rect.y < base_scroll[1] + client_data.height:
            SCREEN.blit(self.image, (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1]))

            if self.transp:
                pygame.draw.rect(SCREEN, (255, 0, 0),
                    (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1], self.rect.w, self.rect.h), 3)

    def draw_cell_indexes(self, SCREEN, base_scroll):  # ideiglenes, amíg kell a cella index megjelenítése
        if base_scroll[0] - self.rect.width < self.rect.x < base_scroll[0] + client_data.width \
                and base_scroll[1] - self.rect.height < self.rect.y < base_scroll[1] + client_data.height:
            SCREEN.blit(self.rendered_text, (self.rect.centerx - round(self.rendered_text.get_width() / 2) - base_scroll[0],
                                             self.rect.centery - round(self.rendered_text.get_height() / 2) - base_scroll[1]))

    def draw_upgrades(self, SCREEN, base_scroll):
        for img in self.upg_icons:
            color, rect = img
            pygame.draw.rect(SCREEN, color, (rect.x - base_scroll[0], rect.y - base_scroll[1], rect.width, rect.height))
            pygame.draw.rect(SCREEN, (0, 0, 0), (rect.x - base_scroll[0], rect.y - base_scroll[1], rect.width, rect.height), 1)

    def update_upgrades(self):
        for i, upgrade in enumerate(self.upgrades):
            self.upg_icons[i][0] = upgrade.icon_color


class Trap(pygame.sprite.Sprite):
    def __init__(self, craftable_to, type, name, obj_imgs, coord, radius, blocker,
                 transp=False, degree=0, sp=10, aggro=0, delay=0,
                 eff_imgs=[], upkeep=0, effect=None, projectile=None,
                 wood=0, stone=0, gear=0, squirrel=0, chicken=0, chicken_leg=0, egg=0,
                 **kwargs):
        super().__init__()
        self.created_by = None
        self.craftable_to = craftable_to
        self.type = type
        self.name = name
        self.blocker = blocker

        # Base Object Images
        self.degree = degree
        self.obj_img_timer = time.time()
        self.obj_fps = 1
        self.image_idx = 0
        self.obj_imgs = obj_imgs
        self.image_count = len(self.obj_imgs) - 1
        self.image = pygame.transform.rotate(self.obj_imgs[0].copy(), -self.degree)
        self.transp = transp
        if self.transp:
            # cp(723, 'Sztem minden egyes alkalommal újrakreálja a komplett object listát, mielött választana belőle.')
            self.image.set_alpha(150)
        self.rect = self.image.get_rect(topleft=coord)
        self.radius = radius
        if radius == 0:
            self.rect_radius = int(math.sqrt(self.rect.width ** 2 + self.rect.height ** 2) / 2)

        # Effect Images
        self.eff_img_timer = time.time()
        self.eff_fps = 0.02
        self.eff_imgs = eff_imgs
        self.eff_img_count = len(self.eff_imgs) - 1
        self.eff_dict = {}

        # Cost
        self.cost = {
            'Wood': wood,
            'Stone': stone,
            'Gear': gear,
            'Squirrel': squirrel,
            'Chicken': chicken,
            'Egg': egg,
            'Chicken leg': chicken_leg}

        # Stats
        self.sp = sp  # structure point
        self.aggro = aggro
        self.delay = delay
        self.effect = effect
        self.projectile = projectile
        self.energy_lvl = 100  # amount of energy recharged

        if self.effect:
            self.effect.degree = self.degree
            if self.effect.type == 'Trap Effect':
                # self.detect_rect = self.rect
                if self.effect.detect_range:
                    self.detect_rect = generate_detect_rect(self.rect, self.degree, self.effect.detect_range)

        elif self.projectile:
            self.projectile.degree = self.degree
            if self.projectile.target_type == 'Trap Area':
                # self.detect_rect = self.rect
                if self.projectile.detect_range:
                    self.detect_rect = generate_detect_rect(self.rect, self.degree, self.projectile.detect_range)

                    if self.projectile.target_type == 'Trap Area':
                        self.projectile.detect_rect = self.detect_rect

            else:
                self.projectile.rect.center = self.coord = self.rect.center

        self.upkeep = upkeep

        # Upgrades
        self.item_cap = 1
        self.upg_cap = 2
        self.upgrades = []
        self.icon_size = 8
        self.upg_icons = []
        for n in range(1, self.upg_cap + 1):
            self.upg_icons.append([
                (200, 200, 200),
                pygame.Rect((self.rect.x + (self.rect.width / (self.upg_cap + 1)) * n - self.icon_size / 2,
                             self.rect.bottom - self.rect.height / 5, self.icon_size, self.icon_size))])

        # Modifiers
        self.upg_upkeep_multi = 1
        self.upg_dmg_multi = 1
        self.upg_range_multi = 1
        self.upg_xp_multi = 1
        self.upg_loot_multi = 1

        self.talent_upkeep_multi = 1
        self.talent_dmg_multi = 1
        self.talent_range_multi = 1
        self.talent_xp_multi = 1
        self.talent_loot_multi = 1

        # Buffs
        self.dmg_buffs = []
        self.slow_buffs = []
        self.slow_dur_buffs = []
        self.push_buffs = []
        self.stun_buffs = []

        # Data
        self.shot_counter = 0
        self.dmg_counter = 0

        self.__dict__.update(kwargs)

    def __copy__(self):
        return Trap(
            self.craftable_to, self.type, self.name, self.obj_imgs, self.rect.topleft, self.radius, self.blocker,
            degree=self.degree, aggro=self.aggro, eff_imgs=self.eff_imgs, eff_img_count=self.eff_img_count,
            eff_dict=self.eff_dict,
            cost=self.cost,
            effect=self.effect, projectile=self.projectile, upkeep=self.upkeep,
            item_cap=self.item_cap, upg_cap=self.upg_cap)

    def update(self, game_objects, dt):
        if self.sp < 1:
            self.kill()
            return

        self.update_buffs(dt)

        self.energy_lvl += game_objects.energy_multi * dt
        if self.energy_lvl >= self.upkeep:
            if self.effect:
                if self.effect.type == 'Trap Effect':
                    target_enemies = detect_targets(game_objects.enemies_group, detect_rect=self.detect_rect)
                    if target_enemies:
                        self.shot_counter += 1
                        self.energy_lvl = 0
                        for enemy in target_enemies:
                            self.dmg_counter += enemy.hit(self.degree, self.effect)

            else:  # self.projectile
                target_enemies = detect_targets(game_objects.enemies_group, detect_rect=self.detect_rect)
                if target_enemies:
                    self.shot_counter += 1
                    self.energy_lvl = 0
                    new_projectile = self.projectile.__copy__()
                    new_projectile.parent = self
                    new_projectile.rect = self.rect.copy()
                    new_projectile.coord = new_projectile.rect.center
                    new_projectile.direction = get_direction(degree=self.degree)

                    new_projectile.effect.dmg = round(new_projectile.effect.dmg * self.upg_dmg_multi
                                                      * self.talent_dmg_multi, 2)

                    try:
                        new_projectile.explosion_eff.dmg = round(new_projectile.effect.dmg * self.upg_dmg_multi
                                                          * self.talent_dmg_multi, 2)
                    except AttributeError:
                        pass
                    new_projectile.range *= self.upg_range_multi * self.talent_range_multi
                    new_projectile.detect_range *= self.upg_range_multi * self.talent_range_multi
                    game_objects.projectiles_group.add(new_projectile)

    def update_buffs(self, dt):
        """ Buffok frissítése Framenként. """
        # Timer update
        buff_list = [self.dmg_buffs, self.slow_buffs, self.slow_dur_buffs, self.push_buffs, self.stun_buffs]
        buff_index = 0

        while buff_index < len(buff_list):
            i = len(buff_list[buff_index]) - 1
            while i >= 0:
                buff_list[buff_index][i][1] -= dt
                if buff_list[buff_index][i][1] <= 0:
                    buff_list[buff_index].pop(i)
                i -= 1
            buff_index += 1

        # Effect updates
        if self.effect:
            if self.effect.reset_cd:
                self.energy_lvl = 100

            self.effect.dmg = self.effect.perm_dmg
            self.effect.slow_eff = self.effect.perm_slow_eff
            self.effect.slow_dur = self.effect.perm_slow_dur
            self.effect.push_speed = self.effect.perm_push_speed
            self.effect.stun_dur = self.effect.perm_stun_dur

            if self.dmg_buffs:
                self.effect.dmg = self.effect.perm_dmg * sum([x[0] for x in self.dmg_buffs])
            if self.slow_buffs:
                self.effect.slow_eff = self.effect.perm_slow_eff * sum([x[0] for x in self.slow_buffs])
            if self.slow_dur_buffs:
                self.effect.slow_dur = self.effect.perm_slow_dur * sum([x[0] for x in self.slow_dur_buffs])
            if self.push_buffs:
                self.effect.push_speed = self.effect.perm_push_speed * sum([x[0] for x in self.push_buffs])
            if self.stun_buffs:
                self.effect.stun_dur = self.effect.perm_stun_dur * sum([x[0] for x in self.stun_buffs])

        else:  # self.projectile
            if self.projectile.effect.reset_cd:
                self.energy_lvl = 100

            self.projectile.effect.dmg = self.projectile.effect.perm_dmg
            self.projectile.effect.slow_eff = self.projectile.effect.perm_slow_eff
            self.projectile.effect.slow_dur = self.projectile.effect.perm_slow_dur
            self.projectile.effect.push_speed = self.projectile.effect.perm_push_speed
            self.projectile.effect.stun_dur = self.projectile.effect.perm_stun_dur

            if self.dmg_buffs:
                self.projectile.effect.dmg = self.projectile.effect.perm_dmg * sum([x[0] for x in self.dmg_buffs])
            if self.slow_buffs:
                self.projectile.effect.slow_eff = self.projectile.effect.perm_slow_eff * sum([x[0] for x in self.slow_buffs])
            if self.slow_dur_buffs:
                self.projectile.effect.slow_dur = self.projectile.effect.perm_slow_dur * sum([x[0] for x in self.slow_dur_buffs])
            if self.push_buffs:
                self.projectile.effect.push_speed = self.projectile.effect.perm_push_speed * sum([x[0] for x in self.push_buffs])
            if self.stun_buffs:
                self.projectile.effect.stun_dur = self.projectile.effect.perm_stun_dur * sum([x[0] for x in self.stun_buffs])

    def update_effects(self, characters_group):
        # még ezt is frissíteni kell a sok buff listával.
        if self.effect:
            self.effect.perm_dmg = self.effect.base_dmg * self.talent_dmg_multi * self.upg_dmg_multi

            for char in characters_group:
                if char.name == self.created_by:
                    for lvl, talent_group in char.talent_tree.talent_dict.items():
                        for talents in talent_group:
                            for talent in talents:
                                if talent.status == 'Picked':
                                    self.effect.perm_dmg *= talent.dmg
                    break

        else:  # self.projectile
            self.projectile.effect.perm_dmg = self.projectile.effect.base_dmg * self.talent_dmg_multi * self.upg_dmg_multi

            for char in characters_group:
                if char.name == self.created_by:
                    for lvl, talent_group in char.talent_tree.talent_dict.items():
                        for talents in talent_group:
                            for talent in talents:
                                if talent.status == 'Picked':
                                    self.projectile.effect.perm_dmg *= talent.dmg
                    break

    def update_trap_dir(self):
        if self.effect:
            self.effect.degree = self.degree
            if self.effect.type == 'Trap Effect':
                # self.detect_rect = self.rect
                if self.effect.detect_range:
                    self.detect_rect = generate_detect_rect(self.rect, self.degree, self.effect.detect_range)

        elif self.projectile:
            self.projectile.degree = self.degree
            if self.projectile.target_type == 'Trap Area':
                # self.detect_rect = self.rect
                if self.projectile.detect_range:
                    self.detect_rect = generate_detect_rect(self.rect, self.degree, self.projectile.detect_range)

                    if self.projectile.target_type == 'Trap Area':
                        self.projectile.detect_rect = self.detect_rect

            else:
                self.projectile.rect.center = self.coord = self.rect.center

    def image_update(self, current_time):
        if self.obj_img_timer + self.obj_fps < current_time:
            self.image_idx += 1
            if self.image_idx > self.image_count:
                self.image_idx = 0
            self.image = pygame.transform.rotate(self.obj_imgs[self.image_idx].copy(), -self.degree)
            self.obj_img_timer = current_time

    def rotate(self, degree):
        self.image = pygame.transform.rotate(self.image, -degree)
        self.degree += degree
        if self.degree > 270:
            self.degree = 0
        elif self.degree < 0:
            self.degree = 270

    def hit(self, dmg):
        self.sp -= dmg

    def draw(self, SCREEN, base_scroll):
        if base_scroll[0] - self.rect.width < self.rect.x < base_scroll[0] + client_data.width \
                and base_scroll[1] - self.rect.height < self.rect.y < base_scroll[1] + client_data.height:
            SCREEN.blit(self.image, (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1]))

            if self.transp:
                pygame.draw.rect(SCREEN, (255, 0, 0),
                    (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1], self.rect.w, self.rect.h), 3)
                try:
                    pygame.draw.rect(SCREEN, (0, 255, 0),
                                     (self.detect_rect.x - base_scroll[0],
                                      self.detect_rect.y - base_scroll[1],
                                      self.detect_rect.w, self.detect_rect.h), 2)  # hatóterület megjelenítés
                except AttributeError:
                    pygame.draw.circle(SCREEN, (0, 255, 0),
                                       (self.rect.centerx - int(base_scroll[0]),
                                        self.rect.centery - int(base_scroll[1])),
                                       self.effect.detect_range, 2)

    def draw_effects(self, SCREEN, base_scroll):
        for i, lst in self.eff_dict.items():
            target_enemy, img_idx, radians = lst

            height = int(self.eff_imgs[0].get_height() * self.range / self.eff_imgs[0].get_width())
            image = pygame.transform.scale(self.eff_imgs[img_idx], (self.range, height))
            image = pygame.transform.rotate(image, -math.degrees(radians))
            x = math.cos(radians) * self.range / 2
            y = math.sin(radians) * self.range / 2
            eff_coord = (self.rect.center[0] + x, self.rect.center[1] + y)
            rect = image.get_rect(center=eff_coord)

            SCREEN.blit(image, (rect.x - base_scroll[0], rect.y - base_scroll[1]))

    def draw_upgrades(self, SCREEN, base_scroll):
        for img in self.upg_icons:
            color, rect = img
            pygame.draw.rect(SCREEN, color, (rect.x - base_scroll[0], rect.y - base_scroll[1], rect.width, rect.height))
            pygame.draw.rect(SCREEN, (0, 0, 0), (rect.x - base_scroll[0], rect.y - base_scroll[1], rect.width, rect.height), 1)

    def update_upgrades(self):
        for i, upgrade in enumerate(self.upgrades):
            self.upg_icons[i][0] = upgrade.icon_color


def create_object(code, coord=(0, 0), transp=False):
    cp(724, 'must fix eventually')
    object_dict = {
        'T-02': Object('Any', 'Tile', 'Grass', [grass_pic], coord, 0, False, transp=transp),
        'T-03': Object('Any', 'Tile', 'Floor', [floor_pic], coord, 0, False, wood=2, transp=transp),
        'T-04': Object('Any', 'Tile', 'Wall', [wall_pic], coord, 0, True, stone=10, transp=transp),

        'O-01': Object('Grass', 'Object', 'Tree', [garden_obj_1_pic], coord, 20, True, transp=transp),
        'O-02': Object('Grass', 'Object', 'Flower', [garden_obj_2_pic], coord, 0, False, transp=transp),
        'O-03': Object('Grass', 'Object', 'Fence', [garden_obj_3_pic], coord, 0, True, wood=2, transp=transp),
        'O-04': Object('Grass', 'Object', 'Dog House', [garden_obj_4_pic], coord, 30, True, wood=3, transp=transp),
        'O-05': Object('Grass', 'Object', 'Dog House', [garden_obj_5_pic], coord, 30, True, wood=3, transp=transp),
        'O-06': Object('Grass', 'Object', 'Dog House', [garden_obj_6_pic], coord, 30, True, wood=3, transp=transp),
        'O-07': Object('Grass', 'Object', 'Dog House', [garden_obj_7_pic], coord, 30, True, wood=3, transp=transp),

        'O-08': Object('Floor', 'Object', 'Science Machine', [floor_obj_1_pic], coord, 0, True, gear=5, upkeep=10, transp=transp),
        'O-09': Object('Floor', 'Object', 'Squirrel Wheel', [floor_obj_2_pic], coord, 0, True, wood=1, gear=1, squirrel=1, output=5, transp=transp),
        'O-10': Object('Floor', 'Object', 'Cabient', [floor_obj_3_pic], coord, 0, True, comfort=10, item_cap=4, transp=transp),
        'O-11': Object('Floor', 'Object', 'Bed', [floor_obj_4_pic], coord, 0, True, fatigue=20, item_cap=4, transp=transp),
        'O-12': Object('Floor', 'Object', 'Cupboard', [floor_obj_5_pic], coord, 0, True, comfort=10, item_cap=4, transp=transp),
        'O-13': Object('Floor', 'Object', 'Table', [floor_obj_6_pic], coord, 30, True, comfort=10, transp=transp),
        'O-14': Object('Floor', 'Object', 'Chest', [floor_obj_7_pic], coord, 0, True, transp=transp),

        'O-15': Object('Wall', 'Object', 'Window', [wall_obj_1_pic], coord, 20, True, comfort=10, transp=transp),
        'O-16': Object('Wall', 'Object', 'Door', [wall_obj_2_pic], coord, 20, False, transp=transp),
        'O-17': Object('Wall', 'Object', 'Picture', [wall_obj_3_pic], coord, 20, False, comfort=10, transp=transp),
        'O-18': Object('Wall', 'Object', 'Picture', [wall_obj_4_pic], coord, 20, False, comfort=10, transp=transp),
        'O-19': Object('Wall', 'Object', 'Picture', [wall_obj_5_pic], coord, 20, False, comfort=10, transp=transp),
        'O-20': Object('Wall', 'Object', 'Picture', [wall_obj_6_pic], coord, 20, False, comfort=10, transp=transp),
        'O-21': Object('Wall', 'Object', 'Picture', [wall_obj_7_pic], coord, 20, False, comfort=10, transp=transp),

        'O-22': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_1_pic], coord, 20, False, effect=spike_trap, transp=transp),
        'O-23': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_2_pic], coord, 20, False, effect=spike_trap, transp=transp),
        'O-24': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_3_pic], coord, 20, False, effect=spike_trap, transp=transp),
        'O-25': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_4_pic], coord, 20, False, effect=spike_trap, transp=transp),
        'O-26': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_5_pic], coord, 20, False, effect=spike_trap, transp=transp),
        'O-27': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_6_pic], coord, 20, False, effect=spike_trap, transp=transp),
        'O-28': Object('Grass', 'Trap', 'Spike Trap', [garden_trap_7_pic], coord, 20, False, effect=spike_trap, transp=transp),

        'O-29': Trap('Floor', 'Trap', 'Spike Trap', [floor_trap_1_pic], coord, 20, False, gear=1, upkeep=1, effect=spike_trap, transp=transp),
        'O-30': Trap('Floor', 'Trap', 'Autocannon', [floor_trap_2_pic], coord, 20, True, gear=1, upkeep=2, projectile=cannonball, transp=transp),
        'O-31': Trap('Floor', 'Trap', 'Catapult', [floor_trap_3_pic], coord, 20, True, gear=1, upkeep=2, projectile=catapult_shot, transp=transp),
        'O-32': Trap('Floor', 'Trap', 'Glue Gun', [floor_trap_4_pic], coord, 20, True, gear=1, upkeep=2, projectile=glue, transp=transp),
        'O-33': Trap('Floor', 'Trap', 'Machine Gunner', [floor_trap_5_pic], coord, 20, False, wood=1, gear=1, upkeep=3, sp=15, aggro=200, projectile=bullet, transp=transp),
        'O-34': Trap('Floor', 'Trap', 'Decoy', [floor_trap_6_pic], coord, 20, False, wood=1, gear=1, sp=20, aggro=400, effect=taunt, transp=transp),
        'O-35': Trap('Floor', 'Trap', 'Decoy', [floor_trap_7_pic], coord, 20, False, wood=1, gear=1, sp=20, aggro=400, effect=taunt, transp=transp),

        'O-36': Trap('Wall', 'Trap', 'Grinder', [wall_trap_1_pic], coord, 20, False, gear=1, upkeep=2, effect=grinder, transp=transp),
        'O-37': Trap('Wall', 'Trap', 'Wall Blades', [wall_trap_2_pic], coord, 20, False, gear=3, upkeep=5, effect=wall_blades, transp=transp),
        'O-38': Trap('Wall', 'Trap', 'Snow Blower', [wall_trap_3_pic], coord, 20, False, gear=1, upkeep=5, effect=snow_blower, transp=transp),
        'O-39': Trap('Wall', 'Trap', 'Air Went', [wall_trap_4_pic], coord, 20, False, gear=1, upkeep=5, effect=air_went, transp=transp),
        'O-40': Trap('Wall', 'Trap', 'Push Trap', [wall_trap_5_pic], coord, 20, False, gear=1, upkeep=5, effect=push_trap, transp=transp),
        'O-41': Trap('Wall', 'Trap', 'Arrow Wall', [wall_trap_6_pic], coord, 20, False, gear=1, upkeep=1, projectile=arrow, transp=transp),
        'O-42': Trap('Wall', 'Trap', 'Arrow Wall', [wall_trap_7_pic], coord, 20, False, gear=1, upkeep=1, projectile=arrow, transp=transp),

        'O-43': Trap('Floor', 'Trap', 'Tesla Coil', tesla_coil_pics, coord, 20, True, gear=1, upkeep=10, range=200, eff_imgs=lightning_pics, transp=transp),
        'O-44': Upgrade('Any', 'Upgrade', 'Overcharger', overcharger_pic, coord, (0, 100, 255), gear=1, upkeep=1, damage_multi=2, upkeep_multi=1.3, output_multi=1.2, transp=transp),
        'O-45': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp),
        'O-46': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp),
        'O-47': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp),
        'O-48': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp),
        'O-49': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp),
        'O-50': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp),
        'O-51': Trap('Floor', 'Placeholder', 'Oth Coil', [question_mark], coord, 20, True, upkeep=5, transp=transp)
    }

    for obj_code, obj in object_dict.items():
        if code == obj_code:
            return obj


class Cursor(pygame.sprite.Sprite):
    def __init__(self, radius):
        super().__init__()
        self.rect = pygame.Rect(0, 0, radius, radius)
        self.radius = radius


class InfoBox(pygame.sprite.Sprite):
    def __init__(self, cell_size):
        super().__init__()
        self.x = 0
        self.y = 0
        self.dist_from_cursor = 15
        self.rect = pygame.Rect(0, 0, 200, 100)
        self.background_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.font_size = 14
        self.style = 'comicsans'
        self.font = pygame.font.SysFont(self.style, self.font_size)
        self.rendered_text_list = []
        self.cell_size = cell_size

    def update(self, new_coord, base_scroll, matrix_dict):
        # Position
        self.x, self.y = new_coord
        self.rect.topleft = (self.x - base_scroll[0] + self.dist_from_cursor, self.y - base_scroll[1] + self.dist_from_cursor)

        # Data
        matrix_coord = get_matrix_coord(new_coord, self.cell_size)
        tile = matrix_dict[matrix_coord]["Tile"]
        object = matrix_dict[matrix_coord]["Object"]
        trap = matrix_dict[matrix_coord]["Trap"]

        self.rendered_text_list = []
        self.rendered_text_list.append(
            self.font.render(f'Tile: {tile.name} - by {tile.created_by}', 1, self.text_color))

        if object:
            self.rendered_text_list.append(self.font.render(f'Object: {object.name} - by {object.created_by}', 1, self.text_color))
            upgrade_names = [upgrade.name for upgrade in object.upgrades]
            if upgrade_names:
                self.rendered_text_list.append(self.font.render(f'Upgrades: {", ".join(upgrade_names)}', 1, self.text_color))
            else:
                self.rendered_text_list.append(self.font.render(f'Upgrades: -', 1, self.text_color))

            self.rendered_text_list.append(self.font.render('', 1, self.text_color))
            if object.upkeep:
                self.rendered_text_list.append(self.font.render(f'Upkeep: {object.upkeep}', 1, self.text_color))
            elif object.output:
                self.rendered_text_list.append(
                    self.font.render(f'Output: {object.output}', 1, self.text_color))
            if object.fatigue:
                self.rendered_text_list.append(self.font.render(f'Fatigue: {object.fatigue}', 1, self.text_color))

            # Modifiers
            self.rendered_text_list.append(self.font.render('', 1, self.text_color))
            if object.talent_output_multi != 1:
                self.rendered_text_list.append(self.font.render(f'Output mlt.: {object.upg_output_multi * object.talent_output_multi}', 1, self.text_color))

        elif trap:
            self.rendered_text_list.append(self.font.render(f'Trap: {trap.name} - by {trap.created_by}', 1, self.text_color))
            upgrade_names = [upgrade.name for upgrade in trap.upgrades]
            if upgrade_names:
                self.rendered_text_list.append(
                    self.font.render(f'Upgrades: {", ".join(upgrade_names)}', 1, self.text_color))

            self.rendered_text_list.append(self.font.render('', 1, self.text_color))
            if trap.upkeep:
                self.rendered_text_list.append(self.font.render(f'Upkeep: {trap.upkeep}', 1, self.text_color))
            if trap.projectile:
                self.rendered_text_list.append(self.font.render(f'Damage: {trap.projectile.effect.dmg * trap.upg_dmg_multi * trap.talent_dmg_multi}', 1, self.text_color))
                if trap.projectile.target_type == 'Trap Area':
                    self.rendered_text_list.append(self.font.render(f'Explosion damage: {trap.projectile.effect.explosion_dmg * trap.upg_dmg_multi * trap.talent_dmg_multi}', 1, self.text_color))
            else:
                self.rendered_text_list.append(self.font.render(f'Damage: {trap.effect.dmg * trap.upg_dmg_multi * trap.talent_dmg_multi}', 1, self.text_color))

            self.rendered_text_list.append(self.font.render(f'Damage count: {trap.dmg_counter}', 1, self.text_color))
            self.rendered_text_list.append(self.font.render('', 1, self.text_color))

            # Modifiers
            if trap.upg_upkeep_multi * trap.talent_upkeep_multi != 1:
                self.rendered_text_list.append(self.font.render(
                    f'Upkeep mlt.: {trap.upg_upkeep_multi * trap.talent_upkeep_multi}', 1, self.text_color))
            if trap.upg_dmg_multi * trap.talent_dmg_multi != 1:
                self.rendered_text_list.append(self.font.render(
                    f'Damage mlt.: {trap.upg_dmg_multi * trap.talent_dmg_multi}', 1, self.text_color))
            if trap.upg_range_multi * trap.talent_range_multi != 1:
                self.rendered_text_list.append(self.font.render(
                    f'Range mlt.: {trap.upg_range_multi * trap.talent_range_multi}', 1, self.text_color))
            if trap.upg_xp_multi * trap.talent_xp_multi != 1:
                self.rendered_text_list.append(self.font.render(
                    f'XP mlt.: {trap.upg_xp_multi * trap.talent_xp_multi}', 1, self.text_color))
            if trap.upg_loot_multi * trap.talent_loot_multi != 1:
                self.rendered_text_list.append(self.font.render(
                    f'Loot mlt.: {trap.upg_loot_multi * trap.talent_loot_multi}', 1, self.text_color))

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.background_color, self.rect)
        self.rect.move_ip(5, 5)
        for text in self.rendered_text_list:
            SCREEN.blit(text, self.rect)
            self.rect.move_ip(0, 10)


class Item(pygame.sprite.Sprite):
    def __init__(self, name, image, x, y, radius, global_aggro=0):
        super().__init__()

        # Stats
        self.name = name
        self.global_aggro = global_aggro
        self.global_aggro_save = global_aggro
        self.istaken = False

        # Image
        self.image_num = 0  # lehetne ez a számláló az animációhoz
        # a self.image pedig ez alapján frissítené magát. Kérdés hogy fixen be kell e tölteni ide a képeket, vagy elég1?
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.radius = radius

    def draw(self, SCREEN, base_scroll):
        SCREEN.blit(self.image, (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1]))


golden_turkey = Item('Golden Turkey', turkey_pic, 300, 300, 20, global_aggro=50)
items_group = pygame.sprite.Group()
items_group.add(golden_turkey)


class Player:
    def __init__(self, id=-1):
        self.id = id
        self.name = ''
        self.char_id = -1
        self.isready = False


class Character(pygame.sprite.Sprite):
    def __init__(self, id, images, name, char_class, description,
                 speed, hp, x, y,
                 skills, battle_skills, talent_tree,
                 wood, stone, gear, squirrel, egg, chicken, chicken_leg):
        super().__init__()
        self.id = id
        self.name = name
        self.char_class = char_class
        self.description = description
        self.isTaken = False
        self.type = 'Character'

        # Skill Tree
        self.talent_tree = talent_tree

        # Stats
        self.base_speed = speed
        self.perm_speed = speed
        self.speed = speed
        self.base_hp = hp
        self.hp = hp
        self.hp_percent = 100
        self.base_aggro = 100
        self.aggro = 100

        # Base Multipliers
        self.base_speed_multi = 1
        self.base_hp_multi = 1
        self.base_dmg_multi = 1
        self.basic_attack_range_multi = 1
        self.basic_attack_cd_multi = 1
        self.base_aggro_multi = 1
        self.base_cd_multi = 1
        self.base_xp_multi = 1
        self.base_loot_multi = 1

        # Actual Multipliers
        self.speed_multi = self.base_speed_multi
        self.hp_multi = self.base_hp_multi
        self.dmg_multi = self.base_dmg_multi
        self.attack_range_multi = self.basic_attack_range_multi
        self.attack_cd_multi = self.basic_attack_cd_multi
        self.aggro_multi = self.base_aggro_multi
        self.cd_multi = self.base_cd_multi
        self.xp_multi = self.base_xp_multi
        self.loot_multi = self.base_loot_multi

        # Buffs
        self.speed_buffs = []  # [40%, 10sec]
        self.dmg_buffs = []

        # Debuffs
        self.stun_dur = 0

        # Skills
        self.craft_skill1, self.craft_skill2, self.craft_skill3, self.craft_skill4 = skills
        self.battle_skill0, self.battle_skill1, self.battle_skill2, self.battle_skill3, self.battle_skill4 = battle_skills

        # Image
        self.image_timer = time.time()
        self.fps = 0.3
        self.image_idx = 0
        self.images = images
        self.image_count = len(self.images) - 1
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.coord = list(self.rect.center)
        self.radius = 20
        self.degree = 0
        self.fixed_coord = ()
        self.fixed_coord2 = ()

        # Health Bar
        self.hp_bar = None
        self.hp_bar_max_width = 0
        self.hp_bar_height = 0
        self.dmg_bar = None

        # Resources
        self.resources = {
            'Wood': wood,
            'Stone': stone,
            'Gear': gear,
            'Squirrel': squirrel,
            'Chicken': chicken,
            'Egg': egg,
            'Chicken leg': chicken_leg}

        # Movement / Action
        self.movement_points = 0
        self.action = None
        self.target_enemy = None
        self.new_object = None

        # Orders
        self.orders_num = 0
        self.new_order = ['Waiting', [None, None]]
        self.orders = [self.new_order]  # [[type, target_coord]]
        self.new_orders_data = None
        self.path = []
        self.timeline = []  # [[time, orders_num, orders]]
        self.data_diff_list = [0,0,0,0,0,0,0,0,0]

        # Statistics
        self.dmg_counter = 0

        # Temp
        self.collision_coord = None

    def update(self, game_objects, game_data):
        order_type, target = self.orders[0]

        if order_type == 'Waiting':
            return
        elif order_type == 'Move':
            follow_path(self, game_data, game_objects)
            if not self.path:
                self.orders.pop(0)
        else:
            if game_data.battle_mode:
                if order_type == 'S-00':
                    self.execute(self.battle_skill0, game_objects, game_data, target)
                elif order_type == 'S-01':
                    if self.execute(self.battle_skill1, game_objects, game_data, target):
                        self.orders.pop(0)
                elif order_type == 'S-02':
                    if self.execute(self.battle_skill2, game_objects, game_data, target):
                        self.orders.pop(0)
                elif order_type == 'S-03':
                    if self.execute(self.battle_skill3, game_objects, game_data, target):
                        self.orders.pop(0)
                elif order_type == 'S-04':
                    if self.execute(self.battle_skill4, game_objects, game_data, target):
                        self.orders.pop(0)
            else:
                if game_objects.transparent_group.sprite:
                    self.crafting(game_objects)
                self.orders.pop(0)

        if len(self.orders) == 0:
            self.remove_order()

    def update_skills(self, dt):
        self.battle_skill0.timer += dt
        self.battle_skill1.timer += dt
        self.battle_skill2.timer += dt
        self.battle_skill3.timer += dt
        self.battle_skill4.timer += dt

        self.speed = self.perm_speed

        i = len(self.speed_buffs) - 1
        while i >= 0:
            self.speed_buffs[i][1] -= dt
            if self.speed_buffs[i][1] > 0:
                self.speed = self.perm_speed * self.speed_buffs[i][0]
            i -= 1

        self.speed_buffs = [x for x in self.speed_buffs if x[1] > 0]

    def update_stats(self, game_data):
        # fatigue és comfort a game_data-ban kéne legyen
        # fatigue a mozgási sebességet,
        # comfort a karakter cd-t befolyásolja.
        self.perm_speed = self.base_speed * self.speed_multi
        self.hp = self.base_hp * self.hp_multi * game_data.hp_multi
        self.aggro = self.base_aggro * self.aggro_multi
        hp_bonuses = 0
        speed_bonuses = 0

        for lvl, talent_group in self.talent_tree.talent_dict.items():
            for talents in talent_group:
                for talent in talents:
                    if talent.status == 'Picked':
                        hp_bonuses += talent.hp
                        speed_bonuses += talent.speed
        self.hp = int(self.hp * (100 + hp_bonuses) / 100)
        self.perm_speed = int(self.perm_speed * (100 + speed_bonuses) / 100)

    def update_image(self):
        current_time = time.time()
        if self.image_timer + self.fps < current_time:
            self.image_idx += 1
            if self.image_idx > self.image_count:
                self.image_idx = 0
            self.image = self.images[self.image_idx]
            self.image_timer = current_time

    def remove_order(self):
        if len(self.orders) > 0:
            self.orders.pop(0)
        if len(self.orders) == 0:
            self.new_order = ['Waiting', [None, None]]
            self.orders.append(self.new_order)
        else:
            self.new_order = self.orders[0]

    def get_order(self, order_type, target_coord, battle_skill, game_data, game_objects):
        if battle_skill.target_type == 'Self':
            game_objects.my_char_group.sprite.new_order = [order_type, game_objects.my_char_group.sprite.rect.center]
        elif battle_skill.target_type == 'Coord':
            game_objects.my_char_group.sprite.new_order = [order_type, target_coord]
        elif battle_skill.target_type == 'Single Target':

            if battle_skill.effect:
                if battle_skill.effect.type in ['Skill Effect']:
                    for enemy in game_objects.enemies_group:
                        if enemy.rect.collidepoint(target_coord):
                            game_objects.my_char_group.sprite.new_order = [order_type, enemy]
                elif battle_skill.effect.type == 'Trap Buff':
                    for trap in game_objects.trap_group:
                        if trap.rect.collidepoint(target_coord):
                            game_objects.my_char_group.sprite.new_order = [order_type, trap]
                elif battle_skill.effect.type == 'Character Buff':
                    for character in game_objects.characters_group:
                        if character.rect.collidepoint(target_coord):
                            game_objects.my_char_group.sprite.new_order = [order_type, character]

            else:  # battle_skill.projectile
                # itt tartok - a Trap Buff és Char buff is frissítést igényel
                if battle_skill.projectile.effect.type in ['Skill Effect']:
                    targets = detect_targets(
                        game_objects.enemies_group, starting_coord=target_coord,
                        max_targets=1, detect_range=game_data.detect_range)
                    if targets:
                        game_objects.my_char_group.sprite.new_order = [order_type, targets[0]]
                elif battle_skill.projectile.effect.type == 'Trap Buff':
                    targets = detect_targets(
                        game_objects.trap_group, starting_coord=target_coord,
                        max_targets=1, detect_range=game_data.detect_range)
                    game_objects.my_char_group.sprite.new_order = [order_type, targets[0]]
                elif battle_skill.projectile.effect.type == 'Character Buff':
                    targets = detect_targets(
                        game_objects.characters_group, starting_coord=target_coord,
                        max_targets=1, detect_range=game_data.detect_range)
                    game_objects.my_char_group.sprite.new_order = [order_type, targets[0]]

    def draw(self, SCREEN, cam_scroll):
        SCREEN.blit(self.image, (self.rect.x - cam_scroll[0],
                                 self.rect.y - cam_scroll[1]))

        if self.collision_coord:
            pygame.draw.circle(SCREEN, (255, 0, 0), self.collision_coord, 3, 1)

        if self.fixed_coord:
            first_coord = self.rect.center[0] - cam_scroll[0], self.rect.center[1] - cam_scroll[1]
            second_coord = self.fixed_coord[0] - cam_scroll[0], self.fixed_coord[1] - cam_scroll[1]
            pygame.draw.line(SCREEN, (0, 0, 0), first_coord, second_coord, 3)
            first_coord = self.rect.center[0] - cam_scroll[0], self.rect.center[1] - cam_scroll[1]
            second_coord = self.fixed_coord2[0] - cam_scroll[0], self.fixed_coord2[1] - cam_scroll[1]
            pygame.draw.line(SCREEN, (0, 0, 0), first_coord, second_coord, 3)

    def draw_hp_bar(self, SCREEN):
        SCREEN.fill((255, 0, 0), self.dmg_bar)
        pygame.draw.rect(SCREEN, (0, 255, 0), self.hp_bar)

    def set_health_bar_size(self, client_data):
        self.hp_bar_max_width = client_data.width - 100
        self.hp_bar_height = 20  # lehetne majd a képernyő mérethez igazítani
        self.hp_bar = pygame.Rect(50, client_data.height - 100 - self.hp_bar_height, self.hp_bar_max_width, self.hp_bar_height)
        self.dmg_bar = pygame.Rect(50, client_data.height - 100 - self.hp_bar_height, self.hp_bar_max_width, self.hp_bar_height)

    def crafting(self, game_objects, isServer=False):
        new_object = game_objects.transparent_group.sprite.__copy__()
        # ez a 2 sor csak arra van, hogy a cellák indexét kiírjam
        # new_object.text = str(get_cell_coord(new_object.rect.topleft, 50))
        # new_object.rendered_text = new_object.font.render(new_object.text, 1, (255, 255, 255))

        coord = new_object.rect.topleft

        if new_object.type in ['Object', 'Trap']:
            if new_object.craftable_to != 'Any':
                for tile_obj in game_objects.tile_group:
                    if tile_obj.rect.topleft == coord:
                        if tile_obj.name != new_object.craftable_to:
                            print('Ide nem lehet craftolni')
                            return
                        break

        if new_object.type == 'Upgrade':
            found_it = False
            for obj in game_objects.object_group:
                if obj.rect.topleft == coord:
                    found_it = True
                    if len(obj.upgrades) < 2:
                        break
                    else:
                        print('Nincs szabad hely.')
                        return
            if not found_it:
                for trap in game_objects.trap_group:
                    if trap.rect.topleft == coord:
                        if len(trap.upgrades) < 2:
                            break
                        else:
                            print('Nincs szabad hely.')
                            return

        elif new_object.type == 'Object':
            for obj in game_objects.object_group:
                if obj.rect.topleft == coord:
                    print('Már van ide építve.')
                    return

        elif new_object.type == 'Trap':
            for trap in game_objects.trap_group:
                if trap.rect.topleft == coord:
                    print('Már van ide építve.')
                    return

        elif new_object.type == 'Tile':
            for tile_obj in game_objects.tile_group:
                if tile_obj.rect.topleft == coord:
                    if tile_obj.name == new_object.name:
                        print('Már van ilyen építve.')
                        return

        for resource in [
            self.resources['Wood'] - new_object.cost['Wood'],
            self.resources['Stone'] - new_object.cost['Stone'],
            self.resources['Gear'] - new_object.cost['Gear'],
            self.resources['Squirrel'] - new_object.cost['Squirrel'],
            self.resources['Chicken'] - new_object.cost['Chicken'],
            self.resources['Egg'] - new_object.cost['Egg'],
            self.resources['Chicken leg'] - new_object.cost['Chicken leg']
        ]:
            if resource < 0:
                return

        self.remove_cost(new_object)
        
        new_object.created_by = self.name

        if new_object.type == 'Upgrade':
            found_it = False
            for obj in game_objects.object_group:
                if obj.rect.topleft == coord:
                    obj.upgrades.append(new_object)
                    obj.update_upgrades()
                    found_it = True
                    break
            if not found_it:
                for trap in game_objects.trap_group:
                    if trap.rect.topleft == coord:
                        trap.upgrades.append(new_object)
                        trap.update_upgrades()
                        break

        elif new_object.type == 'Object':
            game_objects.matrix.dict[new_object.rect.topleft]['Object'] = new_object
            game_objects.object_group.add(new_object)
            if new_object.blocker:
                game_objects.blocker_group.add(new_object)

        elif new_object.type == 'Trap':
            game_objects.matrix.dict[new_object.rect.topleft]['Trap'] = new_object
            game_objects.trap_group.add(new_object)
            if new_object.blocker:
                game_objects.blocker_group.add(new_object)

        elif new_object.type == 'Tile':
            game_objects.matrix.dict[new_object.rect.topleft]['Tile'] = new_object
            for tile_obj in game_objects.tile_group:
                if tile_obj.rect.topleft == coord:
                    tile_obj.kill()
                    break
            game_objects.tile_group.add(new_object)
            if new_object.blocker:
                game_objects.blocker_group.add(new_object)

        game_objects.matrix.update(new_object.rect.topleft)

    def destroy(self, coord, game_objects):
        matrix_coord = get_matrix_coord(coord, game_objects.node_size)
        if game_objects.matrix.dict[matrix_coord]['Object']:
            if game_objects.matrix.dict[matrix_coord]['Object'].created_by in [self.name, None]:
                self.add_resources(game_objects.matrix.dict[matrix_coord]['Object'])
                game_objects.matrix.dict[matrix_coord]['Object'] = None
                for obj in game_objects.object_group:
                    if obj.rect.topleft == matrix_coord:
                        obj.kill()
        elif game_objects.matrix.dict[matrix_coord]['Trap']:
            if game_objects.matrix.dict[matrix_coord]['Trap'].created_by in [self.name, None]:
                self.add_resources(game_objects.matrix.dict[matrix_coord]['Trap'])
                game_objects.matrix.dict[matrix_coord]['Trap'] = None
                for trap in game_objects.trap_group:
                    if trap.rect.topleft == matrix_coord:
                        trap.kill()
        elif game_objects.matrix.dict[matrix_coord]['Tile']:
            if game_objects.matrix.dict[matrix_coord]['Tile'].created_by in [self.name, None]:
                self.add_resources(game_objects.matrix.dict[matrix_coord]['Tile'])
                game_objects.matrix.dict[matrix_coord]['Tile'] = None
                for tile in game_objects.tile_group:
                    if tile.rect.topleft == matrix_coord:
                        tile.kill()

        game_objects.matrix.update(matrix_coord)

    def add_resources(self, object):
        self.resources['Wood'] += object.cost['Wood']
        self.resources['Stone'] += object.cost['Stone']
        self.resources['Gear'] += object.cost['Gear']
        self.resources['Squirrel'] += object.cost['Squirrel']
        self.resources['Chicken'] += object.cost['Chicken']
        self.resources['Egg'] += object.cost['Egg']
        self.resources['Chicken leg'] += object.cost['Chicken leg']

    def remove_cost(self, object):
        self.resources['Wood'] -= object.cost['Wood']
        self.resources['Stone'] -= object.cost['Stone']
        self.resources['Gear'] -= object.cost['Gear']
        self.resources['Squirrel'] -= object.cost['Squirrel']
        self.resources['Chicken'] -= object.cost['Chicken']
        self.resources['Egg'] -= object.cost['Egg']
        self.resources['Chicken leg'] -= object.cost['Chicken leg']

    def hit(self, degree, effect):  # degree kelleni fog késöbb
        self.hp -= effect.dmg
        self.hp_percent = 100 / self.base_hp * self.hp

        # Adjust hp bar
        new_width = int(self.hp_bar_max_width / 100 * self.hp_percent)
        self.hp_bar.x = (self.hp_bar_max_width - new_width) / 2 + 50
        self.hp_bar.width = new_width

    def execute(self, battle_skill, game_objects, game_data, target):
        distance = 0
        if battle_skill.target_type == 'Single Target':
            if target:  # itt majd error lesz, ha elöbb megszűnik a target, minthogy végrehajtaná
                distance = abs(complex(*self.rect.center) - complex(*target.rect.center)) - self.radius - target.radius
            else:
                return True  # azaz törölheti az Ordert
        elif battle_skill.target_type == 'Coord':
            distance = abs(complex(*self.rect.center) - complex(*target)) - self.radius

        if battle_skill.range < distance:
            if battle_skill.target_type == 'Single Target':
                if target.type == 'Trap':
                    if target.blocker:
                        game_objects.matrix.dict[target.rect.topleft]['Blocker'] = False
                        self.path = find_path(self.rect.center, target.rect.center, game_objects)
                        game_objects.matrix.dict[target.rect.topleft]['Blocker'] = True
                    else:
                        self.path = find_path(self.rect.center, target.rect.center, game_objects)
                else:
                    self.path = find_path(self.rect.center, target.rect.center, game_objects)
            elif not self.path:
                self.path = find_path(self.rect.center, target.rect.center, game_objects)
            follow_path(self, game_data, game_objects)

        elif battle_skill.timer >= battle_skill.cd:
            ''' Skill execution '''
            if battle_skill.effect:
                if battle_skill.effect.type == 'Skill Effect':
                    targets = []
                    if battle_skill.target_type == 'Self':
                        targets = detect_targets(
                            game_objects.enemies_group, starting_coord=self.rect.center,
                            detect_range=battle_skill.radius)
                    elif battle_skill.target_type == 'Coord':
                        targets = detect_targets(
                            game_objects.enemies_group, starting_coord=target,
                            detect_range=battle_skill.radius)
                    elif battle_skill.target_type == 'Single Target':
                        targets.append(target)

                    if targets:
                        for target in targets:
                            if battle_skill.effect.dmg > 0:
                                self.dmg_counter += target.hit(self.degree, battle_skill.effect)
                            target.speed_buffs.append([battle_skill.effect.speed_buff, battle_skill.effect.speed_buff_dur])
                            target.dmg_buffs.append([battle_skill.effect.dmg_buff, battle_skill.effect.dmg_buff_dur])
                            if target.stun_dur < battle_skill.effect.stun_dur:
                                target.stun_dur = battle_skill.effect.stun_dur

                elif battle_skill.effect.type == 'Trap Buff':
                    targets = []
                    if battle_skill.target_type == 'Self':
                        targets = detect_targets(
                            game_objects.trap_group, starting_coord=self.rect.center,
                            detect_range=battle_skill.radius)
                    elif battle_skill.target_type == 'Coord':
                        targets = detect_targets(
                            game_objects.trap_group, starting_coord=target,
                            detect_range=battle_skill.radius)
                    elif battle_skill.target_type == 'Single Target':
                        targets.append(target)

                    if targets:
                        for target in targets:
                            target.slow_buffs.append([battle_skill.effect.speed_buff, battle_skill.effect.speed_buff_dur])
                            target.dmg_buffs.append([battle_skill.effect.dmg_buff, battle_skill.effect.dmg_buff_dur])
                            if battle_skill.effect.reset_cd:
                                target.energy_lvl = 100

                elif battle_skill.effect.type == 'Character Buff':
                    targets = []
                    if battle_skill.target_type == 'Self':
                        targets = detect_targets(
                            game_objects.characters_group, starting_coord=self.rect.center,
                            detect_range=battle_skill.radius)
                    elif battle_skill.target_type == 'Coord':
                        targets = detect_targets(
                            game_objects.characters_group, starting_coord=target,
                            detect_range=battle_skill.radius)
                    elif battle_skill.target_type == 'Single Target':
                        detect_targets(
                            game_objects.characters_group, starting_coord=target.rect.center,
                            detect_range=battle_skill.radius)

                    if targets:
                        for target in targets:
                            target.speed_buffs.append([battle_skill.effect.speed_buff, battle_skill.effect.speed_buff_dur])
                            target.dmg_buffs.append([battle_skill.effect.dmg_buff, battle_skill.effect.dmg_buff_dur])

            else:  # battle_skill.projectile
                if battle_skill.target_type == 'Single Target':
                    targets = detect_targets(
                        game_objects.enemies_group, starting_coord=target.rect.center,
                        detect_range=game_data.detect_range, max_targets=1)
                    if targets:
                        new_projectile = battle_skill.projectile.__copy__()
                        new_projectile.parent = battle_skill
                        new_projectile.rect = self.rect.copy()
                        new_projectile.coord = self.coord
                        new_projectile.direction = get_direction(first_coord=new_projectile.coord, second_coord=targets[0].rect.center)
                        game_objects.projectiles_group.add(new_projectile)
                    else:
                        self.remove_order()

            battle_skill.timer = 0
            return True

    def get_enemy_target(self, cursor, target_coord, order_type, enemies_group):
        # Amikor van célpont, akkor egy pillanatra vörösesre kéne színezni azt.
        cursor.rect.center = (target_coord)
        nearby_enemies = pygame.sprite.spritecollide(cursor, enemies_group, False, collided=pygame.sprite.collide_circle)
        distance = cursor.radius
        self.target_enemy = None
        for enemy in nearby_enemies:
            current_dist = abs(complex(*cursor.rect.center) - complex(*enemy.rect.center)) - enemy.radius
            if current_dist <= distance:
                distance = current_dist
                self.target_enemy = enemy
        if self.target_enemy:
            self.new_order = [order_type, self.target_enemy]
        else:
            self.new_target(target_coord)

    def update_char_data(self, char_data):
        self.speed = char_data[0]
        self.hp = char_data[1]
        self.dmg = char_data[2]
        self.resources['Wood'] = char_data[3]
        self.resources['Stone'] = char_data[4]
        self.resources['Gear'] = char_data[5]
        self.resources['Squirrel'] = char_data[6]
        self.resources['Chicken'] = char_data[7]
        self.resources['Egg'] = char_data[8]
        self.resources['Chicken leg'] = char_data[9]

    def char_data(self):
        char_data = [
            self.speed, self.hp, self.dmg,
            self.resources
        ]
        return char_data

    def save_data(self):
        char_data = [
            self.self.rect.centerx, self.self.rect.centery,
            self.resources
        ]
        return char_data

    def save_pred_data(self):
        char_pred_data = [
            self.id, self.speed, self.hp, self.dmg,
            self.rect, self.radius,
            self.action, self.orders_num, self.orders,
            self.new_orders_data, self.is_new_order, self.timeline, self.data_diff_list,
            self.resources
        ]
        return char_pred_data

    def apply_diff(self):
        diff_list = self.data_diff_list  # in case it would get overwritten by prediction
        for num in range(len(self.data_diff_list) - 1):
            self.data_diff_list[num] -= diff_list[num]

        self.rect.centerx += diff_list[0]
        self.rect.centery += diff_list[1]
        self.resources['Wood'] += diff_list[2]
        self.resources['Stone'] += diff_list[3]
        self.resources['Gear'] += diff_list[4]
        self.resources['Squirrel'] += diff_list[5]
        self.resources['Chicken'] += diff_list[6]
        self.resources['Egg'] += diff_list[7]
        self.resources['Chicken leg'] += diff_list[8]


class CharacterPrediction(Character):
    pass


class Enemy(pygame.sprite.Sprite):
    def __init__(self, race, images, radius, hp, speed, xp, loot_code, battle_skills, **kwargs):
        super().__init__()
        self.name = None
        self.race = race
        self.description = None
        self.type = 'Enemy'

        # Image
        self.image_timer = time.time()
        self.fps = 0.1
        self.image_idx = 0
        self.images = images
        self.image_count = len(self.images) - 1
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.coord = list(self.rect.center)
        self.radius = radius

        # Actual Stats
        self.perm_speed = speed
        self.speed = speed

        self.max_hp = hp
        self.hp = hp

        self.movement_points = 0

        self.xp = xp
        self.loot_code = loot_code

        # Debuffs
        self.dmg_buffs = []
        self.speed_buffs = []
        self.push_mods = []
        self.stun_dur = 0

        # Skills
        self.battle_skill0 = battle_skills[0]
        self.passive = None

        self.immune_to_group = pygame.sprite.Group()
        self.immune_length = 1

        # Movement / Action
        self.order = ['Waiting', [None, None]]
        self.path = []
        self.degree = 0
        self.algorithm_time = time.time()
        self.algorithm_cd = 1  # sec
        self.aggro_cd = 1
        self.aggro_time = time.time() - self.aggro_cd
        self.aggro_reset = False
        self.target_enemy = None  # alapjáraton a pulyka kéne legyen.
        # target_enemy-t lehet törölni kéne, és csak simán az order-ben tárolni a célpontot

        # HP bar
        self.hp_bar_max_width = int(self.radius * 2)
        self.hp_bar_height = int(self.radius / 3)
        self.hp_bar_x_mod = int(self.radius)
        self.hp_bar_y_mod = int(self.hp_bar_height * 3)
        self.hp_bar_border_width = int(self.radius / 7)
        self.one_hp_width = self.hp_bar_max_width / self.max_hp

        # Sounds
        self.death_sound = pygame.mixer.Sound('Sounds/splat.wav')
        self.death_sound.set_volume(0.2)

        self.__dict__.update(kwargs)

    def __copy__(self):
        return Enemy(
            race=self.race,
            images=self.images,
            radius=self.radius,
            hp=self.hp,
            speed=self.speed,
            xp=self.xp,
            loot_code=self.loot_code,
            battle_skills=[self.battle_skill0])

    def update(self, game_data, game_objects):
        self.update_debuffs(game_data.time_to_act)

        removables = []

        # ez lehet már szükségtelen:
        for obj in self.immune_to_group:
            if obj.creation_time + self.immune_length < time.time():
                removables.append(obj)
        for obj in removables:
            self.immune_to_group.remove(obj)

        if self.hp <= 0:
            self.death_sound.play()
            game_data.xp += self.xp * game_data.xp_multi
            game_data.loot_packs.append(random.choice(loot_dict[self.loot_code]))
            self.kill()
            return

        self.green_hp_bar_rect = pygame.Rect(0, 0, self.hp_bar_max_width, self.hp_bar_height)
        self.red_hp_bar_rect = pygame.Rect(0, 0, self.one_hp_width * (self.max_hp - self.hp), self.hp_bar_height)
        self.hp_bar_border_rect = pygame.Rect(0, 0, self.hp_bar_max_width + 1 * self.hp_bar_border_width,
                                              self.hp_bar_height + 1 * self.hp_bar_border_width)

        # Targeting
        if self.aggro_time + self.aggro_cd < game_data.current_time or self.aggro_reset:
            self.aggro_reset = False
            highest_aggro = 0
            distance = math.inf

            for char in game_objects.characters_group:
                char_dist = abs(complex(*self.rect.center) - complex(*char.rect.center)) - self.radius - char.radius
                if char.aggro > char_dist:  # megnézi hogy aggro range-en belül van-e
                    if char.aggro > highest_aggro:
                        highest_aggro = char.aggro
                        self.target_enemy = char
                        distance = char_dist
                    elif char.aggro == highest_aggro:
                        if char_dist < distance:
                            self.target_enemy = char
                            distance = char_dist

            for trap in game_objects.trap_group:
                trap_dist = abs(complex(*self.rect.center) - complex(*trap.rect.center)) - self.radius - trap.radius
                if trap.aggro > trap_dist:  # megnézi hogy aggro range-en belül van-e
                    if trap.aggro > highest_aggro:
                        highest_aggro = trap.aggro
                        self.target_enemy = trap
                        distance = trap_dist
                    elif trap.aggro == highest_aggro:
                        if trap_dist < distance:
                            self.target_enemy = trap
                            distance = trap_dist

            if golden_turkey.global_aggro > highest_aggro:
                self.target_enemy = golden_turkey

            if self.target_enemy != self.order[1] or not self.path:
                if self.target_enemy == golden_turkey:
                    if self.rect.center == golden_turkey.rect.center:
                        golden_turkey.istaken = True
                        golden_turkey.global_aggro = 0  # ez semmit nem ért
                        for enemy in game_objects.enemies_group:
                            enemy.aggro_reset = True
                        #btw, spawn_pos coord lehetne inkább egy object.
                        target_coord = random.choice(game_objects.spawn_positions)
                        self.path = find_path(self.rect.center, target_coord, game_objects)
                    else:
                        self.order = ['Move', self.target_enemy]
                        self.path = find_path(self.rect.center, self.target_enemy.rect.center, game_objects)
                else:
                    self.order = ['Basic Attack', self.target_enemy]
                self.aggro_time = game_data.current_time

        order_type, target_obj = self.order
        saved_coord = self.coord

        if self.push_mods:  # traps can push them
            for i, mod in enumerate(self.push_mods):
                push_speed, push_degree = mod
                push_amount = push_speed * game_data.time_to_act
                if push_degree == 0:
                    self.coord[1] -= push_amount
                    self.rect.centery -= push_amount
                elif push_degree == 90:
                    self.coord[0] -= push_amount
                    self.rect.centerx -= push_amount
                elif push_degree == 180:
                    self.coord[1] += push_amount
                    self.rect.centery += push_amount
                else:
                    self.coord[0] += push_amount
                    self.rect.centerx += push_amount
                self.push_mods[i][0] -= 100 * game_data.time_to_act
            self.push_mods = [mod for mod in self.push_mods if mod[0] > 0]
            if self.path:
                self.path = find_path(self.rect.center, target, game_objects)

        if self.stun_dur <= 0:
            if order_type == 'Move':
                self.movement_points = self.speed * game_data.time_to_act
                follow_path(self, game_data, game_objects)

            elif order_type == 'Basic Attack':
                self.execute(self.battle_skill0, game_objects, game_data, target_obj)


    def update_debuffs(self, dt):
        self.battle_skill0.timer += dt
        self.stun_dur -= dt

        self.speed = self.perm_speed

        i = len(self.speed_buffs) - 1
        while i >= 0:
            self.speed_buffs[i][1] -= dt
            if self.speed_buffs[i][1] > 0:
                self.speed = self.perm_speed * self.speed_buffs[i][0]
            i -= 1

        self.speed_buffs = [x for x in self.speed_buffs if x[1] > 0]

    def execute(self, battle_skill, game_objects, game_data, target):
        distance = 0
        if battle_skill.target_type == 'Single Target':
            if target:  # itt majd error lesz, ha elöbb megszűnik a target, minthogy végrehajtaná
                distance = abs(complex(*self.rect.center) - complex(*target.rect.center)) - self.radius - target.radius
            else:
                return True  # azaz törölheti az Ordert
        elif battle_skill.target_type == 'Coord':
            distance = abs(complex(*self.rect.center) - complex(*target)) - self.radius

        if battle_skill.range < distance:
            if battle_skill.target_type == 'Single Target':
                if target.type == 'Trap':
                    if target.blocker:
                        game_objects.matrix.dict[target.rect.topleft]['Blocker'] = False
                        self.path = find_path(self.rect.center, target, game_objects)
                        game_objects.matrix.dict[target.rect.topleft]['Blocker'] = True
                    else:
                        self.path = find_path(self.rect.center, target.rect.center, game_objects)
                else:
                    self.path = find_path(self.rect.center, target.rect.center, game_objects)
            elif not self.path:
                self.path = find_path(self.rect.center, target.rect.center, game_objects)

            self.degree = int(math.degrees(get_radians(self.rect.center, self.path[0][0])))
            follow_path(self, game_data, game_objects)

        elif battle_skill.timer >= battle_skill.cd:
            if battle_skill.effect.type == 'Enemy Effect':
                targets = []
                if battle_skill.target_type == 'Self':
                    targets = detect_targets(
                        game_objects.characters_group, starting_coord=self.rect.center,
                        detect_range=battle_skill.radius)
                elif battle_skill.target_type == 'Coord':
                    targets = detect_targets(
                        game_objects.characters_group, starting_coord=target,
                        detect_range=battle_skill.radius)

                elif battle_skill.target_type == 'Single Target':
                    targets.append(target)

                if targets:
                    for target in targets:
                        if battle_skill.effect.dmg > 0:
                            target.hit(self.degree, battle_skill.effect)
                        target.speed_buffs.append([battle_skill.effect.speed_buff, battle_skill.effect.speed_buff_dur])
                        target.dmg_buffs.append([battle_skill.effect.dmg_buff, battle_skill.effect.dmg_buff_dur])
                        if target.stun_dur < battle_skill.effect.stun_dur:
                            target.stun_dur = battle_skill.effect.stun_dur

            battle_skill.timer = 0

    def hit(self, degree, effect):
        self.hp -= effect.dmg  # itt még az esetleges resisteket bele lehetne kalkulálni
        if effect.slow_eff:
            self.speed_buffs.append([effect.slow_eff, effect.slow_dur])
        if effect.push_speed:
            self.push_mods.append([effect.push_speed, degree])

        return effect.dmg

    def draw(self, SCREEN, base_scroll):
        if base_scroll[0] - self.rect.width < self.rect.x < base_scroll[0] + client_data.width \
                and base_scroll[1] - self.rect.height < self.rect.y < base_scroll[1] + client_data.height:
            SCREEN.blit(self.image, (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1]))

            # if self.hp < self.max_hp:
            self.green_hp_bar_rect.x = self.rect.centerx - self.hp_bar_x_mod - base_scroll[0]
            self.green_hp_bar_rect.y = self.rect.y - self.hp_bar_y_mod - base_scroll[1]
            self.red_hp_bar_rect.x = self.rect.centerx - self.hp_bar_x_mod - base_scroll[0]
            self.red_hp_bar_rect.y = self.rect.y - self.hp_bar_y_mod - base_scroll[1]
            self.hp_bar_border_rect.x = self.rect.centerx - self.hp_bar_x_mod - self.hp_bar_border_width - base_scroll[0]
            self.hp_bar_border_rect.y = self.rect.y - self.hp_bar_y_mod - self.hp_bar_border_width - base_scroll[1]
            pygame.draw.rect(
                SCREEN, (0, 255, 0), self.green_hp_bar_rect)
            pygame.draw.rect(
                SCREEN, (255, 0, 0), self.red_hp_bar_rect)
            pygame.draw.rect(
                SCREEN, (0, 0, 0), self.hp_bar_border_rect, self.hp_bar_border_width)

            # pygame.draw.circle(SCREEN, (0,0,0), self.rect.center, self.radius, 1)


def generate_detect_rect(base_rect, degree, detect_range):
    detect_rect = None
    if degree == 0:
        detect_rect = pygame.Rect(
            base_rect.right,
            base_rect.top,
            detect_range,
            base_rect.height)
    elif degree == 90:
        detect_rect = pygame.Rect(
            base_rect.left,
            base_rect.bottom,
            base_rect.width,
            detect_range)
    elif degree == 180:
        detect_rect = pygame.Rect(
            base_rect.left - detect_range,
            base_rect.top,
            detect_range,
            base_rect.height)
    elif degree == 270:
        detect_rect = pygame.Rect(
            base_rect.left,
            base_rect.top - detect_range,
            base_rect.width,
            detect_range)
    return detect_rect


# def tesla_coil(obj, game_objects):  # AOE-ban kéne sebezzen mindenkit akit a villám ér
#     curr_time = time.time()
#     removables = []
#     if obj.energy_lvl >= obj.upkeep:
#         target_enemy = detect_targets(obj, game_objects.enemies_group, game_objects.matrix, single_target=True)
#         if target_enemy:
#             obj.shot_counter += 1
#             obj.dmg_counter += obj.dmg
#             target_enemy.hit(obj)
#             obj.energy_lvl = 0
#             obj.eff_dict[obj.shot_counter] = [target_enemy, -1, 0]
#
#     for i, lst in obj.eff_dict.items():
#         target_enemy, img_idx, prev_rad = lst
#         obj.eff_dict[i][2] = get_radians(obj.rect.center, target_enemy.rect.center)
#
#         if obj.eff_img_timer + obj.eff_fps < curr_time:
#             if img_idx + 1 >= obj.eff_img_count:
#                 removables.append(i)
#             else:
#                 obj.eff_dict[i][1] += 1
#             obj.eff_img_timer = curr_time
#
#     for key in removables:
#         del obj.eff_dict[key]


class Upgrade(pygame.sprite.Sprite):
    def __init__(self, craftable_to, type, name, image, coord, icon_color,
                 transp=False, upkeep=0,
                 damage_multi=1, range_multi=1, output_multi=1, xp_multi=1, loot_multi=1,
                 wood=0, stone=0, gear=0, squirrel=0, chicken=0, chicken_leg=0, egg=0,
                 **kwargs):
        super().__init__()
        # Stats
        self.created_by = None
        self.type = 'Upgrade'
        self.craftable_to = craftable_to
        self.type = type
        self.name = name

        # Object Image
        self.image = image
        self.transp = transp
        if self.transp:
            self.image.set_alpha(150)
        self.rect = self.image.get_rect(topleft=coord)
        self.icon_color = icon_color

        # Cost
        self.cost = {
            'Wood': wood,
            'Stone': stone,
            'Gear': gear,
            'Squirrel': squirrel,
            'Chicken': chicken,
            'Egg': egg,
            'Chicken leg': chicken_leg}

        # Modifiers
        self.upkeep = upkeep

        self.base_damage_multi = damage_multi
        self.base_range_multi = range_multi
        self.base_output_multi = output_multi
        self.base_xp_multi = xp_multi
        self.base_loot_multi = loot_multi

        self.damage_multi = damage_multi
        self.range_multi = range_multi
        self.output_multi = output_multi
        self.xp_multi = xp_multi
        self.loot_multi = loot_multi

        self.__dict__.update(kwargs)

    def __copy__(self):
        return Upgrade(
            craftable_to=self.craftable_to, type=self.type, name=self.name, image=self.image, coord=self.rect.topleft,
            icon_color=self.icon_color, upkeep=self.upkeep, cost=self.cost,
            damage_multi=self.damage_multi, range_multi=self.range_multi,
            output_multi=self.output_multi,
            xp_multi=self.xp_multi, loot_multi=self.loot_multi)

    def update(self, trap):
        cp(2362, 'pass')
        pass

    def draw(self, SCREEN, base_scroll):
        SCREEN.blit(self.image, (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1]))


class Effect:
    def __init__(self, type='Skill Effect', detect_range=0,
                 dmg=0, push_speed=0, stun_dur=0,
                 slow_eff=0, slow_dur=0,
                 speed_buff=1, speed_buff_dur=0,
                 speed_dur_buff=1, speed_dur_buff_dur=0,
                 dmg_buff=1, dmg_buff_dur=0,
                 push_buff=1, push_buff_dur=0,
                 stun_buff=1, stun_buff_dur=0,
                 reset_cd=False):
        # Stats
        self.type = type
        self.detect_range = detect_range  # ez még mindig nem hiszem hogy ide kéne

        # Offensive effects
        self.base_dmg = dmg
        self.perm_dmg = dmg
        self.dmg = dmg

        self.base_push_speed = push_speed
        self.perm_push_speed = push_speed
        self.push_speed = push_speed

        self.base_stun_dur = stun_dur
        self.perm_stun_dur = stun_dur
        self.stun_dur = stun_dur

        self.base_slow_eff = slow_eff
        self.perm_slow_eff = slow_eff
        self.slow_eff = slow_eff
        self.base_slow_dur = slow_dur
        self.perm_slow_dur = slow_dur
        self.slow_dur = slow_dur

        # Buffs / Debuffs
        self.speed_buff = speed_buff
        self.speed_buff_dur = speed_buff_dur

        self.speed_dur_buff = speed_dur_buff
        self.speed_dur_buff_dur = speed_dur_buff_dur

        self.dmg_buff = dmg_buff
        self.dmg_buff_dur = dmg_buff_dur

        self.push_buff = push_buff
        self.push_buff_dur = push_buff_dur
        
        self.stun_buff = stun_buff
        self.stun_buff_dur = stun_buff_dur

        self.reset_cd = reset_cd

    def __copy__(self):
        return Effect(
            type=self.type, detect_range=self.detect_range,
            dmg=self.dmg, push_speed=self.push_speed, stun_dur=self.stun_dur,
            slow_eff=self.slow_eff, slow_dur=self.slow_dur,
            speed_buff=self.speed_buff, speed_buff_dur=self.speed_buff_dur,
            dmg_buff=self.dmg_buff, dmg_buff_dur=self.dmg_buff_dur,
            push_buff=self.push_buff, push_buff_dur=self.push_buff_dur,
            stun_buff=self.stun_buff, stun_buff_dur=self.stun_buff_dur)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, images, speed, range, radius, detect_range=0, detect_rect=None, degree=None,
                 parent=None,
                 target_type=None, target_coord=None, target_object=None,
                 effect=None, explosion_eff=None, explosion_radius=0, max_targets=1):
        super().__init__()
        self.creation_time = time.time()
        self.type = 'Projectile'
        self.parent = parent

        # Images
        self.img_timer = time.time()
        self.fps = 1
        self.images = images
        self.image_idx = 0
        self.image_count = len(self.images) - 1
        self.image = self.images[0].copy()
        self.rect = self.image.get_rect()
        self.coord = self.rect.center

        # Stats
        self.target_type = target_type  # 'Enemy', 'Trap Area'
        self.max_targets = max_targets
        self.speed = speed
        self.direction = None
        self.range = range  # ezt elérve végrehajtja az explosion effectet ha van, majd törli magát
        self.detect_range = detect_range
        self.detect_rect = detect_rect

        # Effect
        self.effect = effect
        self.radius = radius
        self.degree = degree

        # Explosion effect
        self.explosion_eff = explosion_eff
        self.explosion_radius = explosion_radius

    def __copy__(self):
        return Projectile(self.images, self.speed, self.range, self.radius,
            parent=self.parent,
            effect=self.effect.__copy__(), explosion_eff=self.explosion_eff,
            max_targets=self.max_targets, explosion_radius=self.explosion_radius)

    def update(self, game_objects, dt):
        self_kill = False
        if self.max_targets == 0:
            self_kill = True
        elif self.range <= 0:
            self_kill = True
        # fallal ütközés, vagy max range elérése esetén is self_kill

        if self_kill:
            if self.explosion_radius:
                for enemy in game_objects.enemies_group:
                    distance = abs(complex(*self.rect.center) - complex(*enemy.rect.center))
                    if self.explosion_radius + enemy.radius >= distance:
                        self.parent.dmg_counter += enemy.hit(self.degree, self.explosion_eff)
            self.kill()
            return

        saved_coord = self.coord
        self.coord = move_object(self.coord, self.speed, dt, direction=self.direction)
        self.rect.center = int(self.coord[0]), int(self.coord[1])
        self.range -= abs(complex(*saved_coord) - complex(*self.coord))

        for enemy in game_objects.enemies_group:
            if pygame.sprite.collide_circle(self, enemy):
                if self not in enemy.immune_to_group:
                    self.max_targets -= 1
                    self.parent.dmg_counter += enemy.hit(self.degree, self.effect)
                    enemy.immune_to_group.add(self)

    def draw(self, SCREEN, base_scroll):
        if base_scroll[0] - self.rect.width < self.rect.x < base_scroll[0] + client_data.width \
                and base_scroll[1] - self.rect.height < self.rect.y < base_scroll[1] + client_data.height:
            SCREEN.blit(self.image, (self.rect.x - base_scroll[0], self.rect.y - base_scroll[1]))


cannonball = Projectile(
    cannonball_pics, speed=200, detect_range=300, range=300, effect=Effect(dmg=1), radius=15, target_type='Trap Area',
    max_targets=math.inf, explosion_radius=40, explosion_eff=Effect(dmg=1))

arrow = Projectile(
    cannonball_pics, speed=200, detect_range=200, range=300, effect=Effect(type='Projectile', dmg=1), radius=1, target_type='Trap Area')
bullet = Projectile(
    cannonball_pics, speed=400, detect_range=400, range=600, effect=Effect(type='Projectile', dmg=3), radius=1, target_type='Trap Area')
catapult_shot = Projectile(
    cannonball_pics, speed=100, detect_range=300, range=300, effect=Effect(type='Projectile', dmg=3), radius=15, target_type='Trap Area',
    explosion_radius=40, explosion_eff=Effect(dmg=3))
glue = Projectile(
    cannonball_pics, speed=200, detect_range=200, range=200, effect=Effect(type='Projectile', slow_eff=0.5, slow_dur=10), radius=15, target_type='Trap Area')


spike_trap = Effect(
    dmg=3)
grinder = Effect(
    dmg=1, detect_range=30, stun_dur=0.1)
snow_blower = Effect(
    detect_range=150, slow_eff=30, slow_dur=3)
wall_blades = Effect(
    dmg=10, detect_range=50)
push_trap = Effect(
    dmg=1, detect_range=50, push_speed=200, stun_dur=0.5)  # ellenfeleknek kéne push resistance
air_went = Effect(
    push_speed=100, detect_range=100)
taunt = Effect()

#    Tesla Coil - stun
    # Tesla Coilnál lehetne hogy vlm szélesség alapján 2 párhuzamos intersect check.
    # A intersect check returnben kéne megadja hogy mikkel ütközött.
    # Ez által ki lehetne küszöbölni hogy valakit kétszer találjon el, továbbá saját magát is kiszedhetné.
# elmélet:
# lehet kéne az effect-be egy type
# a type lehetne Single, vagy AOE
#
# lightning = Effect(type='Single', dmg=1, detect_radius=100, stun_dur=0.1)

captain_cook_basic_attack = Skill('Basic Attack', question_mark, cd=1, range=40, target_type='Single Target', effect=Effect(type='Skill Effect', dmg=1))
fatty_basic_attack = Skill('Basic Attack', question_mark, cd=1, range=40, target_type='Single Target', effect=Effect(type='Skill Effect', dmg=1))
flower_sniffer_basic_attack = Skill('Basic Attack', question_mark, cd=1, range=40, target_type='Single Target', effect=Effect(type='Skill Effect', dmg=1))
master_mindcrack_basic_attack = Skill(
    'Basic Attack', question_mark, cd=1, range=200, target_type='Single Target',
    projectile=Projectile(
        cannonball_pics, speed=200, detect_range=400, range=400,
        effect=Effect(dmg=5), explosion_radius=40, explosion_eff=Effect(dmg=10),
        radius=15, target_type='Enemy'))
hammer_head_basic_attack = Skill('Basic Attack', question_mark, cd=1, range=40, target_type='Single Target', effect=Effect(type='Skill Effect', dmg=1))
stinky_basic_attack = Skill('Basic Attack', question_mark, cd=1, range=40, target_type='Single Target', effect=Effect(type='Skill Effect', dmg=1))

goblin_basic_attack = Skill('Basic Attack', question_mark, cd=1, range=40, target_type='Single Target', effect=Effect(type='Enemy Effect', dmg=1))
ogre_basic_attack = Skill('Basic Attack', question_mark, cd=3, range=60, target_type='Single Target', effect=Effect(type='Enemy Effect', dmg=10, stun_dur=1))

tazer_attack = Skill('Tazer', question_mark, cd=5, range=40, target_type='Single Target', effect=Effect(type='Skill Effect', dmg=5, stun_dur=1))
energize = Skill('Energize', question_mark, cd=5, radius=200, target_type='Self', effect=Effect(type='Trap Buff', reset_cd=True))
maniacal_laugh = Skill('Maniacal laugh', question_mark, cd=5, radius=200, target_type='Self', effect=Effect(type='Skill Effect', stun_dur=3))


goblin = Enemy(
    race='Goblin',
    images=goblin_pics,
    radius=15,
    hp=10,
    speed=80,
    battle_skills=[goblin_basic_attack],
    xp=30,
    loot_code=1,
    time_val=2)

ogre = Enemy(
    race='Ogre',
    images=ogre_pics,
    radius=15,
    hp=20,
    speed=50,
    battle_skills=[ogre_basic_attack],
    xp=200,
    loot_code=1,
    time_val=5)

easy_enemy_teams_dict = {
    1: ([goblin, goblin, ogre],
        [goblin, goblin, ogre]),

    2: ([goblin, goblin, ogre],
        [goblin, ogre, ogre]),

    3: ([goblin, goblin, ogre],
        [ogre, ogre, ogre])}