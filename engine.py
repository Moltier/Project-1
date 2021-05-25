import math, pygame, time
from spec_functions import cp


# def camera_scrolling():

# def new_order(client_data, game_data, player_id, target_coord):  # ez biztos nem a Character classba kéne?

def get_cell_coord(coord, cell_size):
    return (math.floor(coord[0] / cell_size),
            math.floor(coord[1] / cell_size))


def get_matrix_coord(coord, cell_size):
    return (math.floor(coord[0] / cell_size) * cell_size,
            math.floor(coord[1] / cell_size) * cell_size)


class Point:
    def __init__(self, coord):
        self.x, self.y = coord


def intersect(p0, p1, lines):
    # https://www.youtube.com/watch?v=A86COO8KC58&ab_channel=CodingMath

    p0 = Point(p0)
    p1 = Point(p1)
    for (p2, p3) in lines:
        if p2.x >= max(p0.x, p1.x) and p3.x >= max(p0.x, p1.x) \
                or p2.x <= min(p0.x, p1.x) and p3.x <= min(p0.x, p1.x) \
                or p2.y >= max(p0.y, p1.y) and p3.y >= max(p0.y, p1.y) \
                or p2.y <= min(p0.y, p1.y) and p3.y <= min(p0.y, p1.y):
            continue

        a1 = p1.y - p0.y
        b1 = p0.x - p1.x
        c1 = a1 * p0.x + b1 * p0.y
        a2 = p3.y - p2.y
        b2 = p2.x - p3.x
        c2 = a2 * p2.x + b2 * p2.y
        denominator = a1 * b2 - a2 * b1

        if denominator == 0:
            continue
        intersect_x, intersect_y = ((b2 * c1 - b1 * c2) / denominator, (a1 * c2 - a2 * c1) / denominator)

        if intersect_x > max(p2.x, p3.x) \
                or intersect_x < min(p2.x, p3.x) \
                or intersect_y > max(p2.y, p3.y) \
                or intersect_y < min(p2.y, p3.y):
            continue

        if (intersect_x, intersect_y) in [(p0.x, p0.y), (p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)]:
            continue
        return True
    return False


def detect_targets(target_group, starting_coord=None, starting_coord_radius=0,
                   detect_range=None, detect_rect=None, max_targets=None):
    targets_list = []

    if detect_range:
        for target in target_group:
            distance = abs(complex(*starting_coord) - complex(*target.rect.center)) - starting_coord_radius - target.radius
            if distance <= detect_range:
                targets_list.append((target, distance))
        targets_list.sort(key=lambda x: x[1])
        targets_list = [x[0] for x in targets_list]

    elif detect_rect:
        for target in target_group:
            if circle_rect_collide(target.rect.center, target.radius, detect_rect):
                targets_list.append(target)
        # rectange detection is not supposed to have range, so no sorting

    if max_targets:
        targets_list = targets_list[:max_targets]
    return targets_list


def char_collision(player_hitbox, oth_char_hitboxes):
    for hitbox in oth_char_hitboxes:
        if player_hitbox.colliderect(hitbox):
            return True
    return False


class CustomError(Exception):
    pass


def get_direction(first_coord=None, second_coord=None, degree=None):
    if not first_coord:
        if first_coord or second_coord:
            raise CustomError("Shouldnt have both coordinates and a degree.")
        radians = math.radians(degree)
        return math.cos(radians), math.sin(radians)
    else:
        radians = math.atan2(second_coord[1] - first_coord[1],
                             second_coord[0] - first_coord[0])
        return math.cos(radians), math.sin(radians)


def get_radians(first_coord, target_coord):
    radians = math.atan2(target_coord[1] - first_coord[1],
                         target_coord[0] - first_coord[0])
    return radians


def circle_rect_collide(circle_coord, radius, rect):
    distance = abs(complex(*circle_coord) - complex(*rect.center))
    if distance < radius:
        return True

    direction = get_direction(first_coord=circle_coord, second_coord=rect.center)
    circle_edge_coord = (int(direction[0] * radius + circle_coord[0]),
                         int(direction[1] * radius + circle_coord[1]))
    return rect.collidepoint(circle_edge_coord)


