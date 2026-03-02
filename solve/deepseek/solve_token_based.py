from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 累计token阈值
    thresholds = [1000, 2000, 3000, 4000]
    current_token_count = 0
    savepoint_count = 0
    
    # 遍历历史，在达到阈值时设置savepoint
    for i, msg in enumerate(optimized):
        current_token_count += len(msg["content"])
        # 检查是否达到下一个阈值
        for thresh in thresholds:
            if current_token_count >= thresh and savepoint_count < 4:
                # 在这个消息上设置savepoint
                optimized[i]["savepoint"] = True
                savepoint_count += 1
                # 移除这个阈值，避免重复设置
                thresholds.remove(thresh)
                break
        
        if savepoint_count >= 4:
            break
    
    # 如果还没有设置任何savepoint，就在系统消息设置
    if savepoint_count == 0 and len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
