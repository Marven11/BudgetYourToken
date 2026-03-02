def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    if len(history) <= 5:
        for msg in history:
            msg["savepoint"] = True
        return history
    
    history[0]["savepoint"] = True
    
    candidates = [(i, len(msg["content"])) for i, msg in enumerate(history[1:], start=1)]
    candidates.sort(key=lambda x: x[1])
    
    for idx, _ in candidates[:3]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
