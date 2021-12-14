from collections import Counter
from typing import NamedTuple, Dict, Tuple


class PolymerCounters(NamedTuple):
    polymers: Dict[str, int]
    pairs: Dict[Tuple[str, str], int]


def parse_polymer_formula(input):
    template = input[0]
    rules_str = map(lambda line: line.split(' -> '), input[2:])
    rules = {polymer_pair: result for polymer_pair, result in rules_str}
    return (template, rules)


def create_polymer_counters(polymer):
    polymers_counter = Counter(polymer)
    polymer_pairs_counter = Counter(map(lambda pair: pair[0] + pair[1], zip(polymer, polymer[1:])))
    return PolymerCounters(polymers_counter, polymer_pairs_counter)


def increase_by_quantity(counter, key, quantity):
    counter[key] = counter.get(key, 0) + quantity


def count_polymers_after_single_extension(polymer_counters, rules):
    result = PolymerCounters(Counter(polymer_counters.polymers), Counter(polymer_counters.pairs))
    for pair, quantity in polymer_counters.pairs.items():
        new_polymer = rules[pair]
        increase_by_quantity(result.polymers, new_polymer, quantity)
        result.pairs[pair] -= quantity
        increase_by_quantity(result.pairs, pair[0] + new_polymer, quantity)
        increase_by_quantity(result.pairs, new_polymer + pair[1], quantity)
    return result


def count_polymers(template, rules, steps):
    counters = create_polymer_counters(template)
    for _ in range(steps):
        counters = count_polymers_after_single_extension(counters, rules)
    return counters.polymers


def get_min_max_difference(polymers_counter):
    max_quantity = max(polymers_counter.values())
    min_quantity = min(polymers_counter.values())
    return max_quantity - min_quantity


def resolve_part1(input):
    template, rules = parse_polymer_formula(input)
    return get_min_max_difference(count_polymers(template, rules, steps=10))


def resolve_part2(input):
    template, rules = parse_polymer_formula(input)
    return get_min_max_difference(count_polymers(template, rules, steps=40))