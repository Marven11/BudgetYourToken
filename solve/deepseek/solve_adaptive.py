from typing import List
from challenge import Message, Billing

# 状态
_last_len = 0


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len
    
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    current_len = len(optimized)
    
    # 检测清理：如果长度显著减少（减少超过30%），认为发生了清理
    # 注意：历史长度可能因为添加消息而增加，所以只考虑减少的情况
    cleaned = False
    if _last_len > 0 and current_len < _last_len * 0.7:
        cleaned = True
    
    # 总是设置系统消息为savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 如果检测到清理，并且在清理后历史不止系统消息，则设置清理后的第一个消息为savepoint
    if cleaned and len(optimized) > 1:
        optimized[1]["savepoint"] = True
    
    _last_len = current_len
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
