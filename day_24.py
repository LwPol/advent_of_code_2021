from typing import NamedTuple


class MonadsDigitProcessorData(NamedTuple):
    has_division_by_26: bool
    x_component: int
    y_component: int


def parse_monad_processors(input):
    per_digit = [input[i:i+18] for i in range(0, len(input), 18)]
    result = []
    for monad_per_digit in per_digit:
        division_by_26 = monad_per_digit[4] == 'div z 26'
        x = int(monad_per_digit[5].split()[-1])
        y = int(monad_per_digit[15].split()[-1])
        result.append(MonadsDigitProcessorData(has_division_by_26=division_by_26, x_component=x, y_component=y))
    return result


# deduced from input
def process_version_number_digit(monads_processor, z, digit):
    x = int(z % 26 + monads_processor.x_component != digit)
    if monads_processor.has_division_by_26:
        z //= 26
    z *= 25 * x + 1
    y = (digit + monads_processor.y_component) * x
    return z + y


def can_z_be_lowered_to_zero(z, remaining):
    return z < 26 ** sum(1 for remain in remaining if remain.has_division_by_26)


def decreasing_digits(upper_limit):
    return range(upper_limit - 1, 0, -1)


def increasing_digits(lower_limit):
    return range(lower_limit + 1, 10)


def convert_to_serial_number(digits_stack):
    return ''.join(str(digit[0]) for digit in digits_stack)


def find_next_appropriate_digit(digits, monad_processors, z, digits_generator):
    digit_index = len(digits)
    for digit in digits_generator:
        new_z = process_version_number_digit(monad_processors[digit_index], z, digit)
        if can_z_be_lowered_to_zero(new_z, monad_processors[digit_index+1:]):
            return digit, new_z


def set_next_viable_digit_sequence(digits, monad_processors, digits_generator_factory):
    last_digit, _ = digits.pop()
    _, z = digits[-1] if digits else (0, 0)
    next_digit = find_next_appropriate_digit(digits, monad_processors, z, digits_generator_factory(last_digit))
    if next_digit is not None:
        digits.append(next_digit)
    else:
        set_next_viable_digit_sequence(digits, monad_processors, digits_generator_factory)


def find_highest_serial_number(monad):
    digits_stack = [(9, process_version_number_digit(monad[0], z=0, digit=9))]
    while len(digits_stack) != 14:
        next_digit = (find_next_appropriate_digit(
            digits_stack, monad, z=digits_stack[-1][1], digits_generator=decreasing_digits(10)))
        if next_digit is not None:
            digits_stack.append(next_digit)
        else:
            set_next_viable_digit_sequence(digits_stack, monad, decreasing_digits)
    return convert_to_serial_number(digits_stack)


def find_lowest_serial_number(monad):
    digits_stack = [(1, process_version_number_digit(monad[0], z=0, digit=1))]
    while len(digits_stack) != 14:
        next_digit = (find_next_appropriate_digit(
            digits_stack, monad, z=digits_stack[-1][1], digits_generator=increasing_digits(0)))
        if next_digit is not None:
            digits_stack.append(next_digit)
        else:
            set_next_viable_digit_sequence(digits_stack, monad, increasing_digits)
    return convert_to_serial_number(digits_stack)


def resolve_part1(input):
    return find_highest_serial_number(parse_monad_processors(input))


def resolve_part2(input):
    return find_lowest_serial_number(parse_monad_processors(input))