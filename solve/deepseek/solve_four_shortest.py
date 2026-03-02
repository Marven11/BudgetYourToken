from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 选择三个最短的消息作为额外savepoint（共4个，包括系统消息）
    if len(optimized) > 1:
        # 跳过系统消息（索引0）
        candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[1:], start=1)]
        # 按长度升序，索引降序排序（和kimi一样）
        candidates.sort(key=lambda x: (x[1], -x[0]))
        # 取前三个（最短的三个，如果长度相同则取索引大的）
        for idx, _ in candidates[:3]:
            optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
