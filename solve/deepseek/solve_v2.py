from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    max_savepoints = 4
    savepoint_count = 0
    
    # 1. 系统消息总是设为savepoint（如果存在）
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 2. 在历史记录中选择几个关键位置设置savepoint
    # 目标：覆盖可能的清理边界
    # 清理保留40%-60%，即丢弃前40%-60%，所以savepoint应该设置在历史记录的前部
    # 因为清理后，历史记录前缀是从中间某个位置开始，如果我们把savepoint设置在前部，清理后可能丢失
    # 实际上，清理后历史记录 = history[0:1] + history[保留部分:]
    # 系统消息总是保留，然后加上从中间开始的部分。
    # 所以清理后的历史记录前缀可能不包含之前的savepoint（除了系统消息）。
    # 因此，我们需要在可能被清理后保留的位置设置savepoint，即靠近末尾的位置。
    
    # 尝试在历史记录的末尾部分设置savepoint
    # 选择位置：从末尾往前数的几个位置
    positions = []
    if len(optimized) > 1:
        # 倒数第1个消息（最后一个）
        positions.append(len(optimized) - 1)
        # 倒数第5个消息（如果存在）
        if len(optimized) >= 5:
            positions.append(len(optimized) - 5)
        # 倒数第10个消息
        if len(optimized) >= 10:
            positions.append(len(optimized) - 10)
    
    for pos in positions:
        if savepoint_count >= max_savepoints:
            break
        if not optimized[pos]["savepoint"]:  # 避免重复设置
            optimized[pos]["savepoint"] = True
            savepoint_count += 1
    
    # 如果还有空位，在中间位置设置
    if savepoint_count < max_savepoints:
        mid_pos = len(optimized) // 2
        if mid_pos > 0 and mid_pos < len(optimized) and not optimized[mid_pos]["savepoint"]:
            optimized[mid_pos]["savepoint"] = True
            savepoint_count += 1
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
