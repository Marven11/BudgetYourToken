from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 在后50%的消息中选择三个最短的
    if len(optimized) > 1:
        start_idx = max(1, len(optimized) // 2)  # 从中间开始
        candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[start_idx:], start=start_idx)]
        # 按长度升序，索引降序排序（与kimi相同）
        candidates.sort(key=lambda x: (x[1], -x[0]))
        # 取前三个
        for idx, _ in candidates[:3]:
            optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
