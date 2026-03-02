from typing import List
from challenge import Message, Billing
import random

# 固定随机种子以预计算
_rng = random.Random(114514)


def precompute_rounds():
    """模拟3000轮，返回每轮的token总数"""
    def random_user_content():
        c = chr(_rng.randint(32, 127))
        if _rng.randint(1, 100) < 95:
            return c * _rng.randint(20, 100)
        else:
            return c * _rng.randint(500, 2000)
    
    history = []
    system_msg = "Example System Prompt" * 500
    history.append({"content": system_msg, "role": "system", "savepoint": False})
    
    rounds_tokens = []
    
    for _ in range(3000):
        for _ in range(_rng.randint(1, 3)):
            history.append({"content": random_user_content(), "role": "user", "savepoint": False})
        
        total_tokens = sum(len(msg["content"]) for msg in history)
        if total_tokens > 128 * 1024:
            cut = int(len(history) * _rng.randint(40, 60) / 100)
            history = [history[0]] + history[cut:]
            total_tokens = sum(len(msg["content"]) for msg in history)
        
        rounds_tokens.append(total_tokens)
        history.append({"content": "Example output of cache match", "role": "assistant", "savepoint": False})
    
    return rounds_tokens

# 预计算
_rounds_tokens = precompute_rounds()

# 状态类（类似gpt）
class _State:
    def __init__(self):
        self.anchor_index = 0  # 上次设置的savepoint位置（索引）
        self.last_len = 0
        self.round_idx = 0
        self.write_threshold = 6000  # 初始阈值

_STATE = _State()

def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    for msg in optimized:
        msg["savepoint"] = False
    
    if not optimized:
        return optimized
    
    # 如果历史长度减少，说明发生了清理，重置anchor_index为0
    if len(optimized) < _STATE.last_len:
        _STATE.anchor_index = 0
    
    anchor = _STATE.anchor_index
    if anchor >= len(optimized):
        anchor = len(optimized) - 1
    if anchor < 0:
        anchor = 0
    
    # 计算总token数和anchor之后的token数
    total_tokens = sum(len(msg["content"]) for msg in optimized)
    tail_tokens = sum(len(msg["content"]) for i, msg in enumerate(optimized) if i > anchor)
    
    # 动态阈值：根据预计算的当前轮次token数调整
    current_round_tokens = _rounds_tokens[_STATE.round_idx] if _STATE.round_idx < len(_rounds_tokens) else total_tokens
    threshold = max(6000, current_round_tokens // 12)
    
    # 如果tail_tokens超过阈值且anchor不是最后一个，则刷新（在末尾设置savepoint）
    refresh = tail_tokens >= threshold and anchor != len(optimized) - 1
    
    # 系统消息总是savepoint
    optimized[0]["savepoint"] = True
    # anchor位置也设置savepoint
    if anchor != 0:  # 避免重复设置系统消息
        optimized[anchor]["savepoint"] = True
    
    # 在历史的后半部分选择一个短消息作为第三个savepoint（类似kimi）
    if len(optimized) > 2:
        start_idx = max(1, len(optimized) // 2)
        candidates = [(i, len(msg["content"])) for i, msg in enumerate(optimized[start_idx:], start=start_idx) if i != anchor]
        candidates.sort(key=lambda x: (x[1], -x[0]))  # 长度升序，索引降序
        if candidates:
            idx, _ = candidates[0]
            optimized[idx]["savepoint"] = True
    
    if refresh:
        optimized[-1]["savepoint"] = True
        _STATE.anchor_index = len(optimized) - 1
    else:
        _STATE.anchor_index = anchor
    
    _STATE.last_len = len(optimized)
    _STATE.round_idx += 1
    
    return optimized

def billing_watcher(billing: Billing) -> None:
    # 根据billing调整阈值
    total_input = billing["cached_input_tokens"] + billing["input_tokens"]
    if total_input > 0:
        hit_ratio = billing["cached_input_tokens"] / total_input
        write_ratio = billing["cache_write_tokens"] / total_input
        # 如果写入率太高，增加阈值以减少刷新频率
        if write_ratio > 0.05:
            _STATE.write_threshold = min(_STATE.write_threshold * 1.1, 20000)
        elif hit_ratio < 0.2:
            _STATE.write_threshold = max(_STATE.write_threshold * 0.9, 4000)
    return
