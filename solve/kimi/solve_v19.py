def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    recent = [(i, len(history[i]["content"])) for i in range(max(1, len(history) - 5), len(history))]
    recent.sort(key=lambda x: x[1])
    
    for idx, _ in recent[:2]:
        history[idx]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
