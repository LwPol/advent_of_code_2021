from typing import List, NamedTuple
import functools


LITERAL_PACKET_ID = 4
SUM_PACKET_ID = 0
PRODUCT_PACKET_ID = 1
MIN_PACKET_ID = 2
MAX_PACKET_ID = 3
GT_PACKET_ID = 5
LT_PACKET_ID = 6


def get_transmission_bits(transmission):
    return ''.join(format(int(digit, 16), '04b') for digit in transmission)


def binary_to_int(bin_str):
    return int(bin_str, 2)


def take_bits(it, count):
    bits = [next(it) for _ in range(count)]
    return ''.join(bits)


class PacketHeader(NamedTuple):
    version: int
    packet_id: int


class LiteralPacket(NamedTuple):
    header: PacketHeader
    literal: int


class OperatorPacket(NamedTuple):
    header: PacketHeader
    subpackets: List


def parse_packet_header(it):
    version = binary_to_int(take_bits(it, 3))
    packet_id = binary_to_int(take_bits(it, 3))
    return PacketHeader(version, packet_id)


def parse_literal_packet_body(it):
    def literal_bits():
        while True:
            group = take_bits(it, count=5)
            yield from group[1:]
            if group[0] == '0':
                break
    return binary_to_int(''.join(literal_bits()))


def parse_operator_packet_body(it):
    length_type = next(it)
    if length_type == '0':
        total_length = binary_to_int(take_bits(it, count=15))
        return parse_subpackets_in_total_length_mode(it, total_length)
    subpackets_count = binary_to_int(take_bits(it, count=11))
    return parse_subpackets_in_numbered_mode(it, subpackets_count)


def parse_subpackets_in_total_length_mode(it, length):
    subpackets_bits = [bit for _, bit in zip(range(length), it)]
    return parse_transmission(iter(subpackets_bits))


def parse_subpackets_in_numbered_mode(it, packets_count):
    return [parse_packet(it) for _ in range(packets_count)]


def parse_packet(it):
    header = parse_packet_header(it)
    if header.packet_id == LITERAL_PACKET_ID:
        return LiteralPacket(header, parse_literal_packet_body(it))
    return OperatorPacket(header, parse_operator_packet_body(it))


def parse_transmission(it):
    packets = []
    try:
        while True:
            packets.append(parse_packet(it))
    except StopIteration:
        return packets


def sum_version_numbers(packets):
    def packet_version_sum(packet):
        if isinstance(packet, LiteralPacket):
            return packet.header.version
        return packet.header.version + sum_version_numbers(packet.subpackets)
    return sum(map(packet_version_sum, packets))


def evaluate_packet(packet):
    packet_type = packet.header.packet_id
    if packet_type == LITERAL_PACKET_ID:
        return packet.literal
    subpackets_evaluation = map(evaluate_packet, packet.subpackets)
    if packet_type == SUM_PACKET_ID:
        return sum(subpackets_evaluation)
    if packet_type == PRODUCT_PACKET_ID:
        return functools.reduce(lambda x, y: x * y, subpackets_evaluation, 1)
    if packet_type == MIN_PACKET_ID:
        return min(subpackets_evaluation)
    if packet_type == MAX_PACKET_ID:
        return max(subpackets_evaluation)
    lhs, rhs = subpackets_evaluation
    if packet_type == GT_PACKET_ID:
        return int(lhs > rhs)
    if packet_type == LT_PACKET_ID:
        return int(lhs < rhs)
    return int(lhs == rhs)


def resolve_part1(input):
    bits = get_transmission_bits(input[0])
    packets = parse_transmission(iter(bits))
    return sum_version_numbers(packets)


def resolve_part2(input):
    bits = get_transmission_bits(input[0])
    packets = parse_transmission(iter(bits))
    return evaluate_packet(packets[0])