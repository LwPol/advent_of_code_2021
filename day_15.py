from typing import Tuple
from day_9 import neighbours_of_point
import heapq
from dataclasses import dataclass


@dataclass
class Node:
    coords: Tuple[int, int]
    value: int
    cost: int
    heuristic_val: int
    

    def __lt__(self, other):
        return self.cost + self.heuristic_val < other.cost + other.heuristic_val


def parse_risk_level_map(input):
    return [[int(num) for num in line] for line in input]


def get_target_point(map):
    width = len(map[0])
    height = len(map)
    return (width - 1, height - 1)


def manhattan_dist(ptA, ptB):
    xa, ya = ptA
    xb, yb = ptB
    return abs(xa - xb) + abs(ya - yb)


def calculate_heuristic(map, point):
    return manhattan_dist(get_target_point(map), point)


class AStarAlgorithm:
    def __init__(self, map):
        self._visited_points = set()
        self._current_node = None
        self._map = map
        self._target = get_target_point(map)


    def find_cost_of_best_path(self):
        nodes = [self._create_starting_node()]
        while not self._is_target_reached(nodes):
            for x, y in neighbours_of_point(self._map, *self._current_node.coords):
                if (x, y) in self._visited_points:
                    continue
                self._update_cost_of_neighbour((x, y), nodes)
            self._visited_points.add(self._current_node.coords)
        return self._current_node.cost
    
    
    def _create_starting_node(self):
        heuristic = calculate_heuristic(self._map, (0, 0))
        node = Node(coords=(0, 0), value=self._map[0][0], cost=0, heuristic_val=heuristic)
        return node
    

    def _is_target_reached(self, nodes):
        self._current_node = heapq.heappop(nodes)
        return self._current_node.coords == self._target
    

    def _update_cost_of_neighbour(self, neighbour, nodes):
        x, y = neighbour
        risk = self._map[y][x]
        indexed_node = next(filter(lambda n: n[1].coords == neighbour, enumerate(nodes)), None)
        evaluated_cost = self._current_node.cost + risk
        if indexed_node is not None:
            idx, node = indexed_node
            if node.cost > evaluated_cost:
                node.cost = evaluated_cost
                del nodes[idx]
                heapq.heappush(nodes, node)
        else:
            node = Node(neighbour, risk, evaluated_cost, calculate_heuristic(self._map, neighbour))
            heapq.heappush(nodes, node)


def transform_risk(value):
    return value + 1 if value < 9 else 1


def generate_adjacent_tile(entry):
    return [[transform_risk(num) for num in row] for row in entry]


def extend_maps_height(map):
    tile = list(map)
    for _ in range(4):
        tile = generate_adjacent_tile(tile)
        map += tile


def extend_maps_width(map):
    for row in map:
        tile_row = list(row)
        for _ in range(4):
            tile_row = [transform_risk(num) for num in tile_row]
            row += tile_row


def extend_map(map):
    extend_maps_height(map)
    extend_maps_width(map)


def resolve_part1(input):
    risk_levels = parse_risk_level_map(input)
    return AStarAlgorithm(risk_levels).find_cost_of_best_path()


def resolve_part2(input):
    # this takes a while :(
    risk_levels = parse_risk_level_map(input)
    extend_map(risk_levels)
    return AStarAlgorithm(risk_levels).find_cost_of_best_path()