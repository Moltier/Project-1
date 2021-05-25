import math
import numpy as np
from engine import intersect, get_matrix_coord
from spec_functions import cp

# https://en.wikipedia.org/wiki/Theta*
# http://vodacek.zvb.cz/archiv/530.html
# https://scholar.uwindsor.ca/cgi/viewcontent.cgi?article=6653&context=etd

class Matrix:
    def __init__(self, matrix_dict, width, height, node_size):
        self.dict = matrix_dict
        self.width = width
        self.height = height
        self.node_size = node_size
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


def lazytheta(matrix, start_coord, obj_radius, target_coord):
    matrix.open_list = []
    matrix.closed_dict = {}
    start_node_coord = get_matrix_coord(start_coord, matrix.node_size)
    euc_dis = np.linalg.norm(np.array(target_coord) - np.array(start_coord), axis=0)
    start_node = Node(start_node_coord, start_node_coord, h=euc_dis)
    matrix.open_list.append(start_node)
    new_parent = True

    while len(matrix.open_list) > 0:
        matrix.open_list.sort(key=lambda x: x.h, reverse=True)
        current_node = matrix.open_list.pop()  # another option: del min of open_list based on .h

        if new_parent:
            parent_coord = current_node.parent_pos
            if current_node.parent_pos != start_node.parent_pos:
                parent_coord = (current_node.parent_pos[0] + matrix.node_size / 2, current_node.parent_pos[1] + matrix.node_size / 2)
            if line_of_sight(matrix, parent_coord, target_coord):
                matrix.closed_dict[current_node.position] = current_node
                return construct_path(target_coord, current_node, matrix.closed_dict, matrix.node_size)

        new_parent = set_vertex(current_node, matrix)

        matrix.closed_dict[current_node.position] = current_node
        x, y = current_node.position

        neighbor_coords = [
            (x - 1 * matrix.node_size, y),
            (x + 1 * matrix.node_size, y),
            (x, y - 1 * matrix.node_size),
            (x, y + 1 * matrix.node_size)]

        for i, next_coord in enumerate(neighbor_coords):
            x, y = next_coord
            if x not in range(0, matrix.width) \
                    or y not in range(0, matrix.height) \
                    or matrix.dict[next_coord]['Blocker'] == True:
                continue

            neighbor_node = Node(next_coord, current_node.position)
            if neighbor_node not in matrix.closed_dict.values():
                if neighbor_node not in matrix.open_list:
                    neighbor_node.g = math.inf
                    neighbor_node.parent_pos = None
                update_vertex(matrix, current_node, neighbor_node, target_coord)
    cp(465, 'No route!')
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


def set_vertex(current_node, matrix):
    current_node_center = (current_node.position[0] + matrix.node_size, current_node.position[1] + matrix.node_size)
    if not line_of_sight(matrix, current_node_center, current_node.parent_pos):
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
        return True


def construct_path(target_node, current_node, closed_dict, node_size):
    path = [target_node]
    while current_node.position != current_node.parent_pos:
        path.append((int(current_node.position[0] + node_size / 2), int(current_node.position[1] + node_size / 2)))
        current_node = closed_dict[current_node.parent_pos]
    return path
