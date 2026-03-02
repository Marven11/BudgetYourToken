from typing import List
from challenge import Message, Billing
import random

# 全局状态管理
class State:
    def __init__(self):
        self.position = 0.5  # 第二个savepoint的位置百分比
        self.best_position = 0.5
        self.best_score = -float('inf')
        self.scores = {}  # 位置 -> 分数历史
        self.last_billing = None
        self.last_len = 0
        self.cleaned = False
        self.adjust_counter = 0
        self.exploration_rate = 0.2
        
state = State()


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    # 重置savepoint
    for msg in optimized:
        msg["savepoint"] = False
    
    # 检测清理
    current_len = len(optimized)
    if state.last_len > 0 and current_len < state.last_len * 0.7:
        state.cleaned = True
    else:
        state.cleaned = False
    state.last_len = current_len
    
    # 总是设置系统消息为savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
    
    # 决定第二个savepoint的位置
    if len(optimized) > 1:
        # 探索或利用
        if random.random() < state.exploration_rate:
            # 探索：随机尝试新位置
            trial_pos = random.uniform(0.3, 0.9)
            idx = int(trial_pos * (len(optimized) - 1))
            idx = max(1, min(idx, len(optimized) - 1))
            optimized[idx]["savepoint"] = True
            state.position = trial_pos
        else:
            # 利用：使用当前最佳位置
            idx = int(state.best_position * (len(optimized) - 1))
            idx = max(1, min(idx, len(optimized) - 1))
            optimized[idx]["savepoint"] = True
            state.position = state.best_position
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    if state.last_billing is None:
        state.last_billing = billing
        return
    
    # 每50次调用评估一次
    state.adjust_counter += 1
    if state.adjust_counter < 50:
        return
    state.adjust_counter = 0
    
    # 计算增量
    delta_cached = billing["cached_input_tokens"] - state.last_billing["cached_input_tokens"]
    delta_input = billing["input_tokens"] - state.last_billing["input_tokens"]
    delta_write = billing["cache_write_tokens"] - state.last_billing["cache_write_tokens"]
    
    total_delta = delta_cached + delta_input
    if total_delta > 10000:  # 有足够数据
        # 计算分数：命中率加分，写入率减分
        hit_ratio = delta_cached / total_delta
        write_ratio = delta_write / total_delta
        
        # 分数公式：优先降低写入，其次提高命中
        score = hit_ratio * 0.1 - write_ratio * 1.0
        
        # 记录当前位置的分数
        if state.position not in state.scores:
            state.scores[state.position] = []
        state.scores[state.position].append(score)
        if len(state.scores[state.position]) > 5:
            state.scores[state.position].pop(0)
        
        # 计算平均分数
        avg_score = sum(state.scores[state.position]) / len(state.scores[state.position])
        
        # 更新最佳位置
        if avg_score > state.best_score:
            state.best_score = avg_score
            state.best_position = state.position
            # 成功时减少探索率
            state.exploration_rate = max(0.05, state.exploration_rate * 0.9)
        else:
            # 未改进时增加探索率
            state.exploration_rate = min(0.5, state.exploration_rate * 1.1)
        
        # 如果检测到清理，稍微调整位置
        if state.cleaned:
            # 清理后，历史从中间开始，最佳位置可能在0.5附近
            state.best_position = 0.5 + random.uniform(-0.1, 0.1)
            state.best_position = max(0.3, min(0.8, state.best_position))
    
    state.last_billing = billing.copy()
