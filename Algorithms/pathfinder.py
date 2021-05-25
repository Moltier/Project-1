import pygame, sys, time
from spec_functions import cp

pygame.init()
pygame.font.init()
pygame.display.set_caption("Pathfinder")
clock = pygame.time.Clock()
display_size = (1600, 900)
grid_size = (160, 90)
SCREEN = pygame.display.set_mode(display_size, pygame.HWSURFACE | pygame.DOUBLEBUF)

wall_pics = [
    pygame.transform.scale(pygame.image.load("Pictures/Tiles/wall_pic.png"), (50, 50)).convert()
]

class Object(pygame.sprite.Sprite):
    def __init__(self, obj_imgs, coord):
        super().__init__()
        self.blocker = True
        self.image = obj_imgs[0]
        self.rect = self.image.get_rect(topleft=coord)


wall_group = pygame.sprite.Group(
    Object(wall_pics, (400, 100)),
    Object(wall_pics, (450, 150)),
    Object(wall_pics, (500, 200)),
    Object(wall_pics, (550, 250)),
    Object(wall_pics, (600, 250)),
    Object(wall_pics, (650, 250)),
    Object(wall_pics, (700, 250)),
    Object(wall_pics, (750, 250)),
    Object(wall_pics, (800, 250)),
    Object(wall_pics, (850, 250)),
    Object(wall_pics, (400, 150)),
    Object(wall_pics, (400, 200)),
    Object(wall_pics, (400, 250)),
    Object(wall_pics, (450, 300)),
    Object(wall_pics, (500, 350)),
    Object(wall_pics, (550, 350)),
    Object(wall_pics, (600, 350)),
    Object(wall_pics, (650, 350)),
    Object(wall_pics, (700, 350)),
    Object(wall_pics, (750, 350)),
    Object(wall_pics, (800, 350)),
    Object(wall_pics, (850, 350))
)

target_coord = (0, 0)
spawn_point = (550, 200)

matrix_dict = {}
for x in range(grid_size[0]):
    for y in range(grid_size[1]):
        matrix_dict[(x * 10, y * 10)] = '.'

for obj in wall_group:
    x_rect = obj.rect.x
    y_rect = obj.rect.y
    width = obj.image.get_width()
    height = obj.image.get_height()

    for w in range(0, width, 10):
        x = x_rect + w
        for h in range(0, height, 10):
            y = y_rect + h
            matrix_dict[(x, y)] = 'B'


def floodfill(matrix_dict, x, y):
    matrix_dict[(x, y)] = 0
    coords_set = {(x, y)}
    next_coords_set = set()

    highest_cost = 0
    while len(coords_set) > 0:
        x, y = coords_set.pop()
        cost = matrix_dict[(x, y)] + 1

        for new_coord in [(x + 10, y), (x - 10, y), (x, y + 10), (x, y - 10)]:
            try:
                if not matrix_dict[new_coord] == 'B' and not type(matrix_dict[new_coord]) is int:
                    if cost > highest_cost:
                        highest_cost = cost
                    matrix_dict[new_coord] = cost
                    next_coords_set.add(new_coord)
            except KeyError:
                pass

        if len(coords_set) == 0:
            coords_set = next_coords_set.copy()
            next_coords_set.clear()

    return matrix_dict, highest_cost


start_time = time.time()
print('Start')
matrix_dict, highest_cost = floodfill(matrix_dict, target_coord[0], target_coord[1])
print('Finish: ',  time.time() - start_time)


def draw(SCREEN, div):
    for coord, cost in matrix_dict.items():
        if cost != 'B':
            pygame.draw.rect(SCREEN, (255 - int(cost / div), 0, 0), (coord[0], coord[1], 10, 10))

    pygame.draw.circle(SCREEN, (255, 0, 0), target_coord, 3)
    pygame.draw.circle(SCREEN, (0, 255, 0), spawn_point, 3)

    wall_group.draw(SCREEN)

    pygame.display.update()
div = highest_cost / 255
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    draw(SCREEN, div)
    clock.tick(60)
