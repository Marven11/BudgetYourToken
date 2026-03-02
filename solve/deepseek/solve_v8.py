from typing import List
from challenge import Message, Billing
import math

# 状态
_current_position_pct = 0.5  # 初始在中间
_position_scores = {}  # 位置百分比 -> 分数
_last_billing = None
_last_hit_ratio = 0.0
_last_write_ratio = 0.0
_step_size = 0.1  # 调整步长
_exploration_chance = 0.1  # 探索新位置的概率


def optimizer(history: List[Message]) -> List[Message]:
    global _current_position_pct, _position_scores, _last_billing, _last_hit_ratio, _last_write_ratio
    
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 决定是否探索新位置
    import random
    if random.random() < _exploration_chance and len(history) > 10:
        # 探索：随机选择一个位置
        explore_pct = random.uniform(0.1, 0.9)
        idx = int(explore_pct * (len(optimized) - 1))
        idx = max(0, min(idx, len(optimized) - 1))
        optimized[idx]["savepoint"] = True
        # 记录探索位置
        _current_position_pct = explore_pct
    else:
        # 利用当前最佳位置
        idx = int(_current_position_pct * (len(optimized) - 1))
        idx = max(0, min(idx, len(optimized) - 1))
        optimized[idx]["savepoint"] = True
    
    # 系统消息也设置为savepoint（稳定）
    if idx != 0 and len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    global _current_position_pct, _position_scores, _last_billing, _last_hit_ratio, _last_write_ratio, _step_size
    
    if _last_billing is None:
        _last_billing = billing
        return
    
    # 计算增量
    delta_cached = billing["cached_input_tokens"] - _last_billing["cached_input_tokens"]
    delta_input = billing["input_tokens"] - _last_billing["input_tokens"]
    delta_write = billing["cache_write_tokens"] - _last_billing["cache_write_tokens"]
    
    total_delta_input = delta_cached + delta_input
    if total_delta_input > 0:
        hit_ratio = delta_cached / total_delta_input
        write_ratio = delta_write / max(1, total_delta_input)
        
        # 评估当前位置的表现
        score = hit_ratio * 10 - write_ratio * 5  # 命中加分，写入减分
        
        # 更新分数
        if _current_position_pct not in _position_scores:
            _position_scores[_current_position_pct] = []
        _position_scores[_current_position_pct].append(score)
        # 保留最近5个分数
        if len(_position_scores[_current_position_pct]) > 5:
            _position_scores[_current_position_pct].pop(0)
        
        # 计算平均分数
        avg_score = sum(_position_scores[_current_position_pct]) / len(_position_scores[_current_position_pct])
        
        # 调整位置：如果分数低，尝试移动
        # 简单策略：随机游走，但偏向高分方向
        import random
        if random.random() < 0.3:  # 30%概率调整
            # 随机选择一个方向
            direction = random.choice([-1, 1])
            new_pct = _current_position_pct + direction * _step_size
            new_pct = max(0.1, min(0.9, new_pct))
            
            # 如果新位置有历史分数且更好，则接受
            if new_pct in _position_scores and len(_position_scores[new_pct]) > 0:
                new_avg = sum(_position_scores[new_pct]) / len(_position_scores[new_pct])
                if new_avg > avg_score:
                    _current_position_pct = new_pct
            else:
                # 新位置，有一定概率接受
                if random.random() < 0.5:
                    _current_position_pct = new_pct
    
    _last_billing = billing.copy()
