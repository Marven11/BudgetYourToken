from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 设置4个savepoint：系统消息，以及后50%部分的三个点
    percentages = [0.0, 0.6, 0.7, 0.8]
    savepoint_count = 0
    
    for pct in percentages:
        if savepoint_count >= 4:
            break
        if len(optimized) == 0:
            break
        idx = int(pct * (len(optimized) - 1))
        idx = max(0, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    # 如果历史很短，可能重复，确保至少有一个
    if savepoint_count == 0 and len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
