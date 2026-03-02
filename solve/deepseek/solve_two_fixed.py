from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 第二个savepoint在70%位置
    if len(optimized) > 1:
        idx = int(0.7 * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))
        optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