def find_path(start_coord, target_coord, game_objects):
    if not intersect(start_coord, target_coord, game_objects.blocker_lines):
        return [(target_coord, 'C')]

    start_waypoints_dict = {}
    target_waypoints_dict = {}

    start_time = time.time()

    for waypoint, dir in game_objects.waypoints_dict.items():
        if not intersect(start_coord, waypoint, game_objects.blocker_lines):
            start_waypoints_dict[waypoint] = dir
        if not intersect(target_coord, waypoint, game_objects.blocker_lines):
            target_waypoints_dict[waypoint] = dir

    cp(621, "Finding neighbor waypoints in:", time.time() - start_time)
    print()

    shortest_path = []
    shortest_path_len = math.inf
    for start_waypoint, start_dir in start_waypoints_dict.items():
        dist1 = abs(complex(*start_coord) - complex(*start_waypoint))
        for target_waypoint, target_dir in target_waypoints_dict.items():
            path = []
            path_len = None
            dist2 = abs(complex(*target_coord) - complex(*target_waypoint))
            endpoint_distances = dist1 + dist2
            if start_waypoint == target_waypoint:
                path = [(start_waypoint, game_objects.waypoints_dict[start_waypoint])]
                path_len = endpoint_distances
            elif game_objects.waypoint_paths_dict[(start_waypoint, target_waypoint)][0] > shortest_path_len:
                continue
            else:
                path_data = game_objects.waypoint_paths_dict[(start_waypoint, target_waypoint)]
                path = path_data[1]
                path_len = endpoint_distances + path_data[0]

            if path_len < shortest_path_len:
                shortest_path_len = path_len
                shortest_path = list(path)
                shortest_path.append((target_coord, 'C'))

    return shortest_path


