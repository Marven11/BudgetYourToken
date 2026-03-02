import subprocess
import re

for mult in [3.5, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 50.0, 100.0, 1000.0]:
    code = f"""from challenge import Message, Billing
class State:
    def __init__(self):
        self.known_caches: list[list[tuple[str, str]]] = []
        self.prev_len: int = 0
        self.uncached_since_write: float = 0.0
_state = State()
def _msg_key(msg):
    return (msg["role"], msg["content"])
def _find_best(history):
    best = 0
    for cache in _state.known_caches:
        cl = len(cache)
        if cl > len(history) or cl <= best:
            continue
        if all(cache[i] == _msg_key(history[i]) for i in range(cl)):
            best = cl
    return best
def _register(history, length):
    key = [_msg_key(history[i]) for i in range(length)]
    for c in _state.known_caches:
        if c == key:
            return
    _state.known_caches.append(key)
def _tcr(history, s, e):
    return sum(len(history[i]["content"]) for i in range(s, e))
def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    n = len(history)
    if n == 0:
        return history
    if n < _state.prev_len:
        _state.uncached_since_write = 0
        _state.known_caches.clear()
    _state.prev_len = n
    bh = _find_best(history)
    tt = _tcr(history, 0, n)
    uc = _tcr(history, bh, n)
    if bh > 0:
        history[bh - 1]["savepoint"] = True
    else:
        history[0]["savepoint"] = True
        _register(history, 1)
    _state.uncached_since_write += uc
    if _state.uncached_since_write * 0.9 > tt * 0.25 * {mult}:
        history[n - 1]["savepoint"] = True
        _register(history, n)
        _state.uncached_since_write = 0
    return history
def billing_watcher(billing):
    return
"""
    with open("solve/claude/_sweep_tmp.py", "w") as f:
        f.write(code)
    r = subprocess.run(["python", "challenge.py", "solve.claude._sweep_tmp"], capture_output=True, text=True)
    m = re.search(r"(\d+\.\d+)%", r.stdout)
    if m:
        pct = float(m.group(1))
        bm = re.search(r"billing=(.*)", r.stdout)
        print(f"mult={mult}: {pct}% {bm.group(1) if bm else ''}")
    else:
        print(f"mult={mult}: FAILED")
