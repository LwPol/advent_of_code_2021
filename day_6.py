from itertools import repeat
from collections import deque


def parse_initial_state(lines):
    init = deque(repeat(0, times=9))
    for fish in [int(num) for num in lines[0].split(',')]:
        init[fish] += 1
    return init


def simulate_single_day(current):
    reproducing_fish_count = current.popleft()
    current[6] += reproducing_fish_count
    current.append(reproducing_fish_count)


def simulate_lanternfish_population_growth(initial_state, days):
    current_state = deque(initial_state)
    for _ in range(days):
        simulate_single_day(current_state)
    return current_state


def resolve_part1(input):
    population = simulate_lanternfish_population_growth(parse_initial_state(input), days=80)
    return sum(population)


def resolve_part2(input):
    population = simulate_lanternfish_population_growth(parse_initial_state(input), days=256)
    return sum(population)