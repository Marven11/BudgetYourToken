def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    if len(history) > 1:
        candidates = [(i, len(msg["content"])) for i, msg in enumerate(history[1:], start=1)]
        candidates.sort(key=lambda x: (x[1], -x[0]))
        for idx, _ in candidates[:1]:
            history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
