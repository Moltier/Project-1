class Node:
    def __init__(self, position: (), parent: ()):
        self.position = position
        self.parent = parent
        self.g = 0  # Distance to start node
        self.h = 0  # Distance to goal node
        self.f = 0  # Total cost

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    # Sort nodes
    def __lt__(self, other):
        return self.f < other.f


# http://www.jcomputers.us/vol13/jcp1305-05.pdf
# http://www.diva-portal.org/smash/get/diva2:1111201/FULLTEXT01.pdf
# Navigation Mesh (NavMesh) + A*
def astar_search(map, start, target):
    target = (int(target[0]), int(target[1]))
    open_list = []
    closed = []

    start_node = Node(start, None)
    goal_node = Node(target, None)

    open_list.append(start_node)

    while len(open_list) > 0:
        open_list.sort()
        current_node = open_list.pop(0)

        # Check if we have reached the goal, return the path
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        closed.append(current_node)

        x, y = current_node.position
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        for next in neighbors:
            map_value = map.get(next)
            # Check if the node is a wall
            if map_value == 'B':
                continue
            # Create a neighbor node
            neighbor = Node(next, current_node)
            # Check if the neighbor is in the closed list
            if neighbor in closed:
                continue

            # Generate heuristics (Manhattan distance)
            neighbor.g = abs(neighbor.position[0] - start_node.position[0]) + abs(
                neighbor.position[1] - start_node.position[1])
            neighbor.h = abs(neighbor.position[0] - goal_node.position[0]) + abs(
                neighbor.position[1] - goal_node.position[1])
            neighbor.f = neighbor.g + neighbor.h

            # Check if neighbor is in open_list list and if it has a lower f value
            if add_to_open(open_list, neighbor):
                # Everything is green, add neighbor to open_list list
                open_list.append(neighbor)
    return None


# Check if a neighbor should be added to open_list list
def add_to_open(open_list, neighbor):
    for node in open_list:
        if neighbor == node and neighbor.f >= node.f:
            return False
    return True
