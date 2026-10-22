from calc.ops import add, div


def mean(values):
    total = 0
    for v in values:
        total = add(total, v)
    return total / len(values)


def median(values):
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid] + s[mid + 1]) / 2


def spread(values):
    return max(values) - min(values)
