import itertools


GRID_SIZE = 10


def parse_energy_levels(input):
    return [[int(num) for num in line] for line in input]


def get_energy_level(grid, x, y):
    return grid[y][x]


def enumerate_grid_points():
    return itertools.product(range(GRID_SIZE), range(GRID_SIZE))


def increase_energy_levels(octopus_grid):
    for x, y in enumerate_grid_points():
        octopus_grid[y][x] += 1


def enumerate_neighbours(position):
    def is_in_grid(pos):
        x, y = pos
        return x >= 0 and x < GRID_SIZE and y >= 0 and y < GRID_SIZE
    x, y = position
    deltas = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
    points_around = ((x + dx, y + dy) for dx, dy in deltas)
    return filter(is_in_grid, points_around)


def flash_octopus(grid, position):
    for x, y in enumerate_neighbours(position):
        grid[y][x] += 1


def find_flashing_octopus(grid, to_ignore):
    def has_enough_energy(pos):
        return get_energy_level(grid, *pos) > 9
    return next(filter(lambda pos: has_enough_energy(pos) and pos not in to_ignore, enumerate_grid_points()), None)


def reset_energy_level(octopus_grid, octopuses):
    for x, y in octopuses:
        octopus_grid[y][x] = 0


class StepSimulator:
    def __init__(self):
        self._flashed_octopus = None
    

    def simulate_step(self, octopus_grid):
        increase_energy_levels(octopus_grid)
        flashed = self._flash_all_octopuses_on_proper_energy_level(octopus_grid)
        reset_energy_level(octopus_grid, flashed)
        return len(flashed)
    

    def _flash_all_octopuses_on_proper_energy_level(self, octopus_grid):
        already_flashed = set()
        def is_any_octopus_flashing():
            self._flashed_octopus = find_flashing_octopus(octopus_grid, already_flashed)
            return self._flashed_octopus is not None
        while is_any_octopus_flashing():
            flash_octopus(octopus_grid, self._flashed_octopus)
            already_flashed.add(self._flashed_octopus)
        return already_flashed


def count_flashes(octopus_grid, steps):
    simulator = StepSimulator()
    return sum(simulator.simulate_step(octopus_grid) for _ in range(steps))


def find_synchronization_point(octopus_grid):
    simulator = StepSimulator()
    def are_all_octopuses_flashed(_):
        return simulator.simulate_step(octopus_grid) == GRID_SIZE ** 2
    return next(filter(are_all_octopuses_flashed, itertools.count(1)))


def resolve_part1(input):
    return count_flashes(parse_energy_levels(input), steps=100)


def resolve_part2(input):
    return find_synchronization_point(parse_energy_levels(input))