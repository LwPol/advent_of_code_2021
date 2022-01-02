from typing import List, NamedTuple, Union
from itertools import dropwhile, combinations, starmap, chain, filterfalse
import heapq


def parse_amphipods_positions(input):
    def amphipods():
        for room_idx, column in enumerate(range(3, 10, 2)):
            yield input[2][column], SideRoomPosition(room_idx, 0)
            yield input[3][column], SideRoomPosition(room_idx, 1)
    return [AmphipodPosition(amph, pos) for amph, pos in amphipods()]


def unfold(amphipod_positions):
    def transform_second_row(amphipod_pos):
        if amphipod_pos.position.place == 1:
            return AmphipodPosition(amphipod_pos.amphipod, SideRoomPosition(amphipod_pos.position.room, place=3))
        return amphipod_pos
    def added_from_unfold():
        for room_idx, amphipods in enumerate(('DD', 'CB', 'BA', 'AC')):
            yield AmphipodPosition(amphipods[0], SideRoomPosition(room_idx, place=1))
            yield AmphipodPosition(amphipods[1], SideRoomPosition(room_idx, place=2))
    return list(chain(map(transform_second_row, amphipod_positions), added_from_unfold()))


HALLWAY_STOPS = [0, 1, 3, 5, 7, 9, 10]


class SideRoomPosition(NamedTuple):
    room: int
    place: int


class HallwayPosition(NamedTuple):
    value: int


class AmphipodPosition(NamedTuple):
    amphipod: str
    position: Union[SideRoomPosition, HallwayPosition]


class Node(NamedTuple):
    diagram: "AmphipodsDiagram"
    energy_used: int
    heuristic: int

    def __lt__(self, other):
        return self.energy_used + self.heuristic < other.energy_used + other.heuristic


class AmphipodsDiagram:
    def __init__(self, amphipod_positions: List[AmphipodPosition], sideroom_depth):
        self._sideroom_depth = sideroom_depth
        self._hallway = [None for _ in range(11)]
        self._siderooms = [[None for _ in range(sideroom_depth)] for _ in range(4)]
        for amphipod_pos in amphipod_positions:
            if isinstance(amphipod_pos.position, HallwayPosition):
                self._hallway[amphipod_pos.position.value] = amphipod_pos.amphipod
            else:
                room, place = amphipod_pos.position
                self._siderooms[room][place] = amphipod_pos.amphipod


    def generate_new_positions(self):
        move_into_target = self._find_move_towards_target_sideroom()
        if move_into_target is not None:
            yield move_into_target
            return
        for position in self._enumerate_movable_sideroom_positions():
            yield from ((position, destination) for destination in self._generate_moves_from_sideroom_to_hallway(position))


    def calculate_reorganization_heuristic(self):
        def min_energy_cost(amphipod, position):
            if isinstance(position, SideRoomPosition) and is_in_own_room(position, amphipod):
                return 0
            target_room = get_target_room(amphipod)
            return evaluate_used_energy((position, SideRoomPosition(target_room, 0)), amphipod)
        return sum(min_energy_cost(self._get_amphipod_at(pos), pos) for pos in self._enumerate_amphipods_positions())


    def apply_amphipod_move(self, source, destination):
        def transform_source_to_dest(position):
            return destination if position == source else position
        amphipods = [AmphipodPosition(self._get_amphipod_at(pos), transform_source_to_dest(pos))
            for pos in self._enumerate_amphipods_positions()]
        return (AmphipodsDiagram(amphipods, self._sideroom_depth),
            evaluate_used_energy((source, destination), self._get_amphipod_at(source)))


    def is_hallway_stuck(self):
        hallway_positions = [idx for idx, amph in enumerate(self._hallway) if amph is not None]
        return any(self._are_blocking_each_other_in_hallway(*comb) for comb in combinations(hallway_positions, 2))


    def are_all_amphipods_in_destination(self):
        def check_sideroom(sideroom, expected_type):
            return all(amphipod == expected_type for amphipod in sideroom)
        return all(starmap(check_sideroom, zip(self._siderooms, ('A', 'B', 'C', 'D'))))


    def _are_blocking_each_other_in_hallway(self, idx1, idx2):
        amphipods = self._hallway[idx1], self._hallway[idx2]
        dest1, dest2 = (side_room_exit_in_hallway(get_target_room(amph)) for amph in amphipods)
        def is_between(value, interval):
            begin, end = sorted(interval)
            return value > begin and value < end
        return is_between(idx2, (idx1, dest1)) and is_between(idx1, (idx2, dest2))


    def _enumerate_amphipods_positions(self):
        return chain(self._enumerate_hallway_positions(), self._enumerate_sideroom_positions())
    

    def _enumerate_hallway_positions(self):
        return (HallwayPosition(idx) for idx, value in enumerate(self._hallway) if value is not None)
    

    def _enumerate_sideroom_positions(self):
        for room_idx, sideroom in enumerate(self._siderooms):
            yield from (SideRoomPosition(room_idx, place_idx) for place_idx, value in enumerate(sideroom) if value is not None)
    

    def _enumerate_movable_sideroom_positions(self):
        def is_unmovable(position):
            return self._is_stuck_in_sideroom(position) or self._is_in_proper_place(position)
        return filterfalse(is_unmovable, self._enumerate_sideroom_positions())
    

    def _generate_moves_from_sideroom_to_hallway(self, sideroom_position):
        hallway_enter = side_room_exit_in_hallway(sideroom_position.room)
        return (HallwayPosition(pos) for pos in HALLWAY_STOPS if self._is_hallway_path_possible(hallway_enter, pos))


    def _find_move_towards_target_sideroom(self):
        for hallway_pos in self._enumerate_hallway_positions():
            sideroom_pos = self._find_move_from_hallway_to_target_sideroom(hallway_pos.value, self._hallway[hallway_pos.value])
            if sideroom_pos is not None:
                return (hallway_pos, sideroom_pos)
        for sideroom_pos in self._enumerate_movable_sideroom_positions():
            target_pos = self._find_move_from_sideroom_to_target_sideroom(sideroom_pos)
            if target_pos is not None:
                return (sideroom_pos, target_pos)
        return None
    

    def _find_move_from_hallway_to_target_sideroom(self, hallway_index, amphipod):
        target_room = get_target_room(amphipod)
        def is_at_destination(indexed_amphipod):
            return indexed_amphipod[1] == amphipod
        indexed_room = list(enumerate(self._siderooms[target_room]))
        idx, value = next(dropwhile(is_at_destination, reversed(indexed_room)))
        if value is None and self._is_hallway_path_possible(hallway_index, side_room_exit_in_hallway(target_room)):
            return SideRoomPosition(target_room, place=idx)
        return None


    def _find_move_from_sideroom_to_target_sideroom(self, sideroom_position):
        amphipod = self._siderooms[sideroom_position.room][sideroom_position.place]
        hallway_entry = side_room_exit_in_hallway(sideroom_position.room)
        return self._find_move_from_hallway_to_target_sideroom(hallway_entry, amphipod)


    def _get_amphipod_at(self, position):
        if isinstance(position, SideRoomPosition):
            return self._siderooms[position.room][position.place]
        return self._hallway[position.value]
    

    def _is_in_proper_place(self, sideroom_pos):
        amphipod = self._siderooms[sideroom_pos.room][sideroom_pos.place]
        if not is_in_own_room(sideroom_pos, amphipod):
            return False
        room = self._siderooms[sideroom_pos.room]
        return all(amphipod_below == amphipod for amphipod_below in room[sideroom_pos.place + 1:])
    

    def _is_stuck_in_sideroom(self, sideroom_pos):
        return sideroom_pos.place > 0 and self._siderooms[sideroom_pos.room][sideroom_pos.place - 1] is not None
    

    def _is_hallway_path_possible(self, source, destination):
       direction = 1 if destination > source else -1
       while source != destination:
           source += direction
           if source in HALLWAY_STOPS and self._hallway[source] is not None:
               return False
       return True


    def __str__(self):
        def transform_list(l):
            return ''.join('.' if value is None else value for value in l)
        hallway = transform_list(self._hallway)
        siderooms = ';'.join(transform_list(sideroom) for sideroom in self._siderooms)
        return hallway + ';' + siderooms
    

    def __repr__(self):
        return self.__str__()
    

    def __hash__(self):
        return hash(str(self))
    

    def __eq__(self, other):
        return str(self) == str(other)