def follow_path(character, game_data, game_objects):
    time_to_act = game_data.time_to_act
    saved_coord = character.coord
    target_coord, dir = list(character.path[0])

    coord = None
    if dir == 'C':
        coord = list(character.rect.center)
    elif dir == 'TL':
        coord = list(character.rect.bottomright)
    elif dir == 'TR':
        coord = list(character.rect.bottomleft)
    elif dir == 'BL':
        coord = list(character.rect.topright)
    elif dir == 'BR':
        coord = list(character.rect.topleft)

    correction = (character.coord[0] - character.rect.center[0], character.coord[1] - character.rect.center[1])
    coord[0] += correction[0]
    coord[1] += correction[1]

    target_dist = abs(complex(*coord) - complex(*target_coord))
    dir_x, dir_y = get_direction(first_coord=coord, second_coord=target_coord)
    full_dir_x, full_dir_y = (dir_x * character.speed * time_to_act, dir_y * character.speed * time_to_act)
    new_coord = [coord[0] + full_dir_x, coord[1] + full_dir_y]

    remove_path = False
    if target_dist < abs(complex(*coord) - complex(*new_coord)):
        act_dir_x = coord[0] - target_coord[0]
        time_used = abs(act_dir_x / dir_x / character.speed)
        time_to_act -= time_used

        coord = target_coord
        remove_path = True
    else:
        coord = new_coord

    # apply new coord
    if dir == 'C':
        character.rect.center = character.coord = coord
    elif dir == 'TL':
        character.rect.bottomright = coord
        character.coord = (coord[0] - (character.rect.w / 2), coord[1] - (character.rect.h / 2))
    elif dir == 'TR':
        character.rect.bottomleft = coord
        character.coord = (coord[0] + (character.rect.w / 2), coord[1] - (character.rect.h / 2))
    elif dir == 'BL':
        character.rect.topright = coord
        character.coord = (coord[0] - (character.rect.w / 2), coord[1] + (character.rect.h / 2))
    elif dir == 'BR':
        character.rect.topleft = coord
        character.coord = (coord[0] + (character.rect.w / 2), coord[1] + (character.rect.h / 2))

    collision_object = collision_check(character, game_objects)

    if collision_object:
        character.coord = saved_coord
        character.rect.center = saved_coord
        coll_dir_x, coll_dir_y = get_direction(
            first_coord=character.rect.center, second_coord=collision_object.rect.center)
        fixed_coord = None
        target_dist = math.inf

        if collision_object.radius:  # ha circle object
            coll_radians = math.atan2(
                collision_object.rect.x - character.rect.x,
                collision_object.rect.y - character.rect.y)  # ha 0,0 a kezdő, megadja radiansban
            coll_degree = math.degrees(coll_radians)
            arc_length = abs(complex(*new_coord) - complex(*character.coord))
            radius = abs(complex(*character.coord) - complex(*collision_object.rect.center))
            radians = arc_length / radius
            degree = math.degrees(radians)

            for mlt in (1, -1):
                radians = math.radians(coll_degree)
                x = radius * math.cos(radians)
                y = radius * math.sin(radians)
                new_coord = x + collision_object.rect.x, y + collision_object.rect.y
                distance = abs(complex(*new_coord) - complex(*target_coord))
                if distance < target_dist:
                    target_dist = distance
                    fixed_coord = new_coord

        else:  # ha rect object
            if coll_dir_x < 0:
                coll_dir_x = -1
            else:
                coll_dir_x = 1
            if coll_dir_y < 0:
                coll_dir_y = -1
            else:
                coll_dir_y = 1
            coll_directions = ((coll_dir_x, 0),(0, coll_dir_y))
            gen_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for dir in coll_directions:
                gen_directions.remove(dir)

            temp_dir_save = None
            for dir in gen_directions:
                full_dir_x, full_dir_y = (dir[0] * character.speed * time_to_act, dir[1])
                new_coord = [character.coord[0] + full_dir_x, character.coord[1] + full_dir_y]
                distance = abs(complex(*new_coord) - complex(*target_coord))
                if distance < target_dist:
                    target_dist = distance
                    fixed_coord = new_coord
                    temp_dir_save = dir

        character.coord = fixed_coord
        character.rect.center = fixed_coord

        # collision check
        collision_object = collision_check(character, game_objects)
        if collision_object:
            character.coord = saved_coord
            character.rect.center = saved_coord

    elif remove_path:
        character.path.pop(0)
    return


def collision_check(character, game_objects):
    collision_object = None

    for blocker in game_objects.blocker_group:
        if circle_rect_collide(character.rect.center, character.radius, blocker.rect):
            collision_object = blocker
            break
    if not collision_object:
        for enemy in game_objects.enemies_group:
            if enemy != character:
                if pygame.sprite.collide_circle(character, enemy):
                    collision_object = enemy
                    break

    return collision_object


def move_object(starting_coord, speed, dt, direction=None):
    """ Simple move func, towards a direction. """
    dir_x, dir_y = direction
    full_dir_x, full_dir_y = (dir_x * speed * dt, dir_y * speed * dt)
    return_coord = [starting_coord[0] + full_dir_x, starting_coord[1] + full_dir_y]

    return return_coord


# def countPoints(points, circles):
#     # https://leetcode.com/problems/queries-on-number-of-points-inside-a-circle/discuss/1167044/Python-3-512-ms-faster-than-100-using-complex-numbers
#     points = list(map(complex, *zip(*points)))
#     circles = ((complex(x, y), radius) for x, y, radius in circles)  # ez miért lesz generator object?
#     return [sum(abs(point - circle_coord) <= radius for point in points) for circle_coord, radius in circles]


def get_distance(starting_coord, target_coord):
    return abs(complex(*target_coord) - complex(*starting_coord))


# def calc_distance(first_coord, second_coord):  # slightly slower than get_distance
#     return int(math.hypot(second_coord[0] - first_coord[0], second_coord[1] - first_coord[1]))
