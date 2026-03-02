_cache_positions = []

def optimizer(history):
    global _cache_positions
    
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    candidates = [(i, len(msg["content"])) for i, msg in enumerate(history[1:], start=1)]
    candidates.sort(key=lambda x: x[1])
    
    if len(history) > 10 and candidates:
        shortest_idx = candidates[0][0]
        if shortest_idx not in _cache_positions:
            _cache_positions.append(shortest_idx)
        if len(_cache_positions) > 3:
            _cache_positions = _cache_positions[-3:]
        for idx in _cache_positions:
            if idx < len(history):
                history[idx]["savepoint"] = True
    else:
        for idx, _ in candidates[:2]:
            history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
