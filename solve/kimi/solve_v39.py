def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    candidates = [(i, len(msg["content"])) for i, msg in enumerate(history[1:], start=1)]
    candidates.sort(key=lambda x: (x[1], -x[0]))
    
    total = len(candidates)
    for idx, _ in candidates[:min(2, total)]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
