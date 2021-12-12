from nmigen import *
from typing import List

def to_formatted_hex(n: int):
    res = f'{n:064X}'

    res = list(res)
    for i in range(len(res)-1, 0, -1):
        if i % 2 == 0:
            res.insert(i, '_')

    return ''.join(res)
