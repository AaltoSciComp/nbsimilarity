def reversed_string(x):
    return ''.join(reversed(x))

def remove_common_parts(x):
    i = common_prefix_length(x)
    x = tuple(a[i:] for a in x)
    i = common_prefix_length(tuple(reversed_string(a) for a in x))
    x = tuple(a[:-i] if i!=0 else a for a in x)
    return x

def common_prefix_length(x):
    x = tuple(x)  # ensure we can iterate multiple times
    first = min(x)
    last = max(x)
    for i in range(len(first)):
        if first[:i] != last[:i]:
            return i - 1
    return len(first)
