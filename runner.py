import argparse
from importlib import import_module
import sys

parser = argparse.ArgumentParser(description='Advent of code 2021')
parser.add_argument('--day', '-d', help='day in advent', type=int, required=True)
parser.add_argument('--part', '-p', help='part of puzzle to solve', choices=['1', '2', 'both'], default='both')
parser.add_argument('--input', '-i', help='input file')


args = vars(parser.parse_args())

day = args['day']
input_file = args['input'] if args['input'] is not None else f'day_{day}.in'

with open(input_file) as file:
    lines = [line.rstrip() for line in file]

try:
    daily_module = import_module(f'day_{day}')
except ImportError:
    print('Specified day is invalid')
    sys.exit(1)

part_to_solve = args['part']
if part_to_solve in ('1', 'both'):
    print('Part 1 solution:', getattr(daily_module, 'resolve_part1')(lines))
if part_to_solve in ('2', 'both'):
    print('Part 2 solution:', getattr(daily_module, 'resolve_part2')(lines))
