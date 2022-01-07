from enum import Enum
from itertools import count


class FacingDirection(Enum):
    EAST = 0
    SOUTH = 1


def parse_cucumbers_map(input):
    width, height = len(input[0]), len(input)
    cucumbers = {}
    for row_idx, row in enumerate(input):
        for idx, char in enumerate(row):
            if char == '>':
                cucumbers[(idx, row_idx)] = FacingDirection.EAST
            elif char == 'v':
                cucumbers[(idx, row_idx)] = FacingDirection.SOUTH
    return CucumbersMap(cucumbers, width, height)


class CucumbersMap:
    def __init__(self, initial_state, width, height):
        self._cucumbers = initial_state
        self._width = width
        self._height = height


    def move(self):
        new_positions, is_east_stalemate = self._move_east()
        south_update, is_south_stalemate = self._move_south(new_positions)
        new_positions.update(south_update)
        return CucumbersMap(new_positions, self._width, self._height), is_east_stalemate and is_south_stalemate


    def _move_east(self):
        east_facing = filter(lambda entry: entry[1] == FacingDirection.EAST, self._cucumbers.items())
        changed_positions = {}
        is_stalemate = True
        for pos, _ in east_facing:
            new_pos = self._determine_position_for_east_facing_cucumber(pos)
            is_stalemate = is_stalemate and pos == new_pos
            changed_positions[new_pos] = FacingDirection.EAST
        return changed_positions, is_stalemate
    

    def _move_south(self, new_east_positions):
        south_facing = filter(lambda entry: entry[1] == FacingDirection.SOUTH, self._cucumbers.items())
        changed_positions = {}
        is_stalemate = True
        for pos, _ in south_facing:
            new_pos = self._determine_position_for_south_facing_cucumber(pos, new_east_positions)
            is_stalemate = is_stalemate and pos == new_pos
            changed_positions[new_pos] = FacingDirection.SOUTH
        return changed_positions, is_stalemate
    

    def _determine_position_for_east_facing_cucumber(self, current_position):
        x, y = current_position
        x = x + 1 if x < self._width - 1 else 0
        if (x, y) in self._cucumbers:
            return current_position
        return (x, y)


    def _determine_position_for_south_facing_cucumber(self, current_position, new_east_positions):
        x, y = current_position
        y = y + 1 if y < self._height - 1 else 0
        if (x, y) in new_east_positions or ((x, y) in self._cucumbers and self._cucumbers[(x, y)] == FacingDirection.SOUTH):
            return current_position
        return (x, y)


def find_first_step_of_cucumbers_stalemate(cucumbers_map: CucumbersMap):
    for i in count(1):
        cucumbers_map, is_stalemate = cucumbers_map.move()
        if is_stalemate:
            return i


def resolve_part1(input):
    return find_first_step_of_cucumbers_stalemate(parse_cucumbers_map(input))


def resolve_part2(_):
    return '(ง^ᗜ^)ง'