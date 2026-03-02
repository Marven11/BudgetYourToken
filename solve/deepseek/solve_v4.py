from typing import List
from challenge import Message, Billing
import math

# 全局状态
_last_history_length = 0
_last_savepoint_index = 0
_optimal_prefix_length = 10000  # 目标前缀长度


def optimizer(history: List[Message]) -> List[Message]:
    global _last_history_length, _last_savepoint_index, _optimal_prefix_length
    
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 计算token累计
    prefix_tokens = 0
    target_tokens = _optimal_prefix_length
    savepoint_idx = -1
    
    # 寻找一个位置，使得前缀token数接近target_tokens
    for i, msg in enumerate(optimized):
        prefix_tokens += len(msg["content"])
        if prefix_tokens >= target_tokens:
            savepoint_idx = i
            break
    
    # 如果历史太短，就在最后一个消息设置savepoint
    if savepoint_idx == -1 and len(optimized) > 0:
        savepoint_idx = len(optimized) - 1
    
    # 确保不超过4个savepoint，我们只设置一个
    if savepoint_idx >= 0:
        optimized[savepoint_idx]["savepoint"] = True
        _last_savepoint_index = savepoint_idx
    
    _last_history_length = len(optimized)
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _optimal_prefix_length
    
    # 根据billing调整目标前缀长度
    # 如果cache_write_tokens较大，说明缓存未命中频繁，可能需要调整前缀长度
    # 这里我们简单调整：如果缓存写入过多，减少目标长度以增加稳定性
    # 如果缓存命中较多，增加目标长度以节省更多
    
    total_input = billing["cached_input_tokens"] + billing["input_tokens"]
    if total_input > 0:
        hit_ratio = billing["cached_input_tokens"] / total_input
        # 目标：hit_ratio在0.5左右？实际上我们希望尽可能高
        # 但太高可能意味着前缀太短，节省不多
        # 我们简单调整：如果hit_ratio>0.9，增加目标长度；如果<0.1，减少
        if hit_ratio > 0.9:
            _optimal_prefix_length = min(_optimal_prefix_length + 1000, 50000)
        elif hit_ratio < 0.1:
            _optimal_prefix_length = max(_optimal_prefix_length - 1000, 1000)
    
    # 也可以根据cache_write_tokens调整
    # 如果cache_write_tokens太大，说明写入频繁，减少目标长度
    write_ratio = billing["cache_write_tokens"] / max(1, total_input)
    if write_ratio > 0.1:  # 写入占比过高
        _optimal_prefix_length = max(_optimal_prefix_length - 500, 1000)
