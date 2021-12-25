import re
import itertools
from collections import Counter
from typing import Tuple
from typing import NamedTuple


POSITION_REGEX = r'Player (?:1|2) starting position: (\d+)'


class PlayerInfo(NamedTuple):
    position: int
    score: int


class GameState(NamedTuple):
    players: Tuple[PlayerInfo, PlayerInfo]
    current_player: int


def parse_positions(input):
    return tuple(int(re.match(POSITION_REGEX, pos).group(1)) for pos in input)


class DeterministicDice:
    def __init__(self):
        self.roll_count = 0
        self._seq = itertools.cycle(range(1, 101))
    

    def roll(self):
        self.roll_count += 1
        return next(self._seq)



def advance_player(player_position, amount):
    zero_based = player_position - 1
    zero_based = (zero_based + amount) % 10
    return zero_based + 1


def determine_pawn_advancement(dice):
    return sum(dice.roll() for _ in range(3))


def update_game_state(state, new_position, new_score):
    updated_player = PlayerInfo(new_position, new_score)
    players = (updated_player, state.players[1]) if state.current_player == 0 else (state.players[0], updated_player)
    next_player = (state.current_player + 1) % 2
    return GameState(players, current_player=next_player)


def play(starting_positions):
    p1, p2 = starting_positions
    state = GameState(players=(PlayerInfo(p1, score=0), PlayerInfo(p2, score=0)), current_player=0)
    dice = DeterministicDice()
    while True:
        player = state.players[state.current_player]
        next_position = advance_player(player.position, determine_pawn_advancement(dice))
        score = player.score + next_position
        state = update_game_state(state, next_position, score)
        if score >= 1000:
            break
    return state.players[state.current_player].score * dice.roll_count


QUANTUM_DICE_ROLLS = Counter(sum(dice_roll) for dice_roll in itertools.product((1, 2, 3), repeat=3))


def calculate_winning_combinations_with_dice_output(game_state, dice_output, state_cache):
    cur_player = game_state.players[game_state.current_player]
    new_pos = advance_player(cur_player.position, dice_output)
    new_score = cur_player.score + new_pos
    if new_score >= 21:
        if game_state.current_player == 0:
            return (QUANTUM_DICE_ROLLS[dice_output], 0)
        return (0, QUANTUM_DICE_ROLLS[dice_output])
    new_state = update_game_state(game_state, new_pos, new_score)
    winns_per_player = calculate_winning_combinations(new_state, state_cache)
    quantity = QUANTUM_DICE_ROLLS[dice_output]
    return tuple(winns * quantity for winns in winns_per_player)


def calculate_winning_combinations(game_state, state_cache):
    if game_state in state_cache:
        return state_cache[game_state]

    p1_wins, p2_wins = 0, 0
    for possible_sum in QUANTUM_DICE_ROLLS.keys():
        p1, p2 = calculate_winning_combinations_with_dice_output(game_state, possible_sum, state_cache)
        p1_wins += p1
        p2_wins += p2
    state_cache[game_state] = (p1_wins, p2_wins)
    return (p1_wins, p2_wins)


def resolve_part1(input):
    return play(parse_positions(input))


def resolve_part2(input):
    pos1, pos2 = parse_positions(input)
    starting_state = GameState(players=(PlayerInfo(pos1, score=0), PlayerInfo(pos2, score=0)), current_player=0)
    return max(calculate_winning_combinations(starting_state, state_cache={}))