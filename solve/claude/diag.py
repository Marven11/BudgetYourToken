from challenge import Message, Billing
import sys

class State:
    def __init__(self):
        self.known_caches: list[list[tuple[str, str]]] = []
        self.prev_len: int = 0
        self.uncached_since_write: float = 0.0
        self.call_num: int = 0
        self.writes: list[tuple[int, int, int, int]] = []
        self.truncations: list[tuple[int, int]] = []

_state = State()

def _msg_key(msg: Message) -> tuple[str, str]:
    return (msg["role"], msg["content"])

def _find_best_cache_hit_len(history: list[Message]) -> int:
    best = 0
    for cache in _state.known_caches:
        cl = len(cache)
        if cl > len(history) or cl <= best:
            continue
        if all(cache[i] == _msg_key(history[i]) for i in range(cl)):
            best = cl
    return best

def _register_cache(history: list[Message], length: int) -> None:
    key = [_msg_key(history[i]) for i in range(length)]
    for cache in _state.known_caches:
        if cache == key:
            return
    _state.known_caches.append(key)

def _token_count_range(history: list[Message], start: int, end: int) -> int:
    return sum(len(history[i]["content"]) for i in range(start, end))

def optimizer(history: list[Message]) -> list[Message]:
    for msg in history:
        msg["savepoint"] = False
    n = len(history)
    if n == 0:
        return history
    _state.call_num += 1
    truncated = n < _state.prev_len
    if truncated:
        _state.truncations.append((_state.call_num, n))
        _state.uncached_since_write = 0
        _state.known_caches.clear()
    _state.prev_len = n
    best_hit = _find_best_cache_hit_len(history)
    total_tokens = _token_count_range(history, 0, n)
    uncached_tokens = _token_count_range(history, best_hit, n)
    if best_hit > 0:
        history[best_hit - 1]["savepoint"] = True
    else:
        history[0]["savepoint"] = True
        _register_cache(history, 1)
    _state.uncached_since_write += uncached_tokens
    write_cost = total_tokens * 0.25
    if _state.uncached_since_write * 0.9 > write_cost * 3.5:
        history[n - 1]["savepoint"] = True
        _register_cache(history, n)
        _state.writes.append((_state.call_num, total_tokens, uncached_tokens, best_hit))
        _state.uncached_since_write = 0
    return history

def billing_watcher(billing: Billing) -> None:
    return

import atexit
def _dump():
    print(f"Truncations: {len(_state.truncations)}", file=sys.stderr)
    for t in _state.truncations[:10]:
        print(f"  call={t[0]} new_len={t[1]}", file=sys.stderr)
    print(f"Writes: {len(_state.writes)}", file=sys.stderr)
    for w in _state.writes[:20]:
        print(f"  call={w[0]} total={w[1]} uncached={w[2]} best_hit_len={w[3]}", file=sys.stderr)
    gaps = []
    prev = 0
    for w in _state.writes:
        gaps.append(w[0] - prev)
        prev = w[0]
    if gaps:
        print(f"Write gaps: min={min(gaps)} max={max(gaps)} avg={sum(gaps)/len(gaps):.1f}", file=sys.stderr)
atexit.register(_dump)
