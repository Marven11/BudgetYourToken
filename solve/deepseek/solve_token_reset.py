from typing import List
from challenge import Message, Billing

# 状态
_last_len = 0
_token_counter = 0  # 从上次清理后累计的token数
_thresholds = [20000, 40000, 60000, 80000]  # token阈值
_used_thresholds = []  # 已经使用过的阈值


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
    
    _last_len = current_len
    
    # 重新计算token累计，设置savepoint
    savepoint_count = 0
    current_token_count = 0
    
    # 总是设置系统消息为savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 遍历历史，在达到阈值时设置savepoint
    for i, msg in enumerate(optimized):
        current_token_count += len(msg["content"])
        # 检查是否达到下一个阈值
        for thresh in _thresholds:
            if thresh in _used_thresholds:
                continue  # 这个阈值已经用过了
            if current_token_count >= thresh and savepoint_count < 4:
                optimized[i]["savepoint"] = True
                savepoint_count += 1
                _used_thresholds.append(thresh)
                break
        
        if savepoint_count >= 4:
            break
    
    # 更新_token_counter为当前累计token数（用于下次检测清理时重置）
    _token_counter = current_token_count
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
