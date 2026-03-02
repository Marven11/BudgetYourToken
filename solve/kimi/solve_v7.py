def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    candidates = [(i, len(msg["content"])) for i, msg in enumerate(history) if i > 0]
    candidates.sort(key=lambda x: x[1])
    
    history[0]["savepoint"] = True
    for idx, _ in candidates[:3]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
