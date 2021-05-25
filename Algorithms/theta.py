import math
import numpy as np

# https://en.wikipedia.org/wiki/Theta*
# http://vodacek.zvb.cz/archiv/530.html
# https://scholar.uwindsor.ca/cgi/viewcontent.cgi?article=6653&context=etd


class Node:
    def __init__(self, position: (), parent_pos: (), g=0, h=0, f=0):
        self.position = position
        self.parent_pos = parent_pos  # ez nem node, hanem csak koordináta
        self.g = g  # Distance to start node
        self.h = h  # Distance to target node
        self.f = f  # Total cost

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    # Sort nodes
    def __lt__(self, other):
        return self.f < other.f


def theta(matrix_dict, matrix_size, start_coord, target_coord):
    matrix_width, matrix_height = matrix_size
    open_list = []
    closed_list = []
    heuristic_dis = np.linalg.norm(np.array(target_coord) - np.array(start_coord), axis=0)

    start_node = Node(start_coord, start_coord, h=heuristic_dis)
    target_node = Node(target_coord, None)

    open_list.append(start_node)
    temp_dict = {}

    while len(open_list) > 0:
        current_node = open_list.pop()
        temp_dict[current_node.position] = current_node

        if current_node == target_node:
            return reconstruct_path(current_node, temp_dict)
        closed_list.append(current_node)

        x, y = current_node.position
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        for next_coord in neighbors:
            x, y = next_coord
            if x not in range(0, matrix_width) \
                    or y not in range(0, matrix_height) \
                    or matrix_dict[next_coord] == 'B':
                continue

            neighbor_node = Node(next_coord, current_node)

            if neighbor_node not in closed_list:
                if neighbor_node not in open_list:
                    neighbor_node.g = math.inf
                    neighbor_node.parent_pos = None
                update_vertex(matrix_dict, temp_dict, open_list, current_node, neighbor_node, target_coord)
    return None


def update_vertex(matrix_dict, temp_dict, open_list, current_node, neighbor_node, target_coord):
    g_old = neighbor_node.g
    compute_cost(matrix_dict, temp_dict, current_node, neighbor_node)
    if neighbor_node.g < g_old:
        neighbor_node.h = np.linalg.norm(np.array(target_coord) - np.array(neighbor_node.position), axis=0)
        neighbor_node.f = neighbor_node.g + neighbor_node.h
        if neighbor_node not in open_list:
            open_list.append(neighbor_node)


def compute_cost(matrix_dict, temp_dict, current_node, neighbor_node):
    if line_of_sight(matrix_dict, current_node.parent_pos, neighbor_node.position):
        euc_dis = np.linalg.norm(np.array(current_node.parent_pos) - np.array(neighbor_node.position), axis=0)
        if temp_dict[current_node.parent_pos].g + euc_dis < neighbor_node.g:
            neighbor_node.parent_pos = current_node.parent_pos
            neighbor_node.g = temp_dict[current_node.parent_pos].g + euc_dis
    else:
        euc_dis = np.linalg.norm(np.array(current_node.position) - np.array(neighbor_node.position), axis=0)
        if current_node.g + euc_dis < neighbor_node.g:
            neighbor_node.parent_pos = current_node.position
            neighbor_node.g = current_node.g + euc_dis


def reconstruct_path(node, temp_dict):
    path = []
    while node.position != node.parent_pos:
        path.append(node.position)
        node = temp_dict[node.parent_pos]
    return path


def line_of_sight(matrix_dict, coord1, coord2):
    x0, y0 = coord1
    x1, y1 = coord2
    sx = sy = -1
    if x0 < x1:
        sx = 1
    if y0 < y1:
        sy = 1
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    err = dx + dy

    while True:
        if matrix_dict[(x0, y0)] == 'B':
            return False
        elif (x0, y0) == (x1, y1):
            return True
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


test_matrix_dict = {
    (0, 0): '.',
    (0, 1): '.',
    (0, 2): '.',
    (0, 3): '.',
    (1, 0): '.',
    (1, 1): '.',
    (1, 2): '.',
    (1, 3): '.',
    (2, 0): '.',
    (2, 1): 'B',
    (2, 2): 'B',
    (2, 3): 'B',
    (3, 0): '.',
    (3, 1): '.',
    (3, 2): '.',
    (3, 3): '.',
}

matrix_size = (4, 4)
print(theta(test_matrix_dict, matrix_size, (1, 2), (3, 3)))