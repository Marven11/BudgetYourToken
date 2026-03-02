from typing import List
from challenge import Message, Billing

# 状态
_last_len = 0
_cleaned = False


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len, _cleaned
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    current_len = len(optimized)
    
    # 检测清理
    if _last_len > 0 and current_len < _last_len * 0.7:
        _cleaned = True
    else:
        _cleaned = False
    
    _last_len = current_len
    
    savepoint_count = 0
    
    # 总是设置系统消息为savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 如果检测到清理，在清理后的历史开头设置第二个savepoint
    if _cleaned and len(optimized) > 1:
        optimized[1]["savepoint"] = True
        savepoint_count += 1
    
    # 在历史的后半部分设置剩余savepoint
    # 选择位置：60%, 80%
    positions_pct = [0.6, 0.8]
    for pct in positions_pct:
        if savepoint_count >= 4:
            break
        if len(optimized) <= 1:
            break
        idx = int(pct * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
