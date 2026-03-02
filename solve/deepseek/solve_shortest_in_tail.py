from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 只考虑历史的后60%的消息（因为清理保留后40%-60%，所以后60%很可能保留）
    start_idx = max(1, int(len(optimized) * 0.4))  # 从40%位置开始，跳过系统消息
    if start_idx < len(optimized):
        # 收集候选（索引，长度）
        candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[start_idx:], start=start_idx)]
        # 按长度升序，索引降序排序
        candidates.sort(key=lambda x: (x[1], -x[0]))
        # 取前三个最短的
        for idx, _ in candidates[:3]:
            optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
