from typing import List
from challenge import Message, Billing
import random

# 状态
_secondary_pos_pct = 0.7  # 次要savepoint位置（百分比）
_best_score = -float('inf')
_last_billing = None
_adjust_counter = 0


def optimizer(history: List[Message]) -> List[Message]:
    global _secondary_pos_pct
    
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 1. 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 2. 在历史后部设置一个次要savepoint
    # 选择在70%位置附近（靠后，但不太靠末尾）
    if len(optimized) > 1:
        idx = int(_secondary_pos_pct * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))  # 确保不是系统消息
        optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _secondary_pos_pct, _best_score, _last_billing, _adjust_counter
    
    if _last_billing is None:
        _last_billing = billing
        return
    
    # 每100次调用调整一次
    _adjust_counter += 1
    if _adjust_counter < 100:
        return
    _adjust_counter = 0
    
    # 计算增量
    delta_cached = billing["cached_input_tokens"] - _last_billing["cached_input_tokens"]
    delta_input = billing["input_tokens"] - _last_billing["input_tokens"]
    delta_write = billing["cache_write_tokens"] - _last_billing["cache_write_tokens"]
    
    total_delta = delta_cached + delta_input
    if total_delta > 0:
        # 计算分数：缓存命中加分，写入减分
        score = (delta_cached * 0.9 - delta_write * 1.25) / total_delta
        
        # 记录最佳分数和位置
        if score > _best_score:
            _best_score = score
            # 如果分数提高，保持当前位置
        else:
            # 分数未提高，随机调整位置
            _secondary_pos_pct += random.uniform(-0.1, 0.1)
            _secondary_pos_pct = max(0.3, min(0.9, _secondary_pos_pct))
    
    _last_billing = billing.copy()
