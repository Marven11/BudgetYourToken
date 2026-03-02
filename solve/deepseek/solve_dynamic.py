from typing import List
from challenge import Message, Billing
import random

# 状态
_position = 0.5  # 主要savepoint位置（百分比）
_best_position = 0.5
_best_score = -float('inf')
_position_scores = {}  # 位置 -> 分数列表
_last_billing = None
_last_len = 0
_cleaned = False


def optimizer(history: List[Message]) -> List[Message]:
    global _position, _last_len, _cleaned
    
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
    
    savepoint_count = 0
    
    # 系统消息总是savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 主要savepoint
    if len(optimized) > 1 and savepoint_count < 4:
        idx = int(_position * (len(optimized) - 1))
        idx = max(1, min(idx, len(optimized) - 1))
        if not optimized[idx]["savepoint"]:
            optimized[idx]["savepoint"] = True
            savepoint_count += 1
    
    # 如果清理刚刚发生，在清理后的起始位置附近添加一个savepoint
    if _cleaned and len(optimized) > 2 and savepoint_count < 4:
        # 清理后历史从中间开始，所以在位置0.5附近设置
        idx2 = int(0.5 * (len(optimized) - 1))
        idx2 = max(1, min(idx2, len(optimized) - 1))
        if not optimized[idx2]["savepoint"]:
            optimized[idx2]["savepoint"] = True
            savepoint_count += 1
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _position, _best_position, _best_score, _position_scores, _last_billing, _cleaned
    
    if _last_billing is None:
        _last_billing = billing
        return
    
    # 计算增量
    delta_cached = billing["cached_input_tokens"] - _last_billing["cached_input_tokens"]
    delta_input = billing["input_tokens"] - _last_billing["input_tokens"]
    delta_write = billing["cache_write_tokens"] - _last_billing["cache_write_tokens"]
    
    total_delta = delta_cached + delta_input
    if total_delta > 10000:  # 有足够数据
        # 计算分数：缓存命中加分，写入减分
        hit_ratio = delta_cached / total_delta
        write_ratio = delta_write / total_delta
        score = hit_ratio * 10 - write_ratio * 20  # 写入惩罚更大
        
        # 记录当前位置的分数
        if _position not in _position_scores:
            _position_scores[_position] = []
        _position_scores[_position].append(score)
        if len(_position_scores[_position]) > 3:
            _position_scores[_position].pop(0)
        
        # 计算平均分数
        avg_score = sum(_position_scores[_position]) / len(_position_scores[_position])
        
        # 更新最佳位置
        if avg_score > _best_score:
            _best_score = avg_score
            _best_position = _position
        else:
            # 分数未提高，尝试随机调整位置
            if random.random() < 0.3:  # 30%概率调整
                _position += random.uniform(-0.1, 0.1)
                _position = max(0.3, min(0.8, _position))
        
        # 如果检测到清理，重置探索
        if _cleaned:
            # 清理后，最佳位置可能在0.5附近
            _position = 0.5 + random.uniform(-0.1, 0.1)
            _position = max(0.4, min(0.6, _position))
    
    _last_billing = billing.copy()
