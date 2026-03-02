from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 在40%-60%范围内设置4个savepoint
    percentages = [0.4, 0.45, 0.5, 0.55]
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
    
    # 确保至少有一个
    if savepoint_count == 0 and len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
