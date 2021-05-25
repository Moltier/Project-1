import math
import numpy as np
from spec_functions import cp

# https://en.wikipedia.org/wiki/Theta*
# http://vodacek.zvb.cz/archiv/530.html
# https://scholar.uwindsor.ca/cgi/viewcontent.cgi?article=6653&context=etd

class Matrix:
    def __init__(self, matrix_dict, width, height):
        self.dict = matrix_dict
        self.width = width
        self.height = height
        self.open_list = []
        self.closed_dict = {}


class Node:
    def __init__(self, position: (), parent_pos: (), g=0, h=0):
        self.position = position
        self.parent_pos = parent_pos
        self.g = g  # Distance to start node
        self.h = h  # Distance to target node
        self.f = self.g + self.h  # Total cost

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    # Sort nodes
    def __lt__(self, other):
        return self.f < other.f


def lazytheta(matrix, start_coord, target_coord):
    matrix.open_list = []
    matrix.closed_dict = {}
    euc_dis = np.linalg.norm(np.array(target_coord) - np.array(start_coord), axis=0)
    matrix.open_list.append(Node(start_coord, start_coord, h=euc_dis))

    cp(23, start_coord, target_coord)
    while len(matrix.open_list) > 0:
        matrix.open_list.sort(key=lambda x: x.h, reverse=True)
        current_node = matrix.open_list.pop()  # another option: del min of open_list based on .h

        # ki tudnám kalkulálni a target coordnak megfelelő matrix key-t
        # amit scannelnék, és ha találat van (tehát az utolsó lépés),
        # akkor kicseréli a normál targetre.
        # Viszont ekkkor még kéne egy lineofsight check erre (ami elvileg amúgy is futna?)

        set_vertex(current_node, matrix, matrix.dict)

        if current_node.position == target_coord:
            return construct_path(current_node, matrix.closed_dict)

        matrix.closed_dict[current_node.position] = current_node
        x, y = current_node.position
        neighbor_coords = [
            (x - 1 * matrix.node_size, y),
            (x + 1 * matrix.node_size, y),
            (x, y - 1 * matrix.node_size),
            (x, y + 1 * matrix.node_size)]

        for next_coord in neighbor_coords:
            x, y = next_coord
            if x not in range(0, matrix.width) \
                    or y not in range(0, matrix.height) \
                    or matrix.dict[next_coord] == 'B':
                continue

            neighbor_node = Node(next_coord, current_node.position)
            if neighbor_node not in matrix.closed_dict.values():
                if neighbor_node not in matrix.open_list:
                    neighbor_node.g = math.inf
                    neighbor_node.parent_pos = None
                update_vertex(matrix, current_node, neighbor_node, target_coord)
    return None


def update_vertex(matrix, current_node, neighbor_node, target_coord):
    g_old = neighbor_node.g
    compute_cost(matrix.closed_dict, current_node, neighbor_node)
    if neighbor_node.g < g_old:
        neighbor_node.h = np.linalg.norm(np.array(target_coord) - np.array(neighbor_node.position), axis=0)
        neighbor_node.f = neighbor_node.g + neighbor_node.h
        if neighbor_node not in matrix.open_list:
            matrix.open_list.append(neighbor_node)


def compute_cost(closed_dict, current_node, neighbor_node):
    euc_dis = np.linalg.norm(np.array(current_node.parent_pos) - np.array(neighbor_node.position), axis=0)
    if closed_dict[current_node.parent_pos].g + euc_dis < neighbor_node.g:
        neighbor_node.parent_pos = current_node.parent_pos
        neighbor_node.g = closed_dict[current_node.parent_pos].g + euc_dis


def set_vertex(current_node, matrix, matrix_dict):
    if not line_of_sight(matrix_dict, current_node.position, current_node.parent_pos):
        # itt derül ki hogy a korábbi current_node.parent_pos már nem jó.
        # emiatt meg kell nézni a current_node szomszédjait, amik már scannelve voltak,
        # és közülük kiválasztani azt, amelyik a most nem jó parent_pos-al rendelkezik,
        # plusz a legközelebb van ehhez a parent_pos-hoz.
        # ennek a kiválasztott szomszédnak a kordinátája lesz a current_node.parent_pos.

        best_node_coord = None
        shortest_path = math.inf
        x, y = current_node.position
        neighbor_coords = [
            (x - 1 * matrix.node_size, y),
            (x + 1 * matrix.node_size, y),
            (x, y - 1 * matrix.node_size),
            (x, y + 1 * matrix.node_size)]

        for coord in neighbor_coords:
            if coord in matrix.closed_dict.keys():  # already scanned coords
                euc_dis1 = np.linalg.norm(np.array(coord) - np.array(matrix.closed_dict[coord].parent_pos), axis=0)
                euc_dis2 = np.linalg.norm(np.array(coord) - np.array(current_node.position), axis=0)
                if euc_dis1 + euc_dis2 < shortest_path:
                    best_node_coord = coord
                    shortest_path = euc_dis1 + euc_dis2

        current_node.parent_pos = best_node_coord
        current_node.g = shortest_path


def construct_path(node, closed_dict):
    path = []
    while node.position != node.parent_pos:
        path.append(node.position)
        node = closed_dict[node.parent_pos]
    return path


def line_of_sight(matrix_dict, coord1, coord2):
    # itt lehet bele kéne kalkulálni valahogy hogy a node-oknak van mérete (node_size)
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


# test_matrix_dict3 = {
#     (0, 0): '.',
#     (0, 1): '.',
#     (0, 2): '.',
#     (0, 3): '.',
#     (0, 4): '.',
#     (0, 5): '.',
#     (1, 0): '.',
#     (1, 1): '.',
#     (1, 2): '.',
#     (1, 3): 'B',
#     (1, 4): '.',
#     (1, 5): '.',
#     (2, 0): '.',
#     (2, 1): '.',
#     (2, 2): '.',
#     (2, 3): 'B',
#     (2, 4): 'B',
#     (2, 5): 'B',
#     (3, 0): '.',
#     (3, 1): '.',
#     (3, 2): '.',
#     (3, 3): '.',
#     (3, 4): '.',
#     (3, 5): '.',
#     (4, 0): '.',
#     (4, 1): '.',
#     (4, 2): '.',
#     (4, 3): '.',
#     (4, 4): '.',
#     (4, 5): '.',
#     (5, 0): '.',
#     (5, 1): '.',
#     (5, 2): '.',
#     (5, 3): '.',
#     (5, 4): '.',
#     (5, 5): '.',
# }
#
# matrix = Matrix(test_matrix_dict3, 6, 6)
# print(lazytheta(matrix, (3, 3), (1, 4)))