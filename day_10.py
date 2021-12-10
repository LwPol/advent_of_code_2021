BRACKET_MATCHES = {
    '(': ')',
    '[': ']',
    '{': '}',
    '<': '>',
}


def find_first_incorrect_closing(chunks):
    opened_chunks = []
    for char in chunks:
        if char in BRACKET_MATCHES.keys():
            opened_chunks.append(char)
        else:
            chunk_opening = opened_chunks.pop()
            if char != BRACKET_MATCHES[chunk_opening]:
                return char
    return None


def score_syntax_errors(navigation):
    score_table = {')': 3, ']': 57, '}': 1197, '>': 25137}
    broken_brackets = filter(lambda x: x is not None, map(find_first_incorrect_closing, navigation))
    return sum(score_table[illegal] for illegal in broken_brackets)


def filter_incomplete_lines(navigation):
    return filter(lambda chunks: find_first_incorrect_closing(chunks) is None, navigation)


def find_chunks_completion(chunks):
    opened_chunks = []
    for char in chunks:
        if char in BRACKET_MATCHES.keys():
            opened_chunks.append(char)
        else:
            opened_chunks.pop()
    opened_chunks.reverse()
    return [BRACKET_MATCHES[opening] for opening in opened_chunks]


def score_completion(completion):
    score_table = {')': 1, ']': 2, '}': 3, '>': 4}
    score = 0
    for bracket in completion:
        score = 5 * score + score_table[bracket]
    return score


def get_middle_score(completions):
    scoretable = sorted(map(score_completion, completions))
    return scoretable[len(scoretable) // 2]


def resolve_part1(input):
    return score_syntax_errors(input)


def resolve_part2(input):
    completions = map(find_chunks_completion, filter_incomplete_lines(input))
    return get_middle_score(completions)