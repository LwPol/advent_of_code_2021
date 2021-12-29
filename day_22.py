import re
import itertools


REBOOT_STEP_REGEX = r'(on|off) x=(-?\d+)\.\.(-?\d+),y=(-?\d+)\.\.(-?\d+),z=(-?\d+)\.\.(-?\d+)'


def parse_reboot_steps(input):
    def parse_step(line):
        parsed = re.match(REBOOT_STEP_REGEX, line).groups()
        instruction = parsed[0]
        x, y, z = (tuple(int(num) for num in interval) for interval in (parsed[1:3], parsed[3:5], parsed[5:7]))
        return RebootStep(instruction, x, y, z)
    return [parse_step(line) for line in input]


def get_interval_intersection(lhs, rhs):
    intersection = (max(lhs[0], rhs[0]), min(lhs[1], rhs[1]))
    return intersection if intersection[0] <= intersection[1] else None


def get_interval_difference(lhs, rhs):
    intersection = get_interval_intersection(lhs, rhs)
    if intersection is None:
        return (lhs,)
    diffs = (lhs[0], intersection[0] - 1), (intersection[1] + 1, lhs[1])
    return tuple(diff for diff in diffs if diff[0] <= diff[1])


class Cube:
    def __init__(self, x_range, y_range, z_range):
        self._x_range = x_range
        self._y_range = y_range
        self._z_range = z_range
    

    @staticmethod
    def _narrow_range_to_initialization_area(range):
        left = max(range[0], -50)
        right = min(range[1], 50)
        return (left, right)


    def enumerate_cubes_in_initialization_area(self):
        x_range = self._narrow_range_to_initialization_area(self._x_range)
        y_range = self._narrow_range_to_initialization_area(self._y_range)
        z_range = self._narrow_range_to_initialization_area(self._z_range)
        def from_range(r):
            return range(r[0], r[1] + 1)
        return itertools.product(from_range(x_range), from_range(y_range), from_range(z_range))
    

    def cube_range(self):
        return (self._x_range, self._y_range, self._z_range)


    def size(self):
        def range_size(r):
            return r[1] - r[0] + 1
        return range_size(self._x_range) * range_size(self._y_range) * range_size(self._z_range)
    

    def is_non_overlapping_with(self, cube):
        return any(get_interval_intersection(r1, r2) is None for r1, r2 in zip(self.cube_range(), cube.cube_range()))


    def subtract(self, cube):
        if self.is_non_overlapping_with(cube):
            return [self]
        x1, y1, z1 = self.cube_range()
        x2, y2, z2 = cube.cube_range()
        z12 = get_interval_intersection(z1, z2)
        y12 = get_interval_intersection(y1, y2)
        z_cubes = (Cube(x1, y1, z) for z in get_interval_difference(z1, z2))
        y_cubes = (Cube(x1, y, z12) for y in get_interval_difference(y1, y2))
        x_cubes = (Cube(x, y12, z12) for x in get_interval_difference(x1, x2))
        return list(itertools.chain(z_cubes, y_cubes, x_cubes))


class RebootStep:
    def __init__(self, instruction, x_range, y_range, z_range):
        self.is_turning_on = instruction == 'on'
        self.cube = Cube(x_range, y_range, z_range)


def run_initialization(steps):
    turned_on = set()
    for step in steps:
        cubes = set(step.cube.enumerate_cubes_in_initialization_area())
        if step.is_turning_on:
            turned_on |= cubes
        else:
            turned_on -= cubes
    return turned_on


def calculate_cube_volume_excluding_processed_cubes_area(processed_cubes, cubes):
    for processed in processed_cubes:
        cubes = list(itertools.chain.from_iterable(c.subtract(processed) for c in cubes))
    return sum(cube.size() for cube in cubes)


def exclude_turned_off_cubes(cube, turned_off):
    remaining = [cube]
    for to_exclude in turned_off:
        remaining = list(itertools.chain.from_iterable(c.subtract(to_exclude) for c in remaining))
    return remaining


def run_reboot(steps):
    steps = list(reversed(steps))
    turned_on = 0
    turned_off_cubes = []
    for idx, step in enumerate(steps):
        if step.is_turning_on:
            processed = (step.cube for step in steps[:idx])
            turning = exclude_turned_off_cubes(step.cube, turned_off_cubes)
            turned_on += calculate_cube_volume_excluding_processed_cubes_area(processed, turning)
        else:
            turned_off_cubes.append(step.cube)
    return turned_on


def resolve_part1(input):
    return len(run_initialization(parse_reboot_steps(input)))


def resolve_part2(input):
    steps = parse_reboot_steps(input)
    return run_reboot(steps)