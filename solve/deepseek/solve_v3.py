from typing import List
from challenge import Message, Billing


def optimizer(history: List[Message]) -> List[Message]:
    optimized = history.copy()
    
    # 重置所有savepoint为False
    for msg in optimized:
        msg["savepoint"] = False
    
    max_savepoints = 4
    savepoint_count = 0
    
    # 1. 系统消息总是设为savepoint
    if len(optimized) > 0:
        optimized[0]["savepoint"] = True
        savepoint_count += 1
    
    # 2. 在后40%部分设置savepoint，以保证清理后仍保留
    # 清理保留起始位置在40%-60%，所以后40%部分总是被保留
    if len(optimized) > 1:
        start_idx = int(len(optimized) * 0.6)  # 后40%的开始索引
        # 确保至少有一个位置
        if start_idx < len(optimized):
            # 在后40%部分选择3个位置（均匀分布）
            positions = []
            # 选择后40%部分的开始、中间、末尾
            if start_idx < len(optimized):
                positions.append(start_idx)  # 后40%的开始
            mid_idx = start_idx + (len(optimized) - 1 - start_idx) // 2
            if mid_idx < len(optimized) and mid_idx not in positions:
                positions.append(mid_idx)
            if len(optimized) - 1 not in positions:
                positions.append(len(optimized) - 1)  # 最后一个
            
            for idx in positions:
                if savepoint_count >= max_savepoints:
                    break
                if idx != 0:  # 避免重复系统消息
                    optimized[idx]["savepoint"] = True
                    savepoint_count += 1
    
    # 3. 如果还有空位且历史长度足够，可以在前部设置一个savepoint
    # 但前部的savepoint可能被清理掉，所以优先使用后部
    # 这里我们不再添加
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    pass
