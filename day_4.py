from dataclasses import dataclass


@dataclass
class BoardField:
    value: int
    is_marked: bool


def board_lines(input):
    board_start = 2
    while board_start < len(input):
        yield input[board_start:board_start+5]
        board_start += 6


def parse_board(board_lines):
    return [[BoardField(value=int(num), is_marked=False) for num in line.split()] for line in board_lines]


def parse_input(input):
    drawed_numbers = [int(num) for num in input[0].split(',')]
    boards = [parse_board(board) for board in board_lines(input)]
    return (drawed_numbers, boards)


def rows(board):
    yield from board


def columns(board):
    yield from ([row[idx] for row in board] for idx in range(5))


def enumerate_board_numbers(board):
    for row in rows(board):
        yield from row


def is_winning_board(board):
    def is_any_row_marked():
        return any(all(field.is_marked for field in row) for row in rows(board))
    def is_any_column_marked():
        return any(all(field.is_marked for field in column) for column in columns(board))
    return is_any_row_marked() or is_any_column_marked()


def find_winner(boards):
    return next(filter(is_winning_board, boards), None)


def mark_number(boards, number):
    for board in boards:
        to_be_marked = next(filter(lambda field: field.value == number, enumerate_board_numbers(board)), None)
        if to_be_marked is not None:
            to_be_marked.is_marked = True


class WinningBingoBoardSeeker:
    def __init__(self):
        self.winner = None
        self.last_called = None
    

    def find(self, boards, numbers):
        drawing = iter(numbers)
        while not self.is_any_board_winning(boards):
            self.last_called = next(drawing)
            mark_number(boards, self.last_called)
        return self.winner
    

    def is_any_board_winning(self, boards):
        self.winner = find_winner(boards)
        return self.winner is not None


class LosingBingoBoardSeeker:
    def __init__(self):
        self.last_called = None
    

    def find(self, boards, numbers):
        drawing = iter(numbers)
        while not self.is_only_single_board_left(boards):
            self.last_called = next(drawing)
            mark_number(boards, self.last_called)
            boards = list(filter(lambda board: not is_winning_board(board), boards))
        loser_board = boards[0]
        while not is_winning_board(loser_board):
            self.last_called = next(drawing)
            mark_number(boards, self.last_called)
        return loser_board
    

    def is_only_single_board_left(self, boards):
        return len(boards) == 1


def calculate_score(board, last_called):
    def is_unmarked(field):
        return not field.is_marked
    unmarked = sum(field.value for field in filter(is_unmarked, enumerate_board_numbers(board)))
    return unmarked * last_called


def solve_bingo_puzzle(input, bingo_seeker):
    numbers, boards = parse_input(input)
    board_of_interest = bingo_seeker.find(boards, numbers)
    return calculate_score(board_of_interest, bingo_seeker.last_called)


def resolve_part1(input):
    return solve_bingo_puzzle(input, WinningBingoBoardSeeker())


def resolve_part2(input):
    return solve_bingo_puzzle(input, LosingBingoBoardSeeker())