from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    """优化历史记录，设置savepoint标志
    
    策略：在历史记录中设置最多4个savepoint，
    尝试在可能被缓存命中的位置设置检查点
    """
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    # 计算token数
    def token_count_msgs(msgs):
        return sum(len(m["content"]) for m in msgs)
    
    total_tokens = token_count_msgs(optimized)
    
    # 策略1：在系统消息后设置第一个savepoint
    # 策略2：在历史记录中均匀分布savepoint
    savepoint_count = 0
    max_savepoints = 4
    
    # 总是在系统消息后设置savepoint（如果存在且不是第一个）
    if len(optimized) > 1:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 在历史记录中寻找合适的位置设置剩余的savepoint
    # 尝试在消息边界和可能的稳定点设置
    for i in range(1, len(optimized) - 1):
        if savepoint_count >= max_savepoints:
            break
        
        # 避免在过短的消息后设置savepoint
        if len(optimized[i]["content"]) < 50:
            continue
        
        # 在用户消息后设置savepoint（假设用户消息更稳定）
        if optimized[i]["role"] == "user":
            optimized[i]["savepoint"] = True
            savepoint_count += 1
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    """监控消费情况，可用于调试"""
    pass
