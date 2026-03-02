from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息和最后一个消息设为savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    if len(optimized) > 1:
        optimized[-1]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
