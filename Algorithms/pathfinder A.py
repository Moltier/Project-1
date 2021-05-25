import sys, time
from Algorithms.a_star import astar_search
from spec_functions import cp

display_size = (200, 200)
grid_size = (20, 20)

starting_pos = (2, 2)
matrix_dict = {}
for x in range(grid_size[0]):
    for y in range(grid_size[1]):
        matrix_dict[(x * 10, y * 10)] = None

# https://www.annytab.com/a-star-search-algorithm-in-python/
# https://www.youtube.com/watch?v=nhiFx28e7JY&list=PLFt_AvWsXl0cq5Umv3pMC9SPnKjfp9eGW&index=2&ab_channel=SebastianLague

#
# class Node:
#     def __init__(self, position: (), parent: ()):
#         self.position = position
#         self.parent = parent
#         self.g = 0  # Distance to start node
#         self.h = 0  # Distance to goal node
#         self.f = 0  # Total cost
#
#     # Compare nodes
#     def __eq__(self, other):
#         return self.position == other.position
#
#     # Sort nodes
#     def __lt__(self, other):
#         return self.f < other.f
#
#     # Print node
#     def __repr__(self):
#         return ('({0},{1})'.format(self.position, self.f))


def draw_grid(map, width, height, spacing=2, **kwargs):
    for y in range(height):
        for x in range(width):
            print('%%-%ds' % spacing % draw_tile(map, (x, y), kwargs), end='')
        print()


def draw_tile(map, position, kwargs):
    value = map.get(position)
    # Check if we should print the path
    if 'path' in kwargs and position in kwargs['path']:
        value = '+'
    # Check if we should print start point
    if 'start' in kwargs and position == kwargs['start']:
        value = '@'
    # Check if we should print the goal point
    if 'goal' in kwargs and position == kwargs['goal']:
        value = '$'
    return value


# def astar_search(map, start, end):
#     open_list = []
#     closed = []
#
#     start_node = Node(start, None)
#     goal_node = Node(end, None)
#
#     open_list.append(start_node)
#
#     while len(open_list) > 0:
#         open_list.sort()
#         current_node = open_list.pop(0)
#         closed.append(current_node)
#
#         # Check if we have reached the goal, return the path
#         if current_node == goal_node:
#             path = []
#             while current_node != start_node:
#                 path.append(current_node.position)
#                 current_node = current_node.parent
#             # path.append(start)
#             return path[::-1]
#
#         x, y = current_node.position
#
#         neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
#
#         for next in neighbors:
#             map_value = map.get(next)
#             # Check if the node is a wall
#             if map_value == '#':
#                 continue
#             # Create a neighbor node
#             neighbor = Node(next, current_node)
#             # Check if the neighbor is in the closed list
#             if neighbor in closed:
#                 continue
#             # Generate heuristics (Manhattan distance)
#             neighbor.g = abs(neighbor.position[0] - start_node.position[0]) + abs(
#                 neighbor.position[1] - start_node.position[1])
#             neighbor.h = abs(neighbor.position[0] - goal_node.position[0]) + abs(
#                 neighbor.position[1] - goal_node.position[1])
#             neighbor.f = neighbor.g + neighbor.h
#             # Check if neighbor is in open_list list and if it has a lower f value
#             if add_to_open(open_list, neighbor) == True:
#                 # Everything is green, add neighbor to open_list list
#                 open_list.append(neighbor)
#
#     return None


# Check if a neighbor should be added to open_list list
# def add_to_open(open_list, neighbor):
#     for node in open_list:
#         if neighbor == node and neighbor.f >= node.f:
#             return False
#     return True


# The main entry point for this module
def main():
    # Get a map (grid)
    map = {}
    chars = ['c']
    start = None
    end = None
    width = 0
    height = 0
    # Open a file
    fp = open('maze', 'r')

    while len(chars) > 0:
        chars = [str(i) for i in fp.readline().strip()]
        width = len(chars) if width == 0 else width

        for x in range(len(chars)):
            map[(x, height)] = chars[x]
            if chars[x] == '@':
                start = (x, height)
            elif chars[x] == '$':
                end = (x, height)

        if len(chars) > 0:
            height += 1

    fp.close()

    start_time = time.time()
    print('Start')
    path = astar_search(map, start, end)
    print('Finish: ',  time.time() - start_time)
    print()
    print(path)
    print()
    draw_grid(map, width, height, spacing=1, path=path, start=start, goal=end)
    print()
    print('Steps to goal: {0}'.format(len(path)))
    print()


if __name__ == "__main__":
    main()

