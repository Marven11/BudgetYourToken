from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 设置4个savepoint在较大的token阈值
    thresholds = [10000, 20000, 30000, 40000]
    current_token_count = 0
    savepoint_count = 0
    
    for i, msg in enumerate(optimized):
        current_token_count += len(msg["content"])
        # 检查是否达到下一个阈值
        for thresh in thresholds:
            if current_token_count >= thresh and savepoint_count < 4:
                optimized[i]["savepoint"] = True
                savepoint_count += 1
                thresholds.remove(thresh)
                break
        
        if savepoint_count >= 4:
            break
    
    # 如果没有达到阈值，在系统消息设置
    if savepoint_count == 0 and len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
