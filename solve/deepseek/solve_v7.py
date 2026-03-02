from typing import List
from challenge import Message, Billing

# 状态
_history_len_tracker = []
_cleaned = False


def optimizer(history: List[Message]) -> List[Message]:
    global _history_len_tracker, _cleaned
    
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 检测清理
    current_len = len(optimized)
    _history_len_tracker.append(current_len)
    if len(_history_len_tracker) > 10:
        _history_len_tracker.pop(0)
    
    # 如果长度突然减少，说明发生了清理
    if len(_history_len_tracker) >= 2:
        prev_len = _history_len_tracker[-2]
        if current_len < prev_len * 0.7:  # 长度减少超过30%
            _cleaned = True
        else:
            _cleaned = False
    
    # 设置savepoint
    # 策略：在可能的清理起始位置附近设置savepoint
    # 清理起始在40%-60%，我们覆盖这个范围
    positions_pct = [0.4, 0.45, 0.5, 0.55, 0.6]
    savepoint_count = 0
    
    for pct in positions_pct:
        if savepoint_count >= 4:
            break
        idx = int(pct * (len(optimized) - 1))
        idx = max(0, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    # 如果还没有savepoint（历史太短），在最后一个设置
    if savepoint_count == 0 and len(optimized) > 0:
        optimized[-1]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    # 可以记录billing用于调整，但这里先简单处理
    pass
