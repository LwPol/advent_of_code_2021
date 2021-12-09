import itertools


def parse_heightmap(input):
    return [[int(num) for num in line] for line in input]


def generate_all_points(heightmap):
    return itertools.product(range(len(heightmap[0])), range(len(heightmap)))


def get_value(heightmap, x, y):
    return heightmap[y][x]


def neighbours_of_point(heightmap, x, y):
    if x - 1 >= 0:
        yield (x - 1, y)
    if x + 1 < len(heightmap[0]):
        yield (x + 1, y)
    if y - 1 >= 0:
        yield (x, y - 1)
    if y + 1 < len(heightmap):
        yield (x, y + 1)


def flow_downward(heightmap, x, y):
    value = get_value(heightmap, x, y)
    neighbours = neighbours_of_point(heightmap, x, y)
    lowest_neighbour = min(neighbours, key=lambda point: get_value(heightmap, *point))
    return lowest_neighbour if get_value(heightmap, *lowest_neighbour) <= value else None


def is_low_point(heightmap, x, y):
    return flow_downward(heightmap, x, y) is None


def low_points(heightmap):
    return filter(lambda point: is_low_point(heightmap, *point), generate_all_points(heightmap))


def sum_risk_levels(heightmap):
    return sum(1 + get_value(heightmap, *point) for point in low_points(heightmap))


def get_basin_flow(heightmap, point):
    flow = [point]
    next_point = flow_downward(heightmap, *point)
    if next_point is not None:
        flow += get_basin_flow(heightmap, next_point)
    return flow


def map_points_to_basins(heightmap):
    basin_map = {point: {point} for point in low_points(heightmap)}
    mapped_points = set(basin_map.keys())
    locations_below_9 = filter(lambda p: get_value(heightmap, *p) != 9, generate_all_points(heightmap))
    for point in locations_below_9:
        if point in mapped_points:
            continue
        flow = get_basin_flow(heightmap, point)
        basin_map[flow[-1]].update(flow)
        mapped_points.update(flow)
    return basin_map


def get_three_largest_basins_product(basins):
    sorted_by_length = sorted(map(len, basins), reverse=True)
    a, b, c = sorted_by_length[:3]
    return a * b * c


def resolve_part1(input):
    return sum_risk_levels(parse_heightmap(input))


def resolve_part2(input):
    basins_map = map_points_to_basins(parse_heightmap(input))
    return get_three_largest_basins_product(basins_map.values())