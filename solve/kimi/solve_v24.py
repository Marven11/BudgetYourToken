def optimizer(history):
    for msg in history:
        msg["savepoint"] = False
    
    history[0]["savepoint"] = True
    
    n = len(history)
    if n > 10:
        history[n // 2]["savepoint"] = True
    
    return history


def billing_watcher(x):
    pass
