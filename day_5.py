from typing import NamedTuple
import re
from itertools import repeat


class Point(NamedTuple):
    x: int
    y: int


class Line(NamedTuple):
    begin: Point
    end: Point


def parse_lines(input):
    def parse_single_line(line):
        match = re.match(r'(\d+),(\d+) -> (\d+),(\d+)', line)
        begin = (int(x) for x in match.group(1, 2))
        end = (int(x) for x in match.group(3, 4))
        return Line(Point(*begin), Point(*end))
    return [parse_single_line(line) for line in input]


def is_vertical(line):
    return line.begin.x == line.end.x


def is_horizontal(line):
    return line.begin.y == line.end.y


def filter_horizontal_and_vertical_lines(lines):
    return filter(lambda line: is_vertical(line) or is_horizontal(line), lines)


def enumerate_points(line):
    def closed_interval(begin, end):
        if begin <= end:
            return range(begin, end + 1)
        return range(begin, end - 1, -1)
    if is_horizontal(line):
        return zip(closed_interval(line.begin.x, line.end.x), repeat(line.begin.y))
    if is_vertical(line):
        return zip(repeat(line.begin.x), closed_interval(line.begin.y, line.end.y))
    return zip(closed_interval(line.begin.x, line.end.x), closed_interval(line.begin.y, line.end.y))


def mark_line_on_plane(plane, line):
    for x, y in enumerate_points(line):
        plane[(x, y)] = plane.get((x, y), 0) + 1


def build_vent_lines_map(lines):
    plane = {}
    for line in lines:
        mark_line_on_plane(plane, line)
    return plane


def calculate_overlapping_points_count(lines):
    vent_lines_overlap = build_vent_lines_map(lines)
    return sum(1 for _, overlap in vent_lines_overlap.items() if overlap > 1)


def resolve_part1(input):
    vent_lines = parse_lines(input)
    return calculate_overlapping_points_count(filter_horizontal_and_vertical_lines(vent_lines))


def resolve_part2(input):
    return calculate_overlapping_points_count(parse_lines(input))