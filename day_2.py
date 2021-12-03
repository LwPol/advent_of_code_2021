class PositionResolverA:
    def __init__(self):
        self.x = 0
        self.y = 0


    def forward(self, units):
        self.x += units
    

    def down(self, units):
        self.y += units
    

    def up(self, units):
        self.y -= units


class PositionResolverB:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.aim = 0
    

    def forward(self, units):
        self.x += units
        self.y += self.aim * units
    

    def down(self, units):
        self.aim += units
    

    def up(self, units):
        self.aim -= units


def go(course, resolver):
    for line in course:
        command, units = line.split()
        getattr(resolver, command)(int(units))
    return resolver.x * resolver.y


def resolve_part1(input):
    return go(input, PositionResolverA())


def resolve_part2(input):
    return go(input, PositionResolverB())