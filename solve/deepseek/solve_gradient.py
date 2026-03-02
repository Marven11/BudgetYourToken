from typing import List
from challenge import Message, Billing
import random

# 状态
_position = 0.5  # 第二个savepoint的位置（百分比）
_last_position = 0.5
_last_score = 0.0
_last_billing = None
_step = 0.1  # 调整步长


def optimizer(history: List[Message]) -> List[Message]:
    global _position
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    # 系统消息
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 第二个savepoint
    if len(optimized) > 1:
        idx = int(_position * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))
        optimized[idx]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _position, _last_position, _last_score, _last_billing, _step
    
    if _last_billing is None:
        _last_billing = billing
        return
    
    # 计算增量
    delta_cached = billing["cached_input_tokens"] - _last_billing["cached_input_tokens"]
    delta_input = billing["input_tokens"] - _last_billing["input_tokens"]
    delta_write = billing["cache_write_tokens"] - _last_billing["cache_write_tokens"]
    
    total_delta = delta_cached + delta_input
    if total_delta > 10000:
        # 计算分数：缓存命中加分，写入减分
        hit_ratio = delta_cached / total_delta
        write_ratio = delta_write / total_delta
        score = hit_ratio - write_ratio * 2  # 写入惩罚加倍
        
        # 与上一次分数比较
        if _last_billing is not None:
            if score > _last_score:
                # 分数提高，保持调整方向
                _last_position = _position
                _position += _step * random.choice([-1, 1])  # 随机方向探索
                _position = max(0.3, min(0.8, _position))
            else:
                # 分数下降，反向调整
                _step *= 0.9  # 减小步长
                _position = _last_position  # 回到上次位置
                # 尝试相反方向
                _position += _step * random.choice([-1, 1])
                _position = max(0.3, min(0.8, _position))
        
        _last_score = score
    
    _last_billing = billing.copy()
