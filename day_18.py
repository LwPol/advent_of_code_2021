import functools
from typing import Optional, Union
import itertools
from dataclasses import dataclass


@dataclass
class SnailfishPrimitive:
    value: int
    parent: Optional["SnailfishNumber"]


@dataclass
class SnailfishNumber:
    first: Union[SnailfishPrimitive, "SnailfishNumber"]
    second: Union[SnailfishPrimitive, "SnailfishNumber"]
    parent: Optional["SnailfishNumber"]


def collect_chars_until_ending_char(it, ending_char):
    return ''.join(itertools.takewhile(lambda c: c != ending_char, it))


def parse_snailfish_number_impl(input_iter):
    def parse_pair_element(ending_char):
        first_char = next(input_iter)
        if first_char != '[':
            value = int(first_char + collect_chars_until_ending_char(input_iter, ending_char))
            return SnailfishPrimitive(value, None)
        subnumber = parse_snailfish_number_impl(input_iter)
        next(input_iter)
        return subnumber
    first = parse_pair_element(',')
    second = parse_pair_element(']')
    return SnailfishNumber(first, second, None)


def apply_parentship(number):
    number.first.parent = number
    number.second.parent = number
    if isinstance(number.first, SnailfishNumber):
        apply_parentship(number.first)
    if isinstance(number.second, SnailfishNumber):
        apply_parentship(number.second)


def parse_snailfish_numbers(input):
    def parse_number(line):
        parsed = parse_snailfish_number_impl(iter(line[1:]))
        apply_parentship(parsed)
        return parsed
    return [parse_number(line) for line in input]


def clone_snailfish_number(number):
    def clone_element(node):
        if isinstance(node, SnailfishPrimitive):
            return SnailfishPrimitive(value=node.value, parent=None)
        return SnailfishNumber(first=clone_element(node.first), second=clone_element(node.second), parent=None)
    copy = clone_element(number)
    apply_parentship(copy)
    return copy


def find_pair_at_nesting_level(number, nesting_level):
    def impl(number, current_level, searched_level):
        if current_level == searched_level:
            return number
        if isinstance(number.first, SnailfishNumber):
            left = impl(number.first, current_level + 1, searched_level)
            if left is not None:
                return left
        if isinstance(number.second, SnailfishNumber):
            return impl(number.second, current_level + 1, searched_level)
        return None
    return impl(number, 0, nesting_level)


def apply_explosion_impact_impl(exploding_pair, explosion_side, opposite_side):
    def get_subtree_on_explosion_side(current_node):
        if current_node.parent is None:
            return None
        if id(explosion_side(current_node.parent)) == id(current_node):
            return get_subtree_on_explosion_side(current_node.parent)
        return explosion_side(current_node.parent)
    def get_furthest_opposite_site_value(subtree):
        while isinstance(subtree, SnailfishNumber):
            subtree = opposite_side(subtree)
        return subtree
    explosion_side_subtree = get_subtree_on_explosion_side(exploding_pair)
    if explosion_side_subtree is not None:
        value_to_update = get_furthest_opposite_site_value(explosion_side_subtree)
        value_to_update.value += explosion_side(exploding_pair).value


def apply_left_side_of_explosion(exploding_pair):
    apply_explosion_impact_impl(exploding_pair, lambda node: node.first, lambda node: node.second)


def apply_right_side_of_explosion(exploding_pair):
    apply_explosion_impact_impl(exploding_pair, lambda node: node.second, lambda node: node.first)


def explode(number):
    exploding = find_pair_at_nesting_level(number, nesting_level=4)
    if exploding is not None:
        apply_left_side_of_explosion(exploding)
        apply_right_side_of_explosion(exploding)
        parent = exploding.parent
        if id(parent.first) == id(exploding):
            parent.first = SnailfishPrimitive(value=0, parent=parent)
        else:
            parent.second = SnailfishPrimitive(value=0, parent=parent)
    return exploding is not None


def find_node_with_value_greater_then(tree, value):
    def enumerate_nodes(subtree):
        if isinstance(subtree, SnailfishPrimitive):
            yield subtree
        else:
            yield from enumerate_nodes(subtree.first)
            yield from enumerate_nodes(subtree.second)
    return next(filter(lambda node: node.value > value, enumerate_nodes(tree)), None)


def create_new_snailfish_number(left_value, right_value, parent):
    left, right = (SnailfishPrimitive(val, None) for val in (left_value, right_value))
    result = SnailfishNumber(left, right, parent)
    left.parent = result
    right.parent = result
    return result


def split(number):
    node_to_split = find_node_with_value_greater_then(number, value=9)
    if node_to_split is not None:
        parent = node_to_split.parent
        new_node = (
            create_new_snailfish_number(node_to_split.value // 2, (node_to_split.value + 1) // 2, parent))
        if id(parent.first) == id(node_to_split):
            parent.first = new_node
        else:
            parent.second = new_node
    return node_to_split is not None



def reduce(number):
    while explode(number) or split(number):
        pass


def add(lhs, rhs):
    lhs = clone_snailfish_number(lhs)
    rhs = clone_snailfish_number(rhs)
    result = SnailfishNumber(lhs, rhs, None)
    lhs.parent = rhs.parent = result
    reduce(result)
    return result


def calculate_magnitude(number):
    def magnitude_of_node(node):
        if isinstance(node, SnailfishPrimitive):
            return node.value
        return calculate_magnitude(node)
    return 3 * magnitude_of_node(number.first) + 2 * magnitude_of_node(number.second)
    

def resolve_part1(input):
    numbers = parse_snailfish_numbers(input)
    sum = functools.reduce(add, numbers)
    return calculate_magnitude(sum)


def resolve_part2(input):
    numbers = parse_snailfish_numbers(input)
    combinations_of_two = filter(lambda entry: id(entry[0]) != id(entry[1]), itertools.product(numbers, repeat=2))
    return max(calculate_magnitude(add(x, y)) for x, y in combinations_of_two)