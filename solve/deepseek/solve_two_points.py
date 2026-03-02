from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 第一个savepoint：系统消息
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 第二个savepoint：在80%位置
    if len(optimized) > 1:
        idx = int(0.8 * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))  # 避免和系统消息重复
        optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
