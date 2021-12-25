import re
import itertools
from typing import NamedTuple
from collections import deque
from functools import reduce


SCANNER_REGEX = r'--- scanner (\d+) ---'


class Vector3D(NamedTuple):
    x: int
    y: int
    z: int


    def __add__(self, other):
        return Vector3D(*(x + y for x, y in zip(self, other)))
    

    def __sub__(self, other):
        return Vector3D(*(x - y for x, y in zip(self, other)))


class Matrix3x3:
    def __init__(self):
        self._matrix = [[0 for _ in range(3)] for _ in range(3)]
    

    def __getitem__(self, indices):
        x, y = indices
        return self._matrix[y][x]
    

    def __setitem__(self, indices, value):
        x, y = indices
        self._matrix[y][x] = value
    

    def __mul__(self, other):
        if isinstance(other, Matrix3x3):
            return self._multiply_matrices(other)
        elif isinstance(other, Vector3D):
            return self._apply_on_vector(other)


    def _multiply_matrices(self, other):
        result = Matrix3x3()
        for x, y in itertools.product(range(3), repeat=2):
            result[x, y] = sum(self[x, i] * other[i, y] for i in range(3))
        return result
    

    def _apply_on_vector(self, vector):
        return Vector3D(*(sum(self[x, i] * vector[i] for i in range(3)) for x in range(3)))


def identity_matrix():
    ret = Matrix3x3()
    ret[0, 0] = ret[1, 1] = ret[2, 2] = 1
    return ret


def x_rotation():
    ret = Matrix3x3()
    ret[0, 0] = 1
    ret[1, 2], ret[2, 1] = -1, 1
    return ret


def z_rotation():
    ret = Matrix3x3()
    ret[2, 2] = 1
    ret[0, 1], ret[1, 0] = -1, 1
    return ret


IDENTITY = identity_matrix()
AROUND_X = x_rotation()
AROUND_Z = z_rotation()


def generate_rotations_around_vertical_axis(base_rotation):
    def rotate_by_base(begin):
        yield begin
        for _ in range(3):
            begin = AROUND_Z * begin
            yield begin
    rotations = zip(rotate_by_base(base_rotation), rotate_by_base(AROUND_X * AROUND_X * base_rotation))
    return list(itertools.chain.from_iterable(rotations))


def generate_all_orientations():
    vertical_z = generate_rotations_around_vertical_axis(IDENTITY)
    vertical_y = generate_rotations_around_vertical_axis(AROUND_X)
    vertical_x = generate_rotations_around_vertical_axis(AROUND_X * AROUND_Z)
    return vertical_z + vertical_y + vertical_x


def parse_scanner_report(input_iter):
    def parse_coords(line):
        return Vector3D(*(int(coord) for coord in line.split(',')))
    scanner_id = int(re.match(SCANNER_REGEX, next(input_iter)).group(1))
    report = {parse_coords(line) for line in itertools.takewhile(lambda l: len(l) > 0, input_iter)}
    return (scanner_id, report)


def parse_scanner_reports(input):
    result = {}
    it = iter(input)
    try:
        while True:
            scanner, report = parse_scanner_report(it)
            result[scanner] = report
    except StopIteration:
        return result


def transform_coordinates(report, scanner_pos):
    return {coords + scanner_pos for coords in report}


def find_overlapping_points(reference_report, scanner_report, matched_points):
    reference_coords, scanner_coords = matched_points
    scanner_pos = reference_coords - scanner_coords
    scanner_report = transform_coordinates(scanner_report, scanner_pos)
    return scanner_report & reference_report


def find_points_match_with_overlap_area(reference_report, scanner_report, overlap_size):
    points_to_consider = set(list(scanner_report)[:(overlap_size - 1)])
    for reference, point in itertools.product(reference_report, points_to_consider):
        overlapping_points = find_overlapping_points(reference_report, scanner_report, (reference, point))
        if len(overlapping_points) >= overlap_size:
            return (reference, point)


def apply_orientation(report, orientation):
    return {orientation * coords for coords in report}


def find_orientation_with_overlap(reference_report, scanner_report, overlap_size):
    rotated_reports = (apply_orientation(scanner_report, orient) for orient in generate_all_orientations())
    def report_with_match():
        for report in rotated_reports:
            yield (report, find_points_match_with_overlap_area(reference_report, report, overlap_size))
    return next(filter(lambda entry: entry[1] is not None, report_with_match()), None)


def normalize_report(report, reference_points):
    ref, relative = reference_points
    scanner_pos = ref - relative
    return (transform_coordinates(report, scanner_pos), scanner_pos)


def normalize_by_report(normalized_report, non_normalized_reports):
    overlapping_reports = {}
    for scanner, report in non_normalized_reports.items():
        match = find_orientation_with_overlap(normalized_report, report, overlap_size=12)
        if match is not None:
            overlapping_reports[scanner] = normalize_report(*match)
    return overlapping_reports


def normalize_scanner_reports(scanner_reports):
    result = {0: (scanner_reports[0], Vector3D(0, 0, 0))}
    reports_queue = deque([scanner_reports[0]])
    scanner_reports = scanner_reports.copy()
    del scanner_reports[0]
    while len(scanner_reports) > 0:
        next_report = reports_queue.pop()
        normalized = normalize_by_report(next_report, scanner_reports)
        for scanner, entry in normalized.items():
            del scanner_reports[scanner]
            result[scanner] = entry
            reports_queue.appendleft(entry[0])
    return result


def manhattan_dist(vec1, vec2):
    return sum(abs(x - y) for x, y in zip(vec1, vec2))


# both parts take some time on real input
def resolve_part1(input):
    scanners = parse_scanner_reports(input)
    normalized = normalize_scanner_reports(scanners)
    reports = (entry[0] for entry in normalized.values())
    return len(reduce(lambda s1, s2: s1 | s2, reports, set()))


def resolve_part2(input):
    scanners = parse_scanner_reports(input)
    normalized = normalize_scanner_reports(scanners)
    scanner_positions = [entry[1] for entry in normalized.values()]
    return max(manhattan_dist(s1, s2) for s1, s2 in itertools.combinations(scanner_positions, 2))