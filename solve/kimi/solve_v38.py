def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 1:
        mid = len(history) // 2
        candidates = [(i, len(history[i]["content"])) for i in range(1, len(history)) if abs(i - mid) < 5]
        if candidates:
            candidates.sort(key=lambda x: x[1])
            history[candidates[0][0]]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
