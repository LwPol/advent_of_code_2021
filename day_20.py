import itertools


def parse_image(input):
    lit_pixels = set()
    for y, line in enumerate(input):
        for x, char in enumerate(line):
            if char == '#':
                lit_pixels.add((x, y))
    return lit_pixels


def parse_input(input):
    enhancement_algo = input[0]
    image = parse_image(input[2:])
    return (enhancement_algo, image)


def enumerate_subimage_pixels(limits):
    upper_left, lower_right = limits
    return itertools.product(range(upper_left[0], lower_right[0] + 1), range(upper_left[1], lower_right[1] + 1))


def enumerate_3x3_grid(middle_point):
    mx, my = middle_point
    for y in (my - 1, my, my + 1):
        for x in (mx - 1, mx, mx + 1):
            yield (x, y)


class InfiniteImage:
    def __init__(self, pixels, is_lit_pixels_map):
        self._pixels = pixels
        self._lit_pixels_stored = is_lit_pixels_map
    

    def get_subimage_limits(self):
        min_x = min(point[0] for point in self._pixels) - 2
        min_y = min(point[1] for point in self._pixels) - 2
        max_x = max(point[0] for point in self._pixels) + 2
        max_y = max(point[1] for point in self._pixels) + 2
        return ((min_x, min_y), (max_x, max_y))
    

    def is_pixel_lit(self, pixel):
        if self._lit_pixels_stored:
            return pixel in self._pixels
        return pixel not in self._pixels
    

    def enhance(self, pattern):
        lit_pixels_storage = self._will_resulting_image_store_lit_pixels(pattern)
        pixels = set()
        def should_be_stored(pixel_value):
            if lit_pixels_storage:
                return pixel_value == '#'
            return pixel_value == '.'
        for pixel in enumerate_subimage_pixels(self.get_subimage_limits()):
            binary = [int(self.is_pixel_lit(p)) for p in enumerate_3x3_grid(pixel)]
            index = int(''.join(str(bit) for bit in binary), 2)
            if should_be_stored(pattern[index]):
                pixels.add(pixel)
        return InfiniteImage(pixels, lit_pixels_storage)
    

    def lit_pixels_count(self):
        if self._lit_pixels_stored:
            return len(self._pixels)
        raise RuntimeError('Infinite amount of lit pixels')


    def _will_resulting_image_store_lit_pixels(self, pattern):
        if self._lit_pixels_stored:
            return pattern[0] == '.'
        return pattern[-1] == '.'


def repeat_enhancement(enhancement_algo, image, iterations):
    for _ in range(iterations):
        image = image.enhance(enhancement_algo)
    return image


def resolve_part1(input):
    algo, pixels = parse_input(input)
    return repeat_enhancement(algo, InfiniteImage(pixels, is_lit_pixels_map=True), iterations=2).lit_pixels_count()


def resolve_part2(input):
    algo, pixels = parse_input(input)
    return repeat_enhancement(algo, InfiniteImage(pixels, is_lit_pixels_map=True), iterations=50).lit_pixels_count()