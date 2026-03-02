from typing import List
from challenge import Message, Billing

# 全局状态
_last_len = 0
_token_counter = 0  # 从上次清理后累计的token数
_thresholds = [15000, 30000, 45000, 60000]  # token阈值
_used_thresholds = []  # 已经触发过的阈值


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len, _token_counter, _used_thresholds
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    current_len = len(optimized)
    
    # 检测清理：如果长度减少超过30%，认为发生了清理
    if _last_len > 0 and current_len < _last_len * 0.7:
        # 清理发生，重置token计数和已用阈值
        _token_counter = 0
        _used_thresholds = []
        # 同时，清理后历史从中间开始，系统消息总是保留
        # 我们在系统消息设置savepoint
        if len(optimized) > 0:
            optimized[0]["savepoint"] = True
    
    _last_len = current_len
    
    # 计算从清理后开始的累计token数
    # 注意：每次调用optimizer时，历史可能已经添加了新消息
    # 我们需要重新计算token累计，但只从清理后开始
    # 简化：我们遍历整个历史，模拟从清理后开始计数
    # 但实际上我们不知道清理的确切位置，所以用_token_counter近似
    
    # 遍历历史，在达到阈值时设置savepoint
    savepoint_count = 0
    current_token_count = 0
    
    # 系统消息总是savepoint（如果还没设置）
    if len(optimized) > 0 and not optimized[0]["savepoint"]:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    for i, msg in enumerate(optimized):
        current_token_count += len(msg["content"])
        # 检查是否达到下一个未使用的阈值
        for thresh in _thresholds:
            if thresh in _used_thresholds:
                continue
            if current_token_count >= thresh and savepoint_count < 4:
                optimized[i]["savepoint"] = True
                savepoint_count += 1
                _used_thresholds.append(thresh)
                break
        
        if savepoint_count >= 4:
            break
    
    # 更新_token_counter（用于下次检测清理）
    _token_counter = current_token_count
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
