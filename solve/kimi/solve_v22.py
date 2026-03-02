def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    candidates = [(i, len(msg["content"]), i) for i, msg in enumerate(history[1:], start=1)]
    candidates.sort(key=lambda x: (x[1], -x[2]))
    
    for idx, _, _ in candidates[:3]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