def calculate_distance(pos1, pos2):
    if isinstance(pos1, SideRoomPosition):
        room, place = pos1
        return place + 1 + calculate_distance(HallwayPosition(side_room_exit_in_hallway(room)), pos2)
    if isinstance(pos2, SideRoomPosition):
        room, place = pos2
        return place + 1 + calculate_distance(pos1, HallwayPosition(side_room_exit_in_hallway(room)))
    return abs(pos2.value - pos1.value)


def evaluate_used_energy(move, amphipod):
    return calculate_distance(*move) * get_step_energy_cost(amphipod)


def get_target_room(amphipod):
    return {'A': 0, 'B': 1, 'C': 2, 'D': 3}[amphipod]


def get_step_energy_cost(amphipod):
    return {'A': 1, 'B': 10, 'C': 100, 'D': 1000}[amphipod]


def side_room_exit_in_hallway(side_room_idx):
    return (2, 4, 6, 8)[side_room_idx]


def is_in_own_room(sideroom_position, amphipod):
    return sideroom_position.room == get_target_room(amphipod)


def generate_diagram_continuations(diagram: AmphipodsDiagram):
    continuations = starmap(diagram.apply_amphipod_move, diagram.generate_new_positions())
    return filter(lambda entry: not entry[0].is_hallway_stuck(), continuations)


class AStarAlgorithm:
    def __init__(self):
        self._visited_diagrams = set()
        self._current_node = None
    

    def run(self, starting_diagram):
        nodes = [self._create_node(starting_diagram, energy_used=0)]
        while not self._is_target_reached(nodes):
            if self._current_node.diagram in self._visited_diagrams:
                continue
            for diagram, cost in generate_diagram_continuations(self._current_node.diagram):
                if diagram in self._visited_diagrams:
                    continue
                heapq.heappush(nodes, self._create_node(diagram, self._current_node.energy_used + cost))
            self._visited_diagrams.add(self._current_node.diagram)
        return self._current_node.energy_used


    def _is_target_reached(self, nodes):
        self._current_node = heapq.heappop(nodes)
        return self._current_node.diagram.are_all_amphipods_in_destination()
    

    def _create_node(self, diagram: AmphipodsDiagram, energy_used):
        return Node(diagram, energy_used, heuristic=diagram.calculate_reorganization_heuristic())


def resolve_part1(input):
    diagram = AmphipodsDiagram(parse_amphipods_positions(input), sideroom_depth=2)
    return AStarAlgorithm().run(diagram)


def resolve_part2(input):
    diagram = AmphipodsDiagram(unfold(parse_amphipods_positions(input)), sideroom_depth=4)
    return AStarAlgorithm().run(diagram)