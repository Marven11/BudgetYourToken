from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 设置最多4个savepoint在固定百分比位置
    percentages = [0.0, 0.2, 0.4, 0.6]  # 0%, 20%, 40%, 60%
    savepoint_count = 0
    
    for pct in percentages:
        if savepoint_count >= 4:
            break
        idx = int(pct * (len(optimized) - 1))  # -1 因为索引从0开始
        idx = max(0, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    # 确保至少有一个savepoint（系统消息）
    if savepoint_count == 0 and len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
