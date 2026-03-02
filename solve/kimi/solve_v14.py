def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 1:
        recent = list(range(max(1, len(history) - 10), len(history)))
        candidates = [(i, len(history[i]["content"]), i) for i in recent]
        candidates.sort(key=lambda x: (x[1], -x[2]))
        for idx, _, _ in candidates[:3]:
            history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
