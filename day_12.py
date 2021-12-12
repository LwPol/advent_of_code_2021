START = 'start'
END = 'end'


class GraphNode:
    def __init__(self, value):
        self.value = value
        self.connected = set()


    def add_neighbour(self, neighbour):
        self.connected.add(neighbour)


def add_graph_connection(graph, source, destination):
    if source in graph:
        graph[source].add_neighbour(destination)
    else:
        newNode = GraphNode(source)
        newNode.add_neighbour(destination)
        graph[source] = newNode


def add_two_way_connection_to_graph(graph, nodeA, nodeB):
    add_graph_connection(graph, nodeA, nodeB)
    add_graph_connection(graph, nodeB, nodeA)


def parse_caves_graph(input):
    graph = {}
    for connection in input:
        nodes = connection.split('-')
        add_two_way_connection_to_graph(graph, *nodes)
    return graph


def is_small_cave(cave):
    return cave.lower() == cave


class PathTraverserA:
    def __init__(self, other=None):
        self.path = list(other.path) if other is not None else []


    def is_cave_nonvisitable(self, cave):
        return is_small_cave(cave) and cave in self.path


    def extend_path(self, cave):
        self.path.append(cave)


class PathTraverserB:
    def __init__(self, other=None):
        self.path = list(other.path) if other is not None else []
        self._small_cave_visited_twice = other is not None and other._small_cave_visited_twice


    def is_cave_nonvisitable(self, cave):
        if cave == START:
            return True
        if is_small_cave(cave) and cave in self.path:
            return self._small_cave_visited_twice
        return False


    def extend_path(self, cave):
        if is_small_cave(cave) and cave in self.path:
            self._small_cave_visited_twice = True
        self.path.append(cave)


def count_all_path_continuations(graph, path_traverser):
    traverser_type = type(path_traverser)
    current_cave = path_traverser.path[-1]
    current_node = graph[current_cave]
    path_continuations = 0
    for cave in current_node.connected:
        if path_traverser.is_cave_nonvisitable(cave):
            continue
        if cave == END:
            path_continuations += 1
        else:
            new_path = traverser_type(path_traverser)
            new_path.extend_path(cave)
            path_continuations += count_all_path_continuations(graph, new_path)
    return path_continuations


def count_all_possible_paths(graph, traverser_type):
    start = traverser_type()
    start.extend_path(START)
    return count_all_path_continuations(graph, start)


def resolve_part1(input):
    return count_all_possible_paths(parse_caves_graph(input), PathTraverserA)


def resolve_part2(input):
    return count_all_possible_paths(parse_caves_graph(input), PathTraverserB)