from challenge import Message, Billing


class State:
    def __init__(self):
        self.known_caches: list[list[tuple[str, str]]] = []
        self.prev_len: int = 0
        self.uncached_since_write: float = 0.0
        self.calls_since_write: int = 0


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

    truncated = n < _state.prev_len
    if truncated:
        _state.uncached_since_write = 0
        _state.calls_since_write = 0
        _state.known_caches.clear()

    _state.prev_len = n
    _state.calls_since_write += 1

    best_hit = _find_best_cache_hit_len(history)
    total_tokens = _token_count_range(history, 0, n)
    uncached_tokens = _token_count_range(history, best_hit, n)

    if best_hit > 0:
        history[best_hit - 1]["savepoint"] = True
    else:
        history[0]["savepoint"] = True
        _register_cache(history, 1)

    _state.uncached_since_write += uncached_tokens

    uncached_ratio = uncached_tokens / total_tokens if total_tokens > 0 else 0
    write_cost = total_tokens * 0.25
    should_write = False
    if best_hit == 0 and _state.calls_since_write >= 2:
        should_write = True
    elif _state.uncached_since_write * 0.9 > write_cost * 3.5:
        should_write = True

    if should_write:
        history[n - 1]["savepoint"] = True
        _register_cache(history, n)
        _state.uncached_since_write = 0
        _state.calls_since_write = 0

    return history


def billing_watcher(billing: Billing) -> None:
    return
