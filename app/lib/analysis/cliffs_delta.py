def get_cliffsdelta(x, y):
    m, n = len(x), len(y)
    y = sorted(y)
    j = more = less = 0
    for (repeats, item) in _get_chunks(sorted(x)):
        while j <= (n - 1) and y[j] < item:
            j += 1
        more += (j * repeats)
        while j <= (n - 1) and y[j] == item:
            j += 1
        less += ((n - j) * repeats)
    d = (more - less) / (m * n)
    return abs(d)


def get_magnitude(delta):
    if delta < 0.147:
        return 'negligible'
    if 0.147 <= delta < 0.33:
        return 'small'
    if 0.33 <= delta < 0.474:
        return 'medium'
    return 'large'


def _get_chunks(data):
    for (j, two) in enumerate(data):
        if j == 0:
            one, i = two, 0
        if one != two:
            yield (j - i), one
            i = j
        one = two
    yield (j - i + 1), two
