from typing import List
from challenge import Message, Billing
import random

# 状态追踪
_last_len = 0
_cleaned = False
_best_position = 0  # 最佳savepoint位置（百分比）


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len, _cleaned, _best_position
    
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 检测清理
    current_len = len(optimized)
    if current_len < _last_len * 0.7:  # 长度显著减少，可能被清理
        _cleaned = True
    else:
        _cleaned = False
    _last_len = current_len
    
    # 选择savepoint位置
    # 策略：清理后，历史从中间开始，所以把savepoint设在清理后的起始位置附近
    # 但清理位置随机（40%-60%），我们取50%作为估计
    if _cleaned or _best_position == 0:
        # 初始或清理后，调整最佳位置
        # 我们希望savepoint在清理后历史的前部，以便前缀稳定
        # 清理后历史 = 系统消息 + 历史[保留起始:]
        # 所以savepoint应设在保留起始位置
        # 但清理位置随机，我们取中间值50%
        _best_position = 0.5
    
    # 计算具体索引
    target_idx = int(_best_position * len(optimized))
    # 确保在有效范围内
    target_idx = max(0, min(target_idx, len(optimized) - 1))
    
    # 设置savepoint
    optimized[target_idx]["savepoint"] = True
    
    # 可选：再设置一个在系统消息处（如果不同）
    if target_idx != 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _best_position
    
    # 根据性能调整最佳位置
    total_input = billing["cached_input_tokens"] + billing["input_tokens"]
    if total_input > 1000000:  # 有足够数据后调整
        hit_ratio = billing["cached_input_tokens"] / total_input
        write_ratio = billing["cache_write_tokens"] / max(1, total_input)
        
        # 如果命中率低且写入率高，说明savepoint不稳定
        if hit_ratio < 0.2 and write_ratio > 0.05:
            # 使savepoint更靠前（更稳定）
            _best_position = max(0.3, _best_position - 0.1)
        elif hit_ratio > 0.3 and write_ratio < 0.01:
            # 命中率不错且写入少，可以尝试更靠后以节省更多
            _best_position = min(0.8, _best_position + 0.1)
