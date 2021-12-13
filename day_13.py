import itertools
from typing import NamedTuple
import re


FOLD_EXPRESSION_REGEX = r'fold along (x|y)=(\d+)'


class Point(NamedTuple):
    x: int
    y: int


class Fold(NamedTuple):
    direction: str
    line: int


def parse_points(input_iter):
    points_input = itertools.takewhile(lambda line: line != '', input_iter)
    points_str = map(lambda line: line.split(','), points_input)
    return {Point(int(x), int(y)) for x, y in points_str}


def parse_folds(input_iter):
    folds_str = map(lambda expr: re.match(FOLD_EXPRESSION_REGEX, expr).groups(), input_iter)
    return [Fold(direction=dir, line=int(amount)) for dir, amount in folds_str]


def parse_paper(input):
    it = iter(input)
    points = parse_points(it)
    folds = parse_folds(it)
    return (points, folds)


def apply_left_fold(points, fold_line):
    def fold_left(point):
        return Point(2 * fold_line - point.x, point.y)
    left_side = set(filter(lambda point: point.x < fold_line, points))
    right_side_folded = {fold_left(pt) for pt in points if pt.x > fold_line}
    return left_side | right_side_folded


def apply_upper_fold(points, fold_line):
    def fold_up(point):
        return Point(point.x, 2 * fold_line - point.y)
    upper_side = set(filter(lambda point: point.y < fold_line, points))
    down_side_folded = {fold_up(pt) for pt in points if pt.y > fold_line}
    return upper_side | down_side_folded


def apply_fold(points, fold):
    if fold.direction == 'x':
        return apply_left_fold(points, fold.line)
    return apply_upper_fold(points, fold.line)


def strigify_paper(points):
    x_max = max(pt.x for pt in points)
    y_max = max(pt.y for pt in points)
    display = [list(itertools.repeat(' ', x_max + 1)) for _ in range(y_max + 1)]
    for point in points:
        display[point.y][point.x] = 'X'
    return '\n'.join(''.join(row) for row in display)


def resolve_part1(input):
    points, folds = parse_paper(input)
    return len(apply_fold(points, folds[0]))


def resolve_part2(input):
    points, folds = parse_paper(input)
    for fold in folds:
        points = apply_fold(points, fold)
    return '\n' + strigify_paper(points)