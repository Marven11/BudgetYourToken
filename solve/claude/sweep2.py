import subprocess
import re
import sys

best_pct = 100.0
best_params = None

for multiplier in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0, 10.0]:
    code = f"""from challenge import Message, Billing

class State:
    def __init__(self):
        self.known_caches: list[list[tuple[str, str]]] = []
        self.prev_len: int = 0
        self.wasted_since_write: float = 0.0

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
    if n < _state.prev_len:
        _state.wasted_since_write = 0
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
    _state.wasted_since_write += uncached_tokens
    write_cost = total_tokens * 0.25
    if _state.wasted_since_write * 0.9 > write_cost * {multiplier}:
        history[n - 1]["savepoint"] = True
        _register_cache(history, n)
        _state.wasted_since_write = 0
    return history

def billing_watcher(billing: Billing) -> None:
    return
"""
    with open("solve/claude/_sweep_tmp.py", "w") as f:
        f.write(code)
    r = subprocess.run(["python", "challenge.py", "solve.claude._sweep_tmp"], capture_output=True, text=True)
    m = re.search(r"(\d+\.\d+)%", r.stdout)
    if m:
        pct = float(m.group(1))
        print(f"multiplier={multiplier}: {pct}%")
        if pct < best_pct:
            best_pct = pct
            best_params = multiplier
    else:
        print(f"multiplier={multiplier}: FAILED - {r.stdout} {r.stderr}")

print(f"\nBest: multiplier={best_params}, {best_pct}%")
