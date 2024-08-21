from typing import Callable, List

_warmup_fns: List[Callable] = []

def register_warmup_fn():
    def outer(fn: Callable):
        if fn not in _warmup_fns:
            _warmup_fns.append(fn)
        return fn
    return outer

def warmup():
    for fn in _warmup_fns:
        fn()
