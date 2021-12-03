def convert_measurements(input):
    return [int(num) for num in input]


def count_increases(numbers):
    return sum(1 for current, next in zip(numbers, numbers[1:]) if current < next)
    

def resolve_part1(input):
    return count_increases(convert_measurements(input))


def resolve_part2(input):
    measurements = convert_measurements(input)
    slided_measurements = [a + b + c for a, b, c in zip(measurements, measurements[1:], measurements[2:])]
    return count_increases(slided_measurements)
