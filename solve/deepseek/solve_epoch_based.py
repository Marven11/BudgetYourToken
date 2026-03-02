from typing import List
from challenge import Message, Billing

# 状态
_last_len = 0
_epoch = 0
_epoch_token_count = 0  # 当前epoch累计token
_thresholds = [15000, 30000, 45000, 60000]  # 每个epoch使用的token阈值
_used_thresholds_this_epoch = []  # 当前epoch已使用的阈值


def optimizer(history: List[Message]) -> List[Message]:
    global _last_len, _epoch, _epoch_token_count, _used_thresholds_this_epoch
    
    optimized = history.copy()
    
    for msg in optimized:
        msg["savepoint"] = False
    
    current_len = len(optimized)
    
    # 检测清理：如果长度减少超过30%，认为发生了清理，开始新epoch
    if _last_len > 0 and current_len < _last_len * 0.7:
        _epoch += 1
        _epoch_token_count = 0
        _used_thresholds_this_epoch = []
        # 新epoch：系统消息总是savepoint
        if len(optimized) > 0:
            optimized[0]["savepoint"] = True
    
    _last_len = current_len
    
    # 如果这是第一个epoch，系统消息还没设置，则设置
    if len(optimized) > 0 and not optimized[0]["savepoint"]:
        optimized[0]["savepoint"] = True
    
    # 计算当前epoch的token累计（从清理后开始）
    # 我们不知道清理的确切位置，所以只能近似：从历史开头累计token，但epoch_token_count是从上次清理后累计的
    # 实际上，每次optimizer调用时，历史可能已经增加了新消息，我们需要重新计算token累计
    # 我们遍历历史，模拟从清理后开始计数，但不知道清理位置，所以假设清理后历史就是当前历史（可能不准确）
    # 更准确的做法：记录epoch开始时的历史长度，然后只计算新增消息的token？但清理会丢弃消息，复杂。
    # 简化：每次检测到清理时重置，然后累计整个历史的token（因为清理后历史是从中间开始的，前面的消息被丢弃了，但整个历史就是清理后的历史）
    # 所以，在清理后，我们重置token计数，然后后续调用时，历史可能增加了新消息，我们累计所有token（因为历史就是清理后的历史加上新增）
    
    # 遍历历史，设置savepoint
    savepoint_count = 1 if len(optimized) > 0 and optimized[0]["savepoint"] else 0
    current_token_count = 0
    
    for i, msg in enumerate(optimized):
        current_token_count += len(msg["content"])
        # 跳过已经设置savepoint的消息（如系统消息）
        if optimized[i]["savepoint"]:
            continue
        
        # 检查是否达到下一个阈值
        if len(_used_thresholds_this_epoch) < len(_thresholds):
            next_threshold = _thresholds[len(_used_thresholds_this_epoch)]
            if current_token_count >= next_threshold and savepoint_count < 4:
                optimized[i]["savepoint"] = True
                savepoint_count += 1
                _used_thresholds_this_epoch.append(next_threshold)
    
    # 更新epoch_token_count为当前累计（用于下次判断）
    _epoch_token_count = current_token_count
    
    return optimized


def billing_watcher(billing: Billing) -> None:
    # 可以根据billing调整阈值，但先保持简单
    pass
