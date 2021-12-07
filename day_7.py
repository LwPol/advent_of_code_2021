def parse_crabs_positions(input):
    return [int(pos) for pos in input[0].split(',')]


def calculate_median(positions):
    positions = sorted(positions)
    if len(positions) % 2 == 1:
        return positions[len(positions) // 2]
    middle = len(positions) // 2
    return (positions[middle - 1] + positions[middle]) / 2


def calculate_mean(positions):
    return sum(positions) / len(positions)


class OptimizerA:
    @staticmethod
    def get_candidates(positions):
        median_approx = round(calculate_median(positions))
        return (median_approx - 1, median_approx, median_approx + 1)
    

    @staticmethod
    def calculate_fuel_usage(positions, candidate):
        return sum(abs(pos - candidate) for pos in positions)


class OptimizerB:
    @staticmethod
    def get_candidates(positions):
        mean_approx = round(calculate_mean(positions))
        return (mean_approx - 1, mean_approx, mean_approx + 1)
    

    @staticmethod
    def calculate_fuel_usage(positions, candidate):
        def sum_of_n_numbers(n):
            return (n * (n + 1)) // 2
        return sum(sum_of_n_numbers(abs(pos - candidate)) for pos in positions)


def find_minimal_fuel_cost(positions, optimizer):
    return min(optimizer.calculate_fuel_usage(positions, candidate) for candidate in optimizer.get_candidates(positions))


def resolve_part1(input):
    return find_minimal_fuel_cost(parse_crabs_positions(input), OptimizerA)


def resolve_part2(input):
    return find_minimal_fuel_cost(parse_crabs_positions(input), OptimizerB)