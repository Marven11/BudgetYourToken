def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    recent_indices = list(range(max(1, len(history) - 3), len(history)))
    for idx in recent_indices[:3]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
