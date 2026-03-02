from typing import TypedDict


class Message(TypedDict):
    content: str
    role: str
    savepoint: bool


class _State:
    def __init__(self) -> None:
        self.anchor_index = 0
        self.last_len = 0


STATE = _State()


def _token_count_range(history: list[Message], start: int, end: int) -> int:
    total = 0
    for i in range(start, end):
        total += len(history[i]["content"])
    return total


def optimizer(history: list[Message]) -> list[Message]:
    if not history:
        return history
    for message in history:
        message["savepoint"] = False
    if len(history) < STATE.last_len:
        STATE.anchor_index = 0
    anchor = STATE.anchor_index
    if anchor >= len(history):
        anchor = len(history) - 1
    if anchor < 0:
        anchor = 0
    total_tokens = _token_count_range(history, 0, len(history))
    tail_tokens = _token_count_range(history, anchor + 1, len(history))
    threshold = max(6000, total_tokens // 12)
    refresh = tail_tokens >= threshold and anchor != len(history) - 1
    history[0]["savepoint"] = True
    history[anchor]["savepoint"] = True
    if refresh:
        history[-1]["savepoint"] = True
        STATE.anchor_index = len(history) - 1
    else:
        STATE.anchor_index = anchor
    STATE.last_len = len(history)
    return history


def billing_watcher(_: dict) -> None:
    return
