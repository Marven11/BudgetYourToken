from typing import List
from challenge import Message, Billing

class _State:
    def __init__(self):
        self.anchor_index = 0  # 上次设置的savepoint位置（索引）
        self.last_len = 0

_STATE = _State()

def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    for msg in optimized:
        msg["savepoint"] = False
    
    if not optimized:
        return optimized
    
    # 如果历史长度减少，说明发生了清理，重置anchor_index为0
    if len(optimized) < _STATE.last_len:
        _STATE.anchor_index = 0
    
    anchor = _STATE.anchor_index
    if anchor >= len(optimized):
        anchor = len(optimized) - 1
    if anchor < 0:
        anchor = 0
    
    # 计算总token数和anchor之后的token数
    total_tokens = sum(len(msg["content"]) for msg in optimized)
    tail_tokens = sum(len(msg["content"]) for i, msg in enumerate(optimized) if i > anchor)
    
    # 阈值 = max(6000, total_tokens // 12)
    threshold = max(6000, total_tokens // 12)
    
    # 如果tail_tokens超过阈值且anchor不是最后一个，则刷新（在末尾设置savepoint）
    refresh = tail_tokens >= threshold and anchor != len(optimized) - 1
    
    # 系统消息总是savepoint
    optimized[0]["savepoint"] = True
    # anchor位置也设置savepoint
    optimized[anchor]["savepoint"] = True
    
    if refresh:
        optimized[-1]["savepoint"] = True
        _STATE.anchor_index = len(optimized) - 1
    else:
        _STATE.anchor_index = anchor
    
    _STATE.last_len = len(optimized)
    return optimized

def billing_watcher(billing: Billing) -> None:
    return
