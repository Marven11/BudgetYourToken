from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 策略：设置4个savepoint，覆盖从30%到90%的范围
    # 清理保留40%-60%，所以savepoint应该在这个范围或之后
    percentages = [0.3, 0.5, 0.7, 0.9]
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
