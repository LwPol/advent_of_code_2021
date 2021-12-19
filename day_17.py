import re
from typing import NamedTuple
import math
import itertools


class TargetArea(NamedTuple):
    x_min: int
    x_max: int
    y_min: int
    y_max: int


def parse_target_area(input):
    TARGET_REGEX = r'target area: x=(\d+)\.\.(\d+), y=(-\d+)\.\.(-\d+)'
    matches = re.match(TARGET_REGEX, input[0]).groups()
    return TargetArea(*(int(num) for num in matches))


def find_zero_of_trajectory_function(velocity, target):
    delta = (velocity + 0.5) ** 2 - 2 * target
    return (velocity + 0.5 - math.sqrt(delta), velocity + 0.5 + math.sqrt(delta))


def calculate_y_values_in_target(velocity, target_area):
    _, over_y_min = find_zero_of_trajectory_function(velocity, target_area.y_min)
    _, below_y_max = find_zero_of_trajectory_function(velocity, target_area.y_max)
    return (below_y_max, over_y_min)


def calculate_x_values_in_target(velocity, target_area):
    over_x_min, _ = find_zero_of_trajectory_function(velocity, target_area.x_min)
    below_x_max, _ = find_zero_of_trajectory_function(velocity, target_area.x_max)
    return (over_x_min, below_x_max)


def get_steps_falling_in_target_at_y_axis(velocity, target_area):
    real_interval = calculate_y_values_in_target(velocity, target_area)
    rounded = (math.floor(real_interval[0]), math.floor(real_interval[1]) + 1)
    return list(filter(lambda n: n >= real_interval[0] and n <= real_interval[1], range(*rounded)))


def get_steps_falling_in_target_at_x_axis(velocity, target_area):
    real_interval = calculate_x_values_in_target(velocity, target_area)
    rounded = (math.floor(real_interval[0]), math.floor(real_interval[1]) + 1)
    return list(filter(lambda n: n >= real_interval[0] and n <= real_interval[1], range(*rounded)))


def is_falling_in_target_at_y_axis(velocity, target_area):
    return len(get_steps_falling_in_target_at_y_axis(velocity, target_area)) > 0


def find_highest_y_velocity_for_target(target_area, brute_force_scale):
    velocities = filter(lambda v: is_falling_in_target_at_y_axis(v, target_area), range(brute_force_scale))
    return max(velocities)


def get_x_velocities_stopping_in_target(target_area):
    min = math.sqrt(2 * target_area.x_min) - 0.5
    max = math.sqrt(2 * target_area.x_max) - 0.5
    return (math.ceil(min), math.floor(max))


def map_x_velocities_stopping_in_target(target_area):
    min, max = get_x_velocities_stopping_in_target(target_area)
    def get_smallest_step_in_target(velocity):
        over_x_min, _ = find_zero_of_trajectory_function(velocity, target_area.x_min)
        return math.ceil(over_x_min)
    return {v: get_smallest_step_in_target(v) for v in range(min, max + 1)}


def map_y_velocities_falling_at_target_to_steps(target_area, brute_force_interval):
    result = {v: get_steps_falling_in_target_at_y_axis(v, target_area) for v in range(*brute_force_interval)}
    filter_empty_velocities = filter(lambda entry: len(entry[1]) > 0, result.items())
    return dict(filter_empty_velocities)


def map_x_velocities_falling_at_target_to_steps(target_area, brute_force_interval):
    result = {v: get_steps_falling_in_target_at_x_axis(v, target_area) for v in range(*brute_force_interval)}
    filter_empty_velocities = filter(lambda entry: len(entry[1]) > 0, result.items())
    return dict(filter_empty_velocities)


def count_velocities_combination_falling_in_target(target_area):
    y_velocities = map_y_velocities_falling_at_target_to_steps(target_area, (-300, 1000))
    x_stopping_at_target = map_x_velocities_stopping_in_target(target_area)
    minimal_x_going_through = max(x_stopping_at_target.keys()) + 1
    x_going_through_target = (
        map_x_velocities_falling_at_target_to_steps(target_area, (minimal_x_going_through, 200)))
    v1 = (sum(1
        for vx, vy in itertools.product(x_going_through_target.keys(), y_velocities.keys())
        if set(x_going_through_target[vx]) & set(y_velocities[vy])))
    v2 = (sum(1
        for vx, vy in itertools.product(x_stopping_at_target.keys(), y_velocities.keys())
        if any(steps >= x_stopping_at_target[vx] for steps in y_velocities[vy])))
    return v1 + v2


def resolve_part1(input):
    target = parse_target_area(input)
    n = find_highest_y_velocity_for_target(target, 1000)
    return n ** 2 - (n * (n - 1)) // 2


def resolve_part2(input):
    target = parse_target_area(input)
    return count_velocities_combination_falling_in_target(target)