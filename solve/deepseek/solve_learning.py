from typing import List
from challenge import Message, Billing
import random

# 状态
_last_len = 0
_cleaned = False
_savepoint_positions = [0.2, 0.4, 0.6, 0.8]  # 初始位置


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len, _cleaned
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 检测清理
    current_len = len(optimized)
    if _last_len > 0 and current_len < _last_len * 0.7:
        _cleaned = True
    else:
        _cleaned = False
    _last_len = current_len
    
    # 设置savepoint
    savepoint_count = 0
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 在其他位置设置savepoint
    for pos_pct in _savepoint_positions:
        if savepoint_count >= 4:
            break
        idx = int(pos_pct * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _savepoint_positions, _cleaned
    
    # 简单调整策略：如果检测到清理，调整位置
    # 清理后历史从中间开始，所以savepoint应该设置在相对位置
    if _cleaned:
        # 清理后，历史变短，重新计算百分比位置
        # 清理丢弃了前40%-60%，所以剩下的历史从原历史的中间开始
        # 我们保持相对位置不变，但可能需要调整
        pass
    
    # 根据billing性能调整
    total = billing["cached_input_tokens"] + billing["input_tokens"]
    if total > 0:
        hit_rate = billing["cached_input_tokens"] / total
        write_rate = billing["cache_write_tokens"] / total
        
        # 如果写入率太高，减少savepoint数量或调整位置
        if write_rate > 0.05:
            # 随机调整一个位置
            idx = random.randint(0, len(_savepoint_positions)-1)
            _savepoint_positions[idx] += random.uniform(-0.1, 0.1)
            _savepoint_positions[idx] = max(0.1, min(0.9, _savepoint_positions[idx]))
