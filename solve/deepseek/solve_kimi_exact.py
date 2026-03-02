from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 选择两个最短的消息作为额外savepoint（kimi策略）
    if len(optimized) > 1:
        # 跳过系统消息（索引0）
        candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[1:], start=1)]
        # 按长度升序，索引降序排序（和kimi完全一样）
        candidates.sort(key=lambda x: (x[1], -x[0]))
        # 取前两个（最短的两个，如果长度相同则取索引大的）
        for idx, _ in candidates[:2]:
            optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
