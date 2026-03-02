from typing import List
from challenge import Message, Billing

# 状态
_last_len = 0
_cleaned = False
_reset_counter = 0  # 清理后经过的轮数


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len, _cleaned, _reset_counter
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    current_len = len(optimized)
    
    # 检测清理
    if _last_len > 0 and current_len < _last_len * 0.7:
        _cleaned = True
        _reset_counter = 0  # 重置计数器
    else:
        _cleaned = False
    
    _last_len = current_len
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 清理后，在清理后的历史中选择短消息作为savepoint
    # 清理后历史从中间开始，我们只考虑后50%的消息（更可能保留）
    if _cleaned:
        # 重置后，重新选择savepoint
        # 选择两个最短的消息（除了系统消息）
        if len(optimized) > 1:
            candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[1:], start=1)]
            candidates.sort(key=lambda x: (x[1], -x[0]))  # 长度升序，索引降序
            for idx, _ in candidates[:2]:
                optimized[idx]["savepoint"] = True
    else:
        # 没有清理，继续使用现有的savepoint策略
        # 但为了不超过4个，我们只设置系统消息
        # 或者，如果_reset_counter较小，可以添加额外的savepoint
        if _reset_counter < 10 and len(optimized) > 1:  # 清理后前10轮
            # 在历史的后半部分选择短消息
            start_idx = max(1, len(optimized) // 2)
            candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[start_idx:], start=start_idx)]
            candidates.sort(key=lambda x: (x[1], -x[0]))
            for idx, _ in candidates[:2]:
                optimized[idx]["savepoint"] = True
    
    _reset_counter += 1
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
