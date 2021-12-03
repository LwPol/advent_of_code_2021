def determine_most_common_bit(report, bit_index):
    bit_counts = {'0': 0, '1': 0}
    for number in report:
        bit_counts[number[bit_index]] += 1
    zeros, ones = bit_counts['0'], bit_counts['1']
    if zeros > ones:
        return '0'
    if ones > zeros:
        return '1'
    return None


def reverse_bit(bit):
    return '1' if bit == '0' else '0'


def get_gamma_epsilon_rates(report):
    gamma_bits = []
    epsilon_bits = []
    bits_count = len(report[0])
    for bit_idx in range(bits_count):
        most_common = determine_most_common_bit(report, bit_idx)
        gamma_bits.append(most_common)
        epsilon_bits.append(reverse_bit(most_common))
    gamma, epsilon = (int(''.join(bits), 2) for bits in (gamma_bits, epsilon_bits))
    return (gamma, epsilon)


class ReportFilterWithBitCriteria:
    def __init__(self, report, bit_criteria_func):
        self._report = list(report)
        self._bit_criteria_func = bit_criteria_func
    

    def get(self):
        step = 0
        while len(self._report) > 1:
            match_bit = self._bit_criteria_func(self._report, step)
            self._report = list(filter(lambda num: num[step] == match_bit, self._report))
            step += 1
        return int(''.join(self._report[0]), 2)


def determine_oxygen_generator_rating_bit(report, bit_index):
    most_common = determine_most_common_bit(report, bit_index)
    return most_common if most_common is not None else '1'


def determine_co2_scrubber_rating_bit(report, bit_index):
    most_common = determine_most_common_bit(report, bit_index)
    return reverse_bit(most_common) if most_common is not None else '0'


def resolve_part1(input):
    gamma, epsilon = get_gamma_epsilon_rates(input)
    return gamma * epsilon


def resolve_part2(input):
    oxygen_rating = ReportFilterWithBitCriteria(input, determine_oxygen_generator_rating_bit).get()
    co2_rating = ReportFilterWithBitCriteria(input, determine_co2_scrubber_rating_bit).get()
    return oxygen_rating * co2_rating