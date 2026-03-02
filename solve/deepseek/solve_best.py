from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 设置最多4个savepoint，覆盖40%-60%的范围，以应对清理
    # 清理起始位置在40%-60%，我们在这个范围内均匀分布savepoint
    percentages = [0.4, 0.45, 0.5, 0.55]
    savepoint_count = 0
    
    for pct in percentages:
        if savepoint_count >= 4:
            break
        idx = int(pct * (len(optimized) - 1))
        idx = max(0, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    # 确保系统消息总是savepoint（稳定基础）
    if len(optimized) > 0 and not optimized[0]["savepoint"]:
        # 如果已经有4个savepoint，需要替换一个
        # 我们替换最前面的一个（除了系统消息）
        for i in range(1, len(optimized)):
            if optimized[i]["savepoint"]:
                optimized[i]["savepoint"] = False
                optimized[0]["savepoint"] = True
                break
        else:
            # 没有其他savepoint，直接设置系统消息
            optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
