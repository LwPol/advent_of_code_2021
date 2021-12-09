from typing import List, NamedTuple, Set
import re
from itertools import chain


DIGITS_BY_SEGMENTS = [
    set('abcefg'),  # 0
    set('cf'),      # 1
    set('acdeg'),   # 2
    set('acdfg'),   # 3
    set('bcdf'),    # 4
    set('abdfg'),   # 5
    set('abdefg'),  # 6
    set('acf'),     # 7
    set('abcdefg'), # 8
    set('abcdfg')   # 9
]
UNIQUE_LENGTHS = (
    len(DIGITS_BY_SEGMENTS[1]),
    len(DIGITS_BY_SEGMENTS[4]),
    len(DIGITS_BY_SEGMENTS[7]),
    len(DIGITS_BY_SEGMENTS[8])
)


class Display(NamedTuple):
    signal_patterns: List[Set[str]]
    digits_output: List[Set[str]]


def parse_displays(input):
    display_pattern = r'(.+) \| (.+)'
    def parse_line(line):
        signal_patterns_str, digits_output_str = re.match(display_pattern, line).groups()
        signal_patterns = [set(sig) for sig in signal_patterns_str.split(' ')]
        digits_output = [set(dig) for dig in digits_output_str.split(' ')]
        return Display(signal_patterns, digits_output)
    return [parse_line(line) for line in input]


def count_1_4_7_8_digits_in_output(displays):
    outputs = chain.from_iterable(display.digits_output for display in displays)
    return sum(1 for out in outputs if len(out) in UNIQUE_LENGTHS)


def is_subset_of(set, subset):
    return len(subset - set) == 0


def get_patterns_with_unique_lengths(signal_patterns):
    def find_pattern_by_length(length):
        return next(filter(lambda pattern: len(pattern) == length, signal_patterns))
    return tuple(find_pattern_by_length(length) for length in UNIQUE_LENGTHS)


def get_from(set):
    return next(iter(set))


class MessyDisplayReader:
    def __init__(self, signal_patterns):
        self.signal_to_segment = {}
        easy_to_recognize = get_patterns_with_unique_lengths(signal_patterns)
        self.one, self.four, self.seven, self.eight = easy_to_recognize
        self._resolve_signal_to_segment_mapping(signal_patterns)
    

    def _resolve_signal_to_segment_mapping(self, signal_patterns):
        a_segment = self._get_segment_a()
        self.signal_to_segment[a_segment] = 'a'
        self.three = self._identify_three_pattern(signal_patterns)
        d_segment = self._get_segment_d()
        self.signal_to_segment[d_segment] = 'd'
        self.signal_to_segment[self._get_segment_b(d_segment)] = 'b'
        self.signal_to_segment[self._get_segment_g(a_segment, d_segment)] = 'g'
        self.six = self._identify_six_pattern(signal_patterns)
        f_segment = self._get_segment_f()
        self.signal_to_segment[f_segment] = 'f'
        self.signal_to_segment[self._get_segment_c(f_segment)] = 'c'
        self.signal_to_segment[self._get_segment_e()] = 'e'


    def _get_segment_a(self):
        return get_from(self.seven - self.one)
    
    
    def _identify_three_pattern(self, signal_patterns):
        matching_threes_length = filter(lambda pattern: len(pattern) == len(DIGITS_BY_SEGMENTS[3]), signal_patterns)
        return next(filter(lambda pattern: is_subset_of(set=pattern, subset=self.one), matching_threes_length))
    

    def _get_segment_d(self):
        return get_from((self.three & self.four) - self.one)
    

    def _get_segment_b(self, d):
        return get_from(self.four - self.one - {d})
    

    def _get_segment_g(self, a, d):
        return get_from(self.three - self.one - {a, d})
    

    def _identify_six_pattern(self, signal_patterns):
        matching_six_length = filter(lambda pattern: len(pattern) == len(DIGITS_BY_SEGMENTS[6]), signal_patterns)
        return next(filter(lambda pattern: not is_subset_of(set=pattern, subset=self.one), matching_six_length))
    

    def _get_segment_f(self):
        return get_from(self.six & self.one)
    

    def _get_segment_c(self, f):
        return get_from(self.one - {f})


    def _get_segment_e(self):
        return get_from(self.eight - set(self.signal_to_segment.keys()))
    

    def read_number(self, digits):
        return int(''.join(str(self._digit_output_to_actual_digit(digit)) for digit in digits))
    

    def _digit_output_to_actual_digit(self, digit_output):
        actual_segments = {self.signal_to_segment[d] for d in digit_output}
        return DIGITS_BY_SEGMENTS.index(actual_segments)


def read_display(display):
    return MessyDisplayReader(display.signal_patterns).read_number(display.digits_output)


def resolve_part1(input):
    return count_1_4_7_8_digits_in_output(parse_displays(input))


def resolve_part2(input):
    displays = parse_displays(input)
    return sum(read_display(display) for display in displays)