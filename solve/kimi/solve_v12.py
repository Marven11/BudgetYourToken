def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 1:
        recent_start = max(1, len(history) - 20)
        candidates = [(i, len(history[i]["content"])) for i in range(recent_start, len(history))]
        candidates.sort(key=lambda x: x[1])
        for idx, _ in candidates[:3]:
            history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
