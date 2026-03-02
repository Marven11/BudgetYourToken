from typing import List
from challenge import Message, Billing

# 状态
_history_length_tracker = []
_epoch = 0  # 当前epoch（每次清理增加）
_savepoint_positions = []  # 当前epoch的savepoint位置（索引列表）
_current_token_count = 0  # 当前epoch累计token
_token_thresholds = [10000, 25000, 40000, 55000]  # token阈值


def optimizer(history: List[Message]) -> List[Message]:
    global _history_length_tracker, _epoch, _savepoint_positions, _current_token_count
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    current_len = len(optimized)
    _history_length_tracker.append(current_len)
    if len(_history_length_tracker) > 10:
        _history_length_tracker.pop(0)
    
    # 检测清理：如果长度突然减少超过30%
    cleaned = False
    if len(_history_length_tracker) >= 2:
        prev_len = _history_length_tracker[-2]
        if current_len < prev_len * 0.7:
            cleaned = True
    
    if cleaned:
        # 新的epoch开始
        _epoch += 1
        _savepoint_positions = []
        _current_token_count = 0
        # 在新epoch开始时，系统消息是第一个savepoint
        if len(optimized) > 0:
            optimized[0]["savepoint"] = True
            _savepoint_positions.append(0)
    
    # 计算当前epoch的token累计（从清理后开始）
    # 由于不知道确切清理位置，我们假设清理后历史从当前历史的前部开始
    # 实际上，清理后历史 = 系统消息 + 历史[保留起始:]
    # 保留起始在40%-60%之间
    # 为了简化，我们重新计算token累计
    
    # 如果没有在清理检测中设置系统消息，这里设置
    if len(optimized) > 0 and not optimized[0]["savepoint"]:
        optimized[0]["savepoint"] = True
        if 0 not in _savepoint_positions:
            _savepoint_positions.append(0)
    
    # 遍历历史，在达到阈值时设置savepoint
    # 我们从后往前遍历，因为清理后历史从中间开始，前面的消息可能已被丢弃
    # 但我们不知道确切位置，所以从开始遍历
    temp_token_count = 0
    savepoint_count = len([i for i in _savepoint_positions if i < len(optimized) and optimized[i]["savepoint"]])
    
    for i, msg in enumerate(optimized):
        if savepoint_count >= 4:
            break
        
        temp_token_count += len(msg["content"])
        
        # 检查是否达到下一个阈值
        threshold_idx = savepoint_count - 1  # 已经设置的savepoint数（不包括系统消息）
        if threshold_idx < 0:
            threshold_idx = 0
        
        if threshold_idx < len(_token_thresholds):
            thresh = _token_thresholds[threshold_idx]
            if temp_token_count >= thresh and i not in _savepoint_positions:
                optimized[i]["savepoint"] = True
                _savepoint_positions.append(i)
                savepoint_count += 1
    
    # 更新_current_token_count为当前epoch的总token数
    _current_token_count = temp_token_count
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    # 可以根据billing调整阈值，但先保持简单
    pass
