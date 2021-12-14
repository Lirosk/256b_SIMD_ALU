from nmigen import *
from typing import List

def to_formatted_hex(n: int):
    res = f'{n:064X}'

    res = list(res)
    for i in range(len(res)-1, 0, -1):
        if i % 2 == 0:
            res.insert(i, '_')

    return ''.join(res)

def to_hex(n: int):
    res = f'{n:X}'

    res = list(res)
    l = len(res)
    for i in range(l-1, 0, -1):
        if (l-i) % 2 == 0:
            res.insert(i, '_')

    if res[1] == '_':
        res.insert(0, '0')

    return ''.join(res)
